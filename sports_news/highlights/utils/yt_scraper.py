from highlights.models import Video
import requests
import time
import re

class YouTubeScraper:

    def __init__(self, api_key: str, *, channel_name: str = None, channel_id: str = None):
        if not api_key:
            raise ValueError("API key is required")
            
        if not channel_name and not channel_id:
            raise ValueError("Either channel_name or channel_id must be provided")
            
        self.api_key = api_key
        self.channel_name = channel_name
         
        if channel_id:
            self.channel_id = channel_id
        else:
            self.channel_id = self._get_channel_id()
            if not self.channel_id:
                raise ValueError(f"Could not find channel ID for channel name: {channel_name}")
            
    @staticmethod
    def send_api_req(url, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=10)  # Add a 10-second timeout
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff (2, 4, 8 sec)
                else:
                    raise e
    
    def _get_channel_id(self):
        try:
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={self.channel_name}&key={self.api_key}"
            data = self.send_api_req(url)
            
            if "items" in data and data["items"]:
                channel_id = data["items"][0]["snippet"]["channelId"]
                return channel_id
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Failed to parse API response: {e}")
            return None
        
    def get_full_video_description(self, video_id):
        """Fetch the full description for a specific video."""
        try:
            url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={self.api_key}"
            data = self.send_api_req(url)
            
            if "items" in data and data["items"]:
                description = data["items"][0]["snippet"]["description"]
                return re.split(r'-{6,}', description)[0].strip()

            return ""
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            print(f"Error fetching full video description: {e}")
            return ""
        
    def get_latest_video(self, max_results=5, video_duration=None):
        """Fetch the latest video(s) from the channel."""
        try:
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={self.channel_id}&maxResults={max_results}&order=date&type=video"
            
            if video_duration:
                url += f"&videoDuration={video_duration}"
                
            url += f"&key={self.api_key}"
            
            data = self.send_api_req(url)

            titles = []
            count = 0
            
            if "items" in data and data["items"]:
                for item in data["items"]:
                    title = item["snippet"]["title"]
                    if title.startswith("NHL Highlights"):
                        video_id = item["id"]["videoId"]
                        if video_id:
                            if not Video.objects.filter(vid_id=video_id).exists():
                                # Fetch the full description
                                full_description = self.get_full_video_description(video_id)
                                
                                Video.objects.create(
                                    vid_id = video_id,
                                    title = title,
                                    description = full_description,  # Use full description
                                    img_url = item["snippet"]["thumbnails"]["high"]["url"],
                                    embed_url = f"https://www.youtube.com/watch?v={video_id}",
                                    is_new = True
                                )
                                titles.append(f"Uploaded: {video_id}")
                                count += 1

                return {
                    'count': count,
                    'titles': titles
                }
            else:
                return {
                    'count': 0,
                    'titles': []
                }
                
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            print(f"Error fetching videos: {e}")
            return {
                'count': 0,
                'titles': [],
                'error': str(e)
            }