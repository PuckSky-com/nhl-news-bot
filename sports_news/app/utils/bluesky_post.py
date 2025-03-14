from atproto_client.models.app.bsky.embed.external import External, Main
from dotenv import load_dotenv
from atproto import Client, client_utils
import requests
import os
import re

load_dotenv()

pds_host = os.getenv('PDS_HOST')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

client = Client(pds_host)
client.login(username, password)

def extract_hashtags(content):
    """
    Extracts hashtags from post content and returns the content and an array of hashtags
    
    Args:
        content (str): The post content that may contain hashtags
        
    Returns:
        tuple: A tuple containing (original_content, hashtags_list)
    """
    # Initialize an empty list to store hashtags
    hashtags = []
    
    # Use regex to find all hashtags in the content
    # This looks for # followed by word characters (letters, numbers, underscore)
    # until it hits a space or end of string
    hashtag_pattern = r'#(\w+)'
    
    # Find all matches in the content
    matches = re.findall(hashtag_pattern, content)
    
    # Add all found hashtags to the list
    hashtags = matches
    
    # Return a tuple with the original content and the hashtags list
    return content, hashtags

def build_text(content: str, tags: list):
    """
    Build rich text with content and hashtags using TextBuilder
    
    Args:
        content (str): The main text content
        tags (list): List of hashtags (without the # symbol)
        
    Returns:
        TextBuilder: A TextBuilder instance with the content and tags
    """
    builder = client_utils.TextBuilder()
    
    # Remove existing hashtags from content since we'll add them properly later
    clean_content = re.sub(r'#\w+', '', content).strip()
    
    # Add the clean content
    builder.text(clean_content)
    
    # Only add a space if there are tags and the content doesn't end with a space
    if tags and not clean_content.endswith(' '):
        builder.text(' ')
    
    # Add each tag
    for i, tag in enumerate(tags):
        builder.tag(f"#{tag}", tag)  # Display as #tag, link to tag
        
        # Add space between tags except after the last one
        if i < len(tags) - 1:
            builder.text(" ")
    
    return builder

def upload_content(text: str, title: str, link: str, description: str = "", img_url: str = None):
    """
    Uploads a post to Bluesky with an external embed.
    
    :param text: The text content of the post.
    :param title: The title for the embedded external content.
    :param link: The URL of the external article.
    :param description: Description for the external content.
    :param img_url: The URL of the image to be used as a thumbnail.
    """
    # Extract hashtags from the original text
    _, hashtags = extract_hashtags(text)
    
    # Build rich text with proper tag formatting
    text_builder = build_text(text, hashtags)

    blob = None
    if img_url:
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(img_url, headers=headers, timeout=10)
            
            # Check if the request was successful and is an image
            if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
                blob = client.upload_blob(response.content)
            else:
                print(f"Warning: Could not download image or not an image type: {response.headers.get('Content-Type')}")
        except Exception as e:
            print(f"Error downloading image: {e}")

    embed_external = External(
        title=title,
        description=description,
        uri=link,
        thumb=blob.blob if blob else None
    )
    embed = Main(external=embed_external)
    
    # Fix the deprecated dict method to use model_dump
    try:
        # For newer versions of Pydantic (v2)
        embed_data = embed.model_dump(by_alias=True)
    except AttributeError:
        # Fallback for older versions
        embed_data = embed.dict(by_alias=True)
    
    client.send_post(text=text_builder, embed=embed_data)


if __name__=='__main__':
    post = "Check out this hockey game! #NHL #Sports #HockeyFans"
    content, hashtags = extract_hashtags(post)

    print(content)  # "Check out this hockey game! #NHL #Sports #HockeyFans"
    print(hashtags)  # ['NHL', 'Sports', 'HockeyFans']
    
    # Test upload with the sample post
    upload_content(
        text=post,
        title="Hockey Game Highlights",
        link="https://media.d3.nhle.com/image/private/t_ratio16_9-size20/f_png/v1741960706/prd/e0zpd6uuvvxqaw4lwalz.png",
        description="Exciting hockey game highlights",
        img_url="https://media.d3.nhle.com/image/private/t_ratio16_9-size20/f_png/v1741960706/prd/e0zpd6uuvvxqaw4lwalz.png"  # Replace with actual image URL or remove
    )