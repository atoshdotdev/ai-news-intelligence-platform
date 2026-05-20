import hashlib
from collections.abc import AsyncGenerator
from types import SimpleNamespace
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
    urlunparse,
)

from ainews.core.config.settings import settings
from ainews.core.db.models import Article
from ainews.core.repositories.article import ArticleRepository
from ainews.core.repositories.source import SourceRepository
from ainews.core.utils.logging import logger
from crawl4ai import (
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    CrawlResult,
)
from crawl4ai.docker_client import Crawl4aiDockerClient
from sqlalchemy.ext.asyncio import AsyncSession


class CrawlerService:
    def __init__(self, session: AsyncSession):
        self.article_repo = ArticleRepository(session)
        self.source_repo = SourceRepository(session)
        self.base_url = settings.web_crawler_url
        self.BATCH_SIZE = 5

    def canonicalize_url(self, url: str) -> str:
        """
        Normalize URLs so duplicate articles hash the same.

        Removes:
        - tracking params (utm_*, fbclid, gclid, etc.)
        - fragments
        - trailing slashes

        Preserves:
        - meaningful query params
        """

        parsed = urlparse(url.strip())

        filtered_query = [
            (k, v)
            for k, v in parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )
            if not (
                k.startswith("utm_")
                or k
                in {
                    "ref",
                    "fbclid",
                    "gclid",
                    "igshid",
                    "mc_cid",
                    "mc_eid",
                }
            )
        ]

        canonical = urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip("/"),
                "",
                urlencode(sorted(filtered_query)),
                "",
            )
        )

        return canonical

    def is_likely_article(self, url: str) -> bool:
        path = urlparse(url).path
        return len(path.split("/")) > 3

    async def run(self):
        """
        Executes a complete crawling + ingestion pipeline for all active sources.
        """

        # sources = await self.source_repo.get_active_sources()
        sources = [
            SimpleNamespace(
                id=1,
                name="BBC Tech",
                url="https://edition.cnn.com/politics",
                blacklist_entries=["/video", "/live", "/audio", "/videos"],
                selector=None,
            )
        ]

        if not sources:
            logger.info("No active sources found.")
            return

        browser_config = BrowserConfig(
            headless=True,
        )

        async with Crawl4aiDockerClient(
            base_url=self.base_url,
            verbose=True,
        ) as client:
            for source in sources:
                logger.info(f"Starting crawl cycle for source: {source.name}")

                try:
                    index_crawler_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        excluded_tags=[
                            "script",
                            "style",
                            "nav",
                            "footer",
                            "header",
                            "aside",
                            "head",
                        ],
                        exclude_external_links=True,
                        exclude_social_media_links=True,
                    )

                    index_result = await client.crawl(
                        urls=[source.url],
                        browser_config=browser_config,
                        crawler_config=index_crawler_config,
                    )

                    if not index_result:
                        logger.warning(
                            f"No crawl response returned for source: {source.name}"
                        )
                        continue

                    if not isinstance(index_result, CrawlResult):
                        logger.warning(
                            f"Unexpected crawl result type for {source.name}"
                        )
                        continue

                    if not index_result.success:
                        logger.warning(
                            f"Failed crawling source index page for "
                            f"{source.name}: "
                            f"{index_result.error_message}"
                        )
                        continue

                    internal_links = index_result.links.get(
                        "internal",
                        [],
                    )

                    raw_links = [
                        link["href"]
                        for link in internal_links
                        if isinstance(link, dict)
                        and link.get("href")
                        and self.is_likely_article(link["href"])
                    ]

                    logger.info(raw_links)

                    url_candidates = {}
                    blacklist = [
                        entry.strip().lower() for entry in source.blacklist_entries
                    ]

                    for raw_url in raw_links:
                        raw_url = raw_url.strip()

                        if not raw_url:
                            continue

                        canonical_url = self.canonicalize_url(raw_url)

                        if blacklist:
                            if any(fragment in canonical_url for fragment in blacklist):
                                logger.info(
                                    f"Excluding blacklisted URL: {canonical_url}"
                                )
                                continue

                        url_hash = hashlib.sha256(canonical_url.encode()).hexdigest()

                        if url_hash not in url_candidates:
                            url_candidates[url_hash] = {
                                "url": canonical_url,
                                "url_hash": url_hash,
                            }

                    if not url_candidates:
                        logger.info(
                            f"No valid URL candidates found for source: {source.name}"
                        )
                        continue

                    all_hashes = list(url_candidates.keys())

                    existing_hashes = await self.article_repo.get_existing_hashes(
                        all_hashes
                    )

                    filtered_links = [
                        link_data
                        for url_hash, link_data in url_candidates.items()
                        if url_hash not in existing_hashes
                    ]

                    if not filtered_links:
                        logger.info(f"No new articles found for source: {source.name}")
                        continue

                    url_to_hash = {
                        link_data["url"]: link_data["url_hash"]
                        for link_data in filtered_links
                    }

                    article_urls = [link_data["url"] for link_data in filtered_links]

                    article_crawler_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        exclude_external_links=True,
                        exclude_internal_links=True,
                        exclude_social_media_links=True,
                        exclude_all_images=True,
                        only_text=True,
                        target_elements=[
                            source.selector if source.selector else "main"
                        ],
                        excluded_tags=[
                            "script",
                            "style",
                            "nav",
                            "footer",
                            "header",
                            "aside",
                            "form",
                        ],
                        word_count_threshold=50,
                    )

                    all_results = []

                    for i in range(0, len(article_urls), self.BATCH_SIZE):
                        batch = article_urls[i : i + self.BATCH_SIZE]

                        try:
                            batch_results = await client.crawl(
                                urls=batch,
                                browser_config=browser_config,
                                crawler_config=article_crawler_config,
                            )

                            if isinstance(batch_results, CrawlResult):
                                all_results.append(batch_results)

                            elif isinstance(batch_results, list):
                                all_results.extend(batch_results)

                            elif isinstance(batch_results, AsyncGenerator):
                                all_results.extend([r async for r in batch_results])

                            else:
                                logger.warning("Unknown crawl result type in batch")
                                continue

                        except Exception as e:
                            logger.exception(f"Batch crawl failed: {str(e)}")
                            continue

                    article_results = [
                        r for r in all_results if isinstance(r, CrawlResult)
                    ]

                    if not article_results:
                        logger.warning(
                            f"No article crawl results returned for {source.name}"
                        )
                        continue

                    articles_to_create = []

                    for article_result in article_results:
                        try:
                            if not article_result.success:
                                logger.warning(
                                    f"Failed article crawl: "
                                    f"{article_result.url} "
                                    f"-> {article_result.error_message}"
                                )
                                continue

                            canonical_url = self.canonicalize_url(article_result.url)
                            url_hash = url_to_hash.get(article_result.url)

                            if not url_hash:
                                url_hash = hashlib.sha256(
                                    canonical_url.encode()
                                ).hexdigest()

                            title = (
                                article_result.metadata.get("title")
                                if article_result.metadata
                                else None
                            )

                            title = title.strip() if title else "Untitled"

                            markdown_content = (article_result.markdown or "").strip()

                            meta_description = (
                                article_result.metadata.get("description")
                                if article_result.metadata
                                else None
                            )

                            extracted_content = (
                                markdown_content or meta_description or ""
                            ).strip()

                            image_url = None

                            if article_result.metadata:
                                image_url = (
                                    article_result.metadata.get("og:image")
                                    or article_result.metadata.get(
                                        "og:image:secure_url"
                                    )
                                    or article_result.metadata.get("image")
                                )

                            if not extracted_content:
                                logger.warning(
                                    f"Skipping empty article: {canonical_url}"
                                )
                                continue

                            article = Article(
                                url=canonical_url,
                                url_hash=url_hash,
                                title=title,
                                content=extracted_content,
                                source_id=source.id,
                                image_url=image_url,
                            )

                            articles_to_create.append(article)

                            logger.info(f"Prepared article: {title}")

                        except Exception as e:
                            logger.exception(
                                f"Error processing article "
                                f"{article_result.url}: {str(e)}"
                            )

                    if not articles_to_create:
                        logger.info(f"No valid articles extracted for {source.name}")
                        continue

                    await self.article_repo.create_many(articles_to_create)

                    logger.info(
                        f"Inserted {len(articles_to_create)} "
                        f"articles for source: {source.name}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error during crawler pipeline for source {source.name}: {e}",
                        exc_info=True,
                    )
