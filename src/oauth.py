import requests
from flask import request, redirect, session
from src.database import SessionLocal, User
from config.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_BASE_URL, TOKEN_URL, SCOPES

def initiate_oauth():
    """
    Redirects the user to Instagram's OAuth login page.
    """
    auth_url = (
        f"{AUTH_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}&response_type=code"
    )
    return redirect(auth_url)

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
