from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

bcrypt = Bcrypt()
register_bp = Blueprint("register_bp", __name__)

@register_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc mật khẩu"}), 400

    # Kiểm tra email đã tồn tại chưa
    existing_user = supabase.table("users_aibot").select("id").eq("email", email).execute()
    if existing_user.data:
        return jsonify({"error": "Email đã được đăng ký"}), 400

    # Hash mật khẩu
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Lưu vào Supabase, dùng try/except để bắt lỗi
    try:
        res = supabase.table("users_aibot").insert({
            "email": email,
            "password_hash": pw_hash
        }).execute()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Thành công
    return jsonify({
        "success": True,
        "message": "Đăng ký thành công",
        "redirect": "/login-ui"
    }), 200
