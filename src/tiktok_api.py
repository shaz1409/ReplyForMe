import requests

def fetch_user_videos(access_token):
    url = "https://open.tiktokapis.com/v1/videos"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_comments(video_id, access_token):
    url = f"https://open.tiktokapis.com/v1/comments?video_id={video_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def post_comment_reply(comment_id, reply_text, access_token):
    url = f"https://open.tiktokapis.com/v1/comments/reply"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"comment_id": comment_id, "reply_text": reply_text}
    response = requests.post(url, json=data, headers=headers)
    return response.json()
