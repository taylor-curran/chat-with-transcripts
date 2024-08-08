from collection import get_collection


def query_presales_vector_database(query: str, n_results: int = 20):
    """
    Query vector store for presales call transcripts to answer questions about presales calls.

    Args:
        query: str - The query to search for in the vector store.
        n_results: int - The number of results to return.

    Returns:
        Documents and metadata representing chunks of presales call transcripts that match the query.
    """
    collection = get_collection()
    return collection.query(query_texts=[query], n_results=n_results)
