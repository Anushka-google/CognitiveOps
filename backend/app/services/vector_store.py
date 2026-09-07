import chromadb
import uuid


def get_collection():

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    collection = client.get_or_create_collection(
        name="workflow_chunks"
    )

    return collection


def add_chunks(
    chunks,
    metadatas=None
):

    collection = get_collection()

    for index, chunk in enumerate(chunks):

        metadata = None

        if metadatas:

            metadata = metadatas[index]

        collection.add(

            documents=[
                chunk
            ],

            ids=[
                str(
                    uuid.uuid4()
                )
            ],

            metadatas=(
                [metadata]
                if metadata
                else None
            )
        )


def search_chunks(
    query: str,
    n_results: int = 3
):

    collection = get_collection()

    results = collection.query(

        query_texts=[
            query
        ],

        n_results=n_results
    )

    return results


def get_context(
    query: str
):

    collection = get_collection()

    results = collection.query(

        query_texts=[
            query
        ],

        n_results=1
    )

    return results[
        "documents"
    ][0][0]