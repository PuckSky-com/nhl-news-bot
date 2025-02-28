from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

api_token = os.getenv('API_TOKEN')
model = "llama3.1-70b"

client = OpenAI(
    api_key=api_token,
    base_url="https://api.llama-api.com"
)

def send_request(title: str, subtitle: str = "", body: str = ""):
    # Construct the prompt with the desired instructions.
    prompt_content = (
        f"Title: {title}\n"
        f"Subtitle: {subtitle}\n"
        "Provide an engaging 200-character summary of the article for social media. "
        "The summary should clearly explain the news or topic in an engaging way, and must not include extra placeholders or quotations."
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": prompt_content,
                }
            ],
            model=model,
            stream=False
        )
        return chat_completion.choices[0].message.content
    except Exception:
        print(f"An Error occurred in the API call")
        return None

def main():
    # Test data for the request.
    title = "Hockey Showdown: Team A vs. Team B Thrills Fans"
    subtitle = "A dramatic turnaround in a high-stakes game"
    
    try:
        chat_resp = send_request(title, subtitle)
        print("Generated Summary:")
        print(chat_resp)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

