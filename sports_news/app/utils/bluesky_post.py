from atproto_client.models.app.bsky.embed.video import Main
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

def is_youtube_url(url):
    """
    Checks if the given URL is a YouTube video and extracts the video ID.
    
    Args:
        url (str): The URL to check.
    
    Returns:
        str or None: Returns the YouTube video ID if it's a valid YouTube URL, otherwise None.
    """
    youtube_regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([\w-]+)"
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

def upload_content(text: str, title: str, link: str, description: str = "", img_url: str = None):
    """
    Uploads a post to Bluesky with an external embed, supporting both articles and YouTube videos.
    
    :param text: The text content of the post.
    :param title: The title for the embedded content.
    :param link: The URL of the external content.
    :param description: Description for the external content.
    :param img_url: The URL of the image to be used as a thumbnail (only for non-YouTube embeds).
    """
    _, hashtags = extract_hashtags(text)
    text_builder = build_text(text, hashtags)
    
    # Check if it's a YouTube video
    video_id = is_youtube_url(link)

    if video_id:
        # For YouTube videos, generate a thumbnail URL
        youtube_thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        
        # Download the thumbnail
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(youtube_thumb_url, headers=headers, timeout=10)
            if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
                blob = client.upload_blob(response.content)
        except Exception as e:
            print(f"Error downloading YouTube thumbnail: {e}")
            blob = None
            
        embed_external = External(
            title=title,
            description=description,
            uri=f"https://www.youtube.com/watch?v={video_id}",
            thumb=blob.blob if blob else None
        )
    else:
        # Regular external embed with an optional image
        blob = None
        if img_url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(img_url, headers=headers, timeout=10)
                if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
                    blob = client.upload_blob(response.content)
            except Exception as e:
                print(f"Error downloading image: {e}")

        embed_external = External(
            title=title,
            description=description,
            uri=link,
            thumb=blob.blob if blob else None
        )

    embed = Main(external=embed_external)

    try:
        embed_data = embed.model_dump(by_alias=True)
    except AttributeError:
        embed_data = embed.dict(by_alias=True)

    client.send_post(text=text_builder, embed=embed_data)