import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Cho phép Cross-Origin Resource Sharing (CORS) để frontend có thể gọi API
CORS(app)

# 🔐 DÁN TRỰC TIẾP SESSION_ID VÀ CSRF_TOKEN CỦA BẠN VÀO ĐÂY
# Lấy các giá trị này từ cookie của trình duyệt sau khi đăng nhập Instagram
SESSION_ID = "DÁN_GIÁ_TRỊ_SESSIONID_MỚI_CỦA_BẠN_VÀO_ĐÂY"
CSRF_TOKEN = "61843189970%3AvhDdOCsdfCCYu1%3A26%3AAYdXhf1rv5MQnHrUoKIufmUSFDob_CTgtvn12C1P3w"
APP_ID = "936619743392459"  # ID này thường không thay đổi

# Tạo một route duy nhất để xử lý tất cả các yêu cầu
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    # Lấy các tham số từ URL (ví dụ: ?username=abc&action=posts)
    username = request.args.get("username")
    action = request.args.get("action", "userinfo")
    max_count = request.args.get("count", 12)

    # --- Kiểm tra đầu vào ---
    if not username:
        return jsonify({"error": "Thiếu tham số 'username'"}), 400

    if SESSION_ID == "DÁN_GIÁ_TRỊ_SESSIONID_MỚI_CỦA_BẠN_VÀO_ĐÂY" or CSRF_TOKEN == "DÁN_GIÁ_TRỊ_CSRFTOKEN_MỚI_CỦA_BẠN_VÀO_ĐÂY":
        return jsonify({"error": "Lỗi cấu hình: Vui lòng cập nhật SESSION_ID và CSRF_TOKEN trong file code."}), 500

    # --- Chuẩn bị header cho yêu cầu đến Instagram ---
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'X-IG-App-ID': APP_ID,
        'X-CSRFToken': CSRF_TOKEN,
        'Cookie': f'sessionid={SESSION_ID}; csrftoken={CSRF_TOKEN}',
    }

    try:
        # --- Lấy thông tin người dùng để có user_id ---
        user_info_url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
        user_info_res = requests.get(user_info_url, headers=headers)
        
        if user_info_res.status_code != 200:
            return jsonify({"error": "Không thể lấy thông tin người dùng", "status_code": user_info_res.status_code}), user_info_res.status_code

        user_data = user_info_res.json().get('data', {}).get('user', {})
        if not user_data:
            return jsonify({"error": "Không tìm thấy người dùng"}), 404

        # --- Xử lý theo hành động (action) ---
        if action == 'userinfo':
            # Trả về thông tin người dùng
            return jsonify(user_data)

        elif action == 'posts':
            user_id = user_data.get('id')
            if not user_id:
                return jsonify({"error": "Không lấy được User ID"}), 400
            
            # Endpoint này dùng để lấy các bài đăng
            post_url = f'https://www.instagram.com/api/v1/feed/user/{user_id}/?count={max_count}'
            posts_res = requests.get(post_url, headers=headers)

            if posts_res.status_code != 200:
                 return jsonify({"error": "Không thể lấy danh sách bài đăng", "status_code": posts_res.status_code}), posts_res.status_code
            
            # Trả về danh sách bài đăng
            return jsonify(posts_res.json())

        else:
            return jsonify({"error": "Hành động không hợp lệ"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel sẽ tự động chạy ứng dụng Flask này
