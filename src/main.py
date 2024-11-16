from src.oauth import initiate_oauth, handle_callback
from src.api import fetch_comments
from flask import Flask, render_template
from flask import request, redirect
from src.database import SessionLocal, User  # Import the database session and User model
from src.automation import automate_replies


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key for sessions

@app.route("/")
def home():
    return "Welcome to ReplyForMe! <a href='/auth/login'>Login with Instagram</a>"

@app.route("/auth/login")
def login():
    return initiate_oauth()

@app.route("/auth/callback")
def callback():
    return handle_callback()

@app.route("/fetch_comments/<media_id>/<user_id>")
def fetch_post_comments(media_id, user_id):
    """
    Fetch comments for a specific media post.
    """
    comments = fetch_comments(media_id, user_id)
    return comments

@app.route("/dashboard")
def dashboard():
    """
    Renders the dashboard showing user data from the database.
    """
    db = SessionLocal()  # Start a new database session
    try:
        users = db.query(User).all()  # Query all users in the database
    finally:
        db.close()  # Ensure the session is closed

    return render_template("dashboard.html", users=users)

@app.route("/automate/<user_id>")
def automate(user_id):
    automate_replies(user_id)
    return f"Automation complete for user: {user_id}"

@app.route("/set_tone/<user_id>", methods=["POST"])
def set_tone(user_id):
    """
    Updates the user's preferred reply tone.
    """
    reply_tone = request.form.get("reply_tone")
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(instagram_user_id=user_id).first()
        if user:
            user.reply_tone = reply_tone
            db.commit()
    finally:
        db.close()
    return redirect("/dashboard")

@app.route("/reply_history/<user_id>")
def reply_history(user_id):
    """
    Displays the reply history for a specific user.
    """
    log_file = "replies.log"
    user_replies = []

    try:
        with open(log_file, "r") as f:
            for line in f:
                if f"User: {user_id}" in line:
                    user_replies.append(line.strip())
    except FileNotFoundError:
        return f"No reply history found for user: {user_id}"

    return render_template("reply_history.html", user_id=user_id, replies=user_replies)


if __name__ == "__main__":
    app.run(debug=True)

