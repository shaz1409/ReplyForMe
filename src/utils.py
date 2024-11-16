import openai
from datetime import datetime
from src.database import SessionLocal, User

# Set OpenAI API key
openai.api_key = "your-openai-api-key"

def is_token_expired(expiry_date):
    """
    Checks if the token expiry date has passed.
    """
    if expiry_date and datetime.utcnow() > expiry_date:
        return True
    return False

def generate_specific_response(comment, user_id):
    """
    Generate a specific response using OpenAI GPT model based on user-selected tone.
    """
    # Fetch user preferences
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(instagram_user_id=user_id).first()
        reply_tone = user.reply_tone if user else "positive"
    finally:
        db.close()

    # ChatGPT prompt based on tone
    prompt = f"""
    You are an Instagram comment bot. Generate a reply to this comment:
    "{comment}"
    The tone of the reply should be {reply_tone}.
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )

    return response.choices[0].text.strip()

def log_action(action_type, user_id, details):
    """
    Logs actions to a log file for auditing purposes.
    """
    with open("bot_actions.log", "a") as log_file:
        log_file.write(f"{datetime.utcnow()} - {action_type} - User: {user_id} - {details}\n")