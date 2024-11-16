from src.api import fetch_user_media, fetch_comments, post_reply
from src.utils import generate_specific_response, log_action
import time

# Reply log to keep track of replies per session
reply_log = {}

RATE_LIMIT = 5  # Limit to 5 replies per user per minute

def can_reply(user_id):
    """
    Check if the user is within the rate limit for replies.
    """
    current_time = time.time()
    if user_id not in reply_log:
        reply_log[user_id] = []

    # Remove logs older than 60 seconds
    reply_log[user_id] = [t for t in reply_log[user_id] if current_time - t < 60]

    # Allow reply if under the limit
    return len(reply_log[user_id]) < RATE_LIMIT

def log_reply(user_id, comment_id, response_message):
    """
    Log reply details to a file for auditing purposes.
    """
    with open("replies.log", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - User: {user_id} - Comment ID: {comment_id} - Reply: {response_message}\n")

def automate_replies(user_id):
    """
    Automate fetching comments and posting tailored replies using ChatGPT.
    """
    log_action("START_AUTOMATION", user_id, "Starting automation for user.")

    # Fetch user media (posts)
    media = fetch_user_media(user_id)
    if "error" in media:
        log_action("ERROR", user_id, f"Error fetching media: {media['error']}")
        return

    # Loop through each post
    for post in media.get("data", []):
        media_id = post["id"]
        log_action("PROCESS_MEDIA", user_id, f"Processing media ID: {media_id}")

        # Fetch comments for the post
        comments = fetch_comments(media_id, user_id)
        if "error" in comments:
            log_action("ERROR", user_id, f"Error fetching comments for media ID {media_id}: {comments['error']}")
            continue

        # Process each comment
        for comment in comments.get("data", []):
            comment_id = comment["id"]
            text = comment["text"]
            log_action("PROCESS_COMMENT", user_id, f"Analyzing comment: {text}")

            # Rate limiting check
            if not can_reply(user_id):
                log_action("RATE_LIMIT", user_id, "Rate limit reached. Skipping reply.")
                continue

            # Generate a response based on user-selected tone
            response_message = generate_specific_response(text, user_id)
            log_action("GENERATE_RESPONSE", user_id, f"Generated response: {response_message}")

            # Post the reply
            response = post_reply(comment_id, response_message, user_id)
            if "error" in response:
                log_action("ERROR", user_id, f"Error replying to comment {comment_id}: {response['error']}")
            else:
                log_action("REPLY_SUCCESS", user_id, f"Replied to comment {comment_id}: {response}")
                log_reply(user_id, comment_id, response_message)

                # Add the reply to the rate limit log
                reply_log[user_id].append(time.time())
