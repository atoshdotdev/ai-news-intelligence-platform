from gliner import GLiNER

MODEL_NAME = "EmergentMethods/gliner_medium_news-v2.1"


def extract_entities(
    model,
    text: str,
    labels: list[str],
    threshold: float = 0.5,
):
    return model.predict_entities(
        text,
        labels,
        threshold=threshold,
    )


def deduplicate_entities(entities):
    seen = {}

    for entity in entities:
        key = (entity["text"].lower(), entity["label"])

        if key not in seen:
            seen[key] = entity

    return list(seen.values())


def main():
    print("Loading GLiNER model...")

    model = GLiNER.from_pretrained(MODEL_NAME, local_files_only=True)

    article = """
    Iran’s hardliners warn of a ‘coup’ as US truce comes under pressure | CNN
Hardline factions in Iran believe that instead of avenging the late supreme leader’s killing, Iranian officials have surrendered by signing an agreement with the US.
    """

    labels = [
        "person",
        "organization",
        "location",
        "country",
        "government",
        "political party",
        "event",
        "date",
        "product",
    ]

    entities = model.predict_entities(article, labels)

    entities = deduplicate_entities(entities)

    print("\nEntities found:\n")

    for entity in entities:
        print(f"{entity['text']} => {entity['label']} (score: {entity['score']:.3f})")


if __name__ == "__main__":
    main()
