import controlflow as cf
from tools import query_presales_vector_database


@cf.flow
def interrogate_transcripts():
    user_input_task = cf.Task(
        "Ask the user what their question is today. After the user provides a question, use presales transcripts to answer the user's question about current trends.",
        result_type=str,
        user_access=True,
        tools=[query_presales_vector_database],
    )

    result = user_input_task.run()
    print(result)


if __name__ == "__main__":
    interrogate_transcripts()
