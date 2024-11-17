import requests
from flask import request, redirect, session
from src.database import SessionLocal, User
from config.settings import (
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_BASE_URL, TOKEN_URL, SCOPES,
    TIKTOK_CLIENT_ID, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI,
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REDIRECT_URI
)
from src.tiktok_api import fetch_user_videos as fetch_tiktok_videos, fetch_comments as fetch_tiktok_comments, post_comment_reply as post_tiktok_reply
from src.youtube_api import fetch_user_videos as fetch_youtube_videos, fetch_comments as fetch_youtube_comments, post_comment_reply as post_youtube_reply

def initiate_oauth():
    """
    Redirects the user to Instagram's OAuth login page.
    """
    auth_url = (
        f"{AUTH_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}&response_type=code"
    )
    return redirect(auth_url)

@app.route("/instagram/auth/callback")
def handle_callback():
    """
    Handles the callback from Instagram and exchanges the authorization code for an access token.
    Saves the user information and access token to the database.
    """
    code = request.args.get("code")
    if not code:
        return "Authorization failed!", 400

    # Exchange authorization code for access token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        return f"Failed to fetch access token: {response.json()}", 400

    token_data = response.json()
    access_token = token_data.get("access_token")
    user_id = token_data.get("user_id")

    # Save to database
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter_by(instagram_user_id=user_id).first()
        if not existing_user:
            new_user = User(
                instagram_user_id=user_id,
                username=f"user_{user_id}",  # Replace with real username if available
                access_token=access_token,
                token_expiry=None  # Add expiration logic if needed
            )
            db.add(new_user)
            db.commit()
        else:
            existing_user.access_token = access_token
            db.commit()
    finally:
        db.close()

    return f"User {user_id} authenticated and token saved!"

def get_access_token(user_id):
    """
    Retrieves the access token for a specific user from the database.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(instagram_user_id=user_id).first()
        if user:
            return user.access_token
        else:
            return None
    finally:
        db.close()

@app.route("/tiktok/auth")
def tiktok_auth():
    """
    Redirect user to TikTok for authentication.
    """
    tiktok_auth_url = (
        f"https://www.tiktok.com/auth/authorize"
        f"?client_id={TIKTOK_CLIENT_ID}"
        f"&redirect_uri={TIKTOK_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=video.list,comment.list,comment.write"
    )
    return redirect(tiktok_auth_url)

@app.route("/tiktok/auth/callback")
def tiktok_callback():
    """
    Handles TikTok OAuth callback.
    """
    code = request.args.get("code")
    if not code:
        return "TikTok Authorization failed!", 400

    # Exchange authorization code for access token
    data = {
        "client_id": TIKTOK_CLIENT_ID,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": TIKTOK_REDIRECT_URI,
        "code": code,
    }

    response = requests.post("https://open.tiktokapis.com/v1/oauth/token", json=data)
    if response.status_code != 200:
        return f"Failed to fetch TikTok access token: {response.json()}", 400

    token_data = response.json()
    access_token = token_data.get("access_token")
    open_id = token_data.get("open_id")

    # Save to database
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter_by(tiktok_user_id=open_id).first()
        if not existing_user:
            new_user = User(
                tiktok_user_id=open_id,
                tiktok_access_token=access_token
            )
            db.add(new_user)
            db.commit()
        else:
            existing_user.tiktok_access_token = access_token
            db.commit()
    finally:
        db.close()

    return f"TikTok user {open_id} authenticated and token saved!"

@app.route("/youtube/auth")
def youtube_auth():
    """
    Redirect user to YouTube for authentication.
    """
    youtube_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={YOUTUBE_CLIENT_ID}"
        f"&redirect_uri={YOUTUBE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=https://www.googleapis.com/auth/youtube.force-ssl"
    )
    return redirect(youtube_auth_url)

@app.route("/youtube/auth/callback")
def youtube_callback():
    """
    Handles YouTube OAuth callback.
    """
    code = request.args.get("code")
    if not code:
        return "YouTube Authorization failed!", 400

    # Exchange authorization code for access token
    data = {
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "code": code,
    }

    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    if response.status_code != 200:
        return f"Failed to fetch YouTube access token: {response.json()}", 400

    token_data = response.json()
    access_token = token_data.get("access_token")
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    youtube_user_id = user_info.get("id")

    # Save to database
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter_by(youtube_user_id=youtube_user_id).first()
        if not existing_user:
            new_user = User(
                youtube_user_id=youtube_user_id,
                youtube_access_token=access_token
            )
            db.add(new_user)
            db.commit()
        else:
            existing_user.youtube_access_token = access_token
            db.commit()
    finally:
        db.close()

    return f"YouTube user {youtube_user_id} authenticated and token saved!"

def automate_tiktok_replies(user_id):
    # Fetch TikTok videos and comments
    videos = fetch_tiktok_videos(user_id)
    for video in videos.get("data", []):
        video_id = video["id"]
        comments = fetch_tiktok_comments(video_id, user_id)
        for comment in comments.get("data", []):
            reply = generate_specific_response(comment["text"], user_id)
            post_tiktok_reply(comment["id"], reply, user_id)

def automate_youtube_replies(user_id):
    # Fetch YouTube videos and comments
    videos = fetch_youtube_videos(user_id)
    for video in videos.get("items", []):
        video_id = video["id"]["videoId"]
        comments = fetch_youtube_comments(video_id, user_id)
        for comment in comments.get("items", []):
            reply = generate_specific_response(comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"], user_id)
            post_youtube_reply(comment["id"], reply, user_id)
