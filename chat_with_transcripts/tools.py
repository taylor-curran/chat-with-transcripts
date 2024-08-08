from collection import get_collection


def query_presales_vector_database(
    query: str, n_results: int = 20, exclude_internal_calls: bool = True
):
    """
    Query vector store for presales call transcripts to answer questions about presales calls.

    Args:
        query: str - The query to search for in the vector store.
        n_results: int - The number of results to return.
        exclude_internal_calls: bool - Whether to exclude internal calls from the results.

    Returns:
        Documents and metadata representing chunks of presales call transcripts that match the query.
    """
    collection = get_collection()
    where = {"is_internal": False} if exclude_internal_calls else None
    return collection.query(query_texts=[query], n_results=n_results, where=where)
