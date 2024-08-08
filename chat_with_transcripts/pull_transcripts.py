import os

import requests
from collection import get_collection
from dotenv import load_dotenv


def fetch_transcripts(email: str, limit: int = 50):
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
            "limit": limit,  # Limit to 3 transcripts for testing
        },
    }

    response = requests.post(url, json=data_with_filter, headers=headers)
    response_json = response.json()
    if response_json.get("errors"):
        raise ValueError(f"Error fetching transcripts: {response_json['errors']}")
    return response_json["data"]


def transcript_to_documents(transcript) -> list[dict]:
    """Convert a Fireflies transcript to a document for storage in a ChromaDB collection."""

    internal_only = all(
        [email.endswith("@prefect.io") for email in transcript["participants"]]
    )

    metadata = {
        "id": transcript["id"],
        "title": transcript["title"],
        "participants": ",".join(transcript["participants"]),
        "dateString": transcript["dateString"],
        "transcript_url": transcript["transcript_url"],
        "is_internal": internal_only,
    }

    # 8191 is the maximum token limit for OpenAI API
    # tokens are about 4 words
    embedding_character_limit = 8191 * 2

    prefect_speakers = [
        "Darren Pinder",
        "Taylor Curran",
        "Bianca Hoch",
        "Bionca Htun",
        "Mihir Thatte",
        "Mitchell Bradley",
        "Shane Nordstrand",
        "Emil Christensen",
    ]

    content = ""
    for sentence in transcript["sentences"] or []:
        speaker = sentence["speaker_name"] or "UNKNOWN SPEAKER:"
        if speaker in prefect_speakers:
            speaker += " (Prefect)"
        content += speaker + ": " + sentence["text"] + "\n"
    # Split the string into chunks of the same size
    content_chunks = [
        content[i : i + embedding_character_limit]
        for i in range(0, len(content), embedding_character_limit)
    ]
    documents = []
    for i, content_chunk in enumerate(content_chunks):
        documents.append(
            {
                "id": f"{transcript["id"]}-chunk-{i}",
                "metadata": metadata,
                "content": content_chunk,
            }
        )

    return documents


def store_embeddings_in_chroma(
    documents: list[dict],
):
    """Store embeddings of news article titles and content in a ChromaDB collection."""
    collection = get_collection()

    seen_ids = set()
    documents_content = []
    documents_metadata = []
    documents_ids = []
    for doc in documents:
        if doc["id"] in seen_ids:
            print(f"Already saw document with id {doc['id']}. Skipping.")
            continue
        documents_content.append(doc["content"])
        documents_ids.append(doc["id"])
        documents_metadata.append(doc["metadata"])
        seen_ids.add(doc["id"])

    collection.add(
        documents=documents_content, metadatas=documents_metadata, ids=documents_ids
    )
    print("------------------- count -------------------")
    print(collection.count())


if __name__ == "__main__":
    # Define participant emails to filter by (one at a time due to API constraint)
    participant_emails_to_filter = [
        # "taylor.curran@prefect.io",  # Taylor Curran
        "shane@prefect.io",  # Shane Nordstrand
        "mitchell.bradley@prefect.io",  # Mitchell Bradley
        # "darren.pinder@prefect.io",  # Darren Pinder
        # "bianca.hoch@prefect.io",  # Bianca Hoch
        "bionca@prefect.io",  # Bionca Htun
        # "mihir.thatte@prefect.io",  # Mihir Thatte
    ]

    documents = []

    # Fetch and print filtered transcripts for each participant email
    for email in participant_emails_to_filter:
        print(f"Fetching transcripts for {email}...")
        payload = fetch_transcripts(email)
        print(f"Found {len(payload['transcripts'])} transcripts. Processing...")
        for transcript in payload["transcripts"]:
            documents.extend(transcript_to_documents(transcript))

    # Store the fetched transcripts in a ChromaDB collection
    print(f"Storing {len(documents)} transcripts in ChromaDB...")
    store_embeddings_in_chroma(
        documents=documents,
    )
