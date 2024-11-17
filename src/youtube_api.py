import requests

def fetch_user_videos(access_token):
    url = "https://www.googleapis.com/youtube/v3/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"part": "snippet", "type": "video", "q": "shorts", "maxResults": 10}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def fetch_comments(video_id, access_token):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"part": "snippet", "videoId": video_id}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def post_comment_reply(comment_id, reply_text, access_token):
    url = f"https://www.googleapis.com/youtube/v3/comments"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "snippet": {
            "parentId": comment_id,
            "textOriginal": reply_text
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
