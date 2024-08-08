from collection import get_collection

collection = get_collection()

result = collection.query(
    query_texts=["Find me presales calls that mention architecture"],
    n_results=1,
    # where={"metadata_field": "is_equal_to_this"},
    # where_document={"$contains":"search_string"}
)
breakpoint()
...
