import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="workflow_chunks"
)

def add_chunks(chunks):
    for idx, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"chunk_{idx}"]
        )

def search_chunks(query: str, n_results: int = 3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results

def get_context(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=1
    )

    return results["documents"][0][0]