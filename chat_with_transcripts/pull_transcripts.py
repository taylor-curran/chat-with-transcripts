import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import requests
from dotenv import load_dotenv


def fetch_transcripts(email: str):
    # Load the .env file
    load_dotenv()

    # Get the API key from the .env file
    api_key = os.getenv("FIREFLIES_API_KEY")

    # Check if the API key is successfully loaded
    if not api_key:
        raise ValueError("API key not found. Please check your .env file.")

    url = "https://api.fireflies.ai/graphql"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # GraphQL query to fetch transcripts with specified participants and meeting attendee details
    data_with_filter = {
        "query": """
        query Transcripts($participantEmail: String!, $limit: Int) {
          transcripts(participant_email: $participantEmail, limit: $limit) {
            id
            title
            participants
            dateString
            transcript_url
            meeting_attendees {
              displayName
              email
              phoneNumber
              name
            }
            sentences {
                index
                speaker_name
                speaker_id
                text
                raw_text
                start_time
                end_time
                ai_filters {
                    task
                    pricing
                    metric
                    question
                    date_and_time
                    text_cleanup
                    sentiment
                }
            }
          }
        }
        """,
        "variables": {
            "participantEmail": email,  # Currently only one email is used
            "limit": 1,  # Limit to 3 transcripts for testing
        },
    }

    response = requests.post(url, json=data_with_filter, headers=headers)
    response_json = response.json()
    if response_json.get("errors"):
        raise ValueError(f"Error fetching transcripts: {response_json['errors']}")
    return response_json["data"]


def transcript_to_document(transcript):
    """Convert a Fireflies transcript to a document for storage in a ChromaDB collection."""
    metadata = {
        "id": transcript["id"],
        "title": transcript["title"],
        "participants": ",".join(transcript["participants"]),
        "dateString": transcript["dateString"],
        "transcript_url": transcript["transcript_url"],
    }

    content = ""
    for sentence in transcript["sentences"]:
        content += sentence["speaker_name"] + ": " + sentence["text"] + "\n"

    return {"id": transcript["id"], "metadata": metadata, "content": content}


def store_embeddings_in_chroma(
    documents: list[dict],
    openai_api_key: str,
    chroma_db_path: str,
    embedding_model_name: str,
):
    """Store embeddings of news article titles and content in a ChromaDB collection."""
    chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key, model_name=embedding_model_name
    )
    collection = chroma_client.get_or_create_collection(
        "presale_calls", embedding_function=openai_ef
    )

    documents_content = [doc["content"] for doc in documents]
    documents_metadata = [doc["metadata"] for doc in documents]
    documents_ids = [doc["id"] for doc in documents]

    collection.add(
        documents=documents_content, metadatas=documents_metadata, ids=documents_ids
    )
    print("------------------- peek -------------------")
    print(collection.peek(1))
    print("------------------- count -------------------")
    print(collection.count())


if __name__ == "__main__":
    # Define participant emails to filter by (one at a time due to API constraint)
    participant_emails_to_filter = [
        # "taylor.curran@prefect.io",  # Taylor Curran
        "shane@prefect.io",  # Shane Nordstrand
        # "mitchell.bradley@prefect.io",  # Mitchell Bradley
        # "darren.pinder@prefect.io",  # Darren Pinder
        # "bianca.hoch@prefect.io",  # Bianca Hoch
        # "bionca.htun@prefect.io",  # Bionca Htun
        # "mihir.thatte@prefect.io",  # Mihir Thatte
    ]

    documents = []

    # Fetch and print filtered transcripts for each participant email
    for email in participant_emails_to_filter:
        print(f"Fetching transcripts for {email}...")
        payload = fetch_transcripts(email)
        for transcript in payload["transcripts"]:
            documents.append(transcript_to_document(transcript))

    # Store the fetched transcripts in a ChromaDB collection
    print("Storing transcripts in ChromaDB...")
    store_embeddings_in_chroma(
        documents=documents,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        chroma_db_path="presales_chromadb",
        embedding_model_name="text-embedding-3-small",
    )
