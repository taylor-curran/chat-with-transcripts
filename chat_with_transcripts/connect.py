import requests
from dotenv import load_dotenv
import os


def fetch_users():
    # Load the .env file
    load_dotenv()

    # Get the API key from the .env file
    api_key = os.getenv("FIREFLIES_API_KEY")

    # Check if the API key is successfully loaded
    if not api_key:
        raise ValueError("API key not found. Please check your .env file.")

    url = "https://api.fireflies.ai/graphql"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"query": "{ users { name user_id } }"}

    response = requests.post(url, json=data, headers=headers)
    return response.json()


if __name__ == "__main__":
    users_data = fetch_users()
    print(users_data)
