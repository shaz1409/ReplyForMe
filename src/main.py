from flask import Flask, session
from src.oauth import initiate_oauth, handle_callback

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

if __name__ == "__main__":
    app.run(debug=True)
