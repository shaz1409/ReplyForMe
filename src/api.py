import requests
from src.oauth import get_access_token
from textblob import TextBlob

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

def fetch_comments(media_id, user_id):
    """
    Fetch comments for a specific media post.
    """
    access_token = get_access_token(user_id)
    if not access_token:
        return {"error": "User not authenticated or token missing."}

    url = f"https://graph.instagram.com/{media_id}/comments"
    params = {"access_token": access_token}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": response.json()}

    return response.json()

def post_reply(comment_id, message, user_id):
    """
    Post a reply to a specific comment.
    """
    access_token = get_access_token(user_id)
    if not access_token:
        return {"error": "User not authenticated or token missing."}

    url = f"https://graph.instagram.com/{comment_id}/replies"
    data = {
        "message": message,
        "access_token": access_token
    }
    response = requests.post(url, data=data)

    if response.status_code != 200:
        return {"error": response.json()}

    return response.json()

def analyze_comment_sentiment(comment):
    """
    Analyze the sentiment of a comment.
    Returns: 'positive', 'neutral', or 'negative'
    """
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"
