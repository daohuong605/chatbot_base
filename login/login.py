from flask import Blueprint, request, jsonify, session
from supabase import create_client
import os
import bcrypt

login_bp = Blueprint("login", __name__)

# Kết nối Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@login_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc password"}), 400

    # Lấy user theo email
    result = (
        supabase.table("users_aibot")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Sai tài khoản hoặc mật khẩu"}), 401

    user = result.data[0]

    # Kiểm tra password (bcrypt)
    stored_hash = user.get("password_hash")
    if not stored_hash:
        return jsonify({"error": "User chưa có password"}), 401

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        # Lưu session
        session["user"] = {"id": user["id"], "email": user["email"]}
        return jsonify({"success": True, "redirect": "/chatbot"}), 200
    else:
        return jsonify({"error": "Sai tài khoản hoặc mật khẩu"}), 401
