import requests
from src.oauth import get_access_token

def fetch_user_media(user_id):
    """
    Fetch the media (posts) for a user using the Instagram Graph API.
    """
    access_token = get_access_token(user_id)
    if not access_token:
        return {"error": "User not authenticated or token missing."}

    url = "https://graph.instagram.com/me/media"
    params = {
        "fields": "id,caption",
        "access_token": access_token
    }
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return {"error": response.json()}
    
    return response.json()
