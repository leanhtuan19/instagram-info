import json
import requests

# 🔐 Hardcoded session ID and CSRF token
SESSION_ID = "61843189970%3AvhDdOCsdfCCYu1%3A26%3AAYdXhf1rv5MQnHrUoKIufmUSFDob_CTgtvn12C1P3w"
CSRF_TOKEN = "awEUQG8f6F5qdDlxfuc1pqvHkyV1wciy"

def handler(request):
    params = request.get("query", {})
    username = params.get("username")
    action = params.get("action", "userinfo")
    max_count = int(params.get("count", 5))

    if not username:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'username' parameter"})
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-CSRFToken": CSRF_TOKEN,
        "Cookie": f"sessionid={SESSION_ID}",
        "X-IG-App-ID": "936619743392459",
    }

    try:
        if action == "userinfo":
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                user = r.json().get("data", {}).get("user", {})
                if user:
                    return {
                        "statusCode": 200,
                        "body": json.dumps({
                            "username": user.get("username"),
                            "full_name": user.get("full_name"),
                            "user_id": user.get("id"),
                            "follower_count": user.get("edge_followed_by", {}).get("count"),
                            "following_count": user.get("edge_follow", {}).get("count"),
                            "post_count": user.get("edge_owner_to_timeline_media", {}).get("count"),
                            "is_private": user.get("is_private"),
                            "is_verified": user.get("is_verified"),
                            "bio": user.get("biography"),
                            "profile_pic_url": user.get("profile_pic_url_hd"),
                        })
                    }
                else:
                    return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}
            else:
                return {"statusCode": r.status_code, "body": json.dumps({"error": "Failed to fetch user info"})}

        elif action == "posts":
            user_info_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            r = requests.get(user_info_url, headers=headers)
            user_id = r.json().get("data", {}).get("user", {}).get("id")
            if not user_id:
                return {"statusCode": 400, "body": json.dumps({"error": "User ID not found"})}

            post_url = f"https://www.instagram.com/api/v1/media/{user_id}/feed/?count={max_count}"
            response = requests.get(post_url, headers=headers)
            if response.status_code == 200:
                posts = response.json().get("data", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
                result = []
                for post in posts:
                    node = post.get("node", {})
                    result.append({
                        "post_id": node.get("id"),
                        "caption": node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", ""),
                        "media_url": node.get("display_url"),
                        "timestamp": node.get("taken_at_timestamp"),
                        "like_count": node.get("edge_liked_by", {}).get("count"),
                        "comment_count": node.get("edge_media_to_comment", {}).get("count"),
                    })
                return {"statusCode": 200, "body": json.dumps(result)}
            else:
                return {"statusCode": response.status_code, "body": json.dumps({"error": "Failed to fetch posts"})}

        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid action"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
