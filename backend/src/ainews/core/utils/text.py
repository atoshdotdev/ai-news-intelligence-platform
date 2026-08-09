from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3", local_files_only=True)


article = """
President Donald Trump, center, hosts a Cabinet meeting at Camp David on July 31, 2026.
President Donald Trump is not, historically, a Camp David guy. 
The wood-wrapped rooms of the Laurel Lodge are not his happy place. His predecessors have chosen the retreat as an escape from cameras and formality; Trump rarely objects to having his picture taken or an extra chandelier or two. 

"""


def split_article(text: str, chunk_size: int = 512, chunk_overlap: int = 50):
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_text(text)


chunks = split_article(article)


print(f"Number of chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks):
    token_count = len(tokenizer.encode(chunk, add_special_tokens=False))

    print("=" * 80)
    print(f"CHUNK {i + 1} ({token_count} tokens)")
    print("=" * 80)
    print(chunk)
    print()
