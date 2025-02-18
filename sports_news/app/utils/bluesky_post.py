from atproto_client.models.app.bsky.embed.external import External, Main
from dotenv import load_dotenv
from atproto import Client
import requests
import os

load_dotenv()

pds_host = os.getenv('PDS_HOST')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

client = Client(pds_host)
client.login(username, password)

def upload_content(text: str, title: str, link: str, description: str = "", img_url: str = None):
    """
    Uploads a post to Bluesky with an external embed.
    The thumbnail (thumb) is set to None in this version.
    
    :param text: The text content of the post.
    :param title: The title for the embedded external content.
    :param link: The URL of the external article.
    :param image_url: (Ignored) The URL of the image to be used as a thumbnail.
    """
    image_data = requests.get(img_url).content if img_url else None

    blob = client.upload_blob(image_data) if image_data else None

    embed_external = External(
        title=title,
        description=description,
        uri=link,
        thumb=blob.blob if blob else None
    )
    embed = Main(external=embed_external)
    
    # Use by_alias=True to output keys in the expected camelCase format
    client.send_post(text=text, embed=embed.dict(by_alias=True))
