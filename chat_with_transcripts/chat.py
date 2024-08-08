import controlflow as cf
from tools import query_presales_vector_database


@cf.flow
def interrogate_transcripts():
    user_input_task = cf.Task(
        """
        Ask Prefect's VP of Marketing what their question is today. 
        After the user provides a question, 
        use presales transcripts to answer the user's question about
        trends in how customers understand and evaluate Prefect.
        """,
        result_type=str,
        user_access=True,
        tools=[query_presales_vector_database],
    )

    user_input_task.run()


if __name__ == "__main__":
    interrogate_transcripts()


# Good responses
# What tools were customers using before considering Prefect?
# What are the most common concerns customers have about adopting Prefect?
