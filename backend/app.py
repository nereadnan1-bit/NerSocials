# backend/app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for now, tighten later

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SUPABASE_URL'] = os.environ.get('SUPABASE_URL')
app.config['SUPABASE_KEY'] = os.environ.get('SUPABASE_KEY')

def get_supabase() -> Client:
    return create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

# Change this to YOUR email address (the one you'll use to log in as admin)
ADMIN_EMAILS = ["nereadnan1@gmail.com"]

# Decorators
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(' ')[1]
        supabase = get_supabase()
        try:
            user = supabase.auth.get_user(token)
            request.user = user.user
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user.email not in ADMIN_EMAILS:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

# Auth Routes
@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email required"}), 400
    supabase = get_supabase()
    try:
        supabase.auth.sign_in_with_otp({"email": email, "options": {"should_create_user": True}})
        return jsonify({"message": "OTP sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    token = data.get('token')
    if not email or not token:
        return jsonify({"error": "Email and token required"}), 400
    supabase = get_supabase()
    try:
        response = supabase.auth.verify_otp({"email": email, "token": token, "type": "email"})
        return jsonify({
            "access_token": response.session.access_token,
            "user": {"id": response.user.id, "email": response.user.email}
        }), 200
    except Exception as e:
        return jsonify({"error": "Invalid OTP"}), 401

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me():
    user = request.user
    return jsonify({
        "id": user.id,
        "email": user.email,
        "is_admin": user.email in ADMIN_EMAILS
    }), 200

# Blog Routes
TABLE_NAME = "blog_posts"

@app.route('/api/blog/posts', methods=['GET'])
def get_posts():
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME).select("*").eq("published", True).order("created_at", desc=True).execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blog/posts/<slug>', methods=['GET'])
def get_post(slug):
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME).select("*").eq("slug", slug).eq("published", True).single().execute()
        if not res.data:
            return jsonify({"error": "Not found"}), 404
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blog/admin/posts', methods=['GET'])
@admin_required
def admin_get_posts():
    supabase = get_supabase()
    res = supabase.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    return jsonify(res.data), 200

@app.route('/api/blog/admin/posts', methods=['POST'])
@admin_required
def admin_create_post():
    data = request.get_json()
    if not all(k in data for k in ['title', 'slug', 'content']):
        return jsonify({"error": "Missing fields"}), 400
    supabase = get_supabase()
    post = {
        "title": data['title'],
        "slug": data['slug'],
        "content": data['content'],
        "excerpt": data.get('excerpt', ''),
        "published": data.get('published', False)
    }
    res = supabase.table(TABLE_NAME).insert(post).execute()
    return jsonify(res.data[0]), 201

@app.route('/api/blog/admin/posts/<slug>', methods=['PUT'])
@admin_required
def admin_update_post(slug):
    data = request.get_json()
    update = {k: v for k, v in data.items() if k in ['title', 'content', 'excerpt', 'published', 'slug']}
    if not update:
        return jsonify({"error": "No fields to update"}), 400
    supabase = get_supabase()
    res = supabase.table(TABLE_NAME).update(update).eq("slug", slug).execute()
    if not res.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify(res.data[0]), 200

@app.route('/api/blog/admin/posts/<slug>', methods=['DELETE'])
@admin_required
def admin_delete_post(slug):
    supabase = get_supabase()
    res = supabase.table(TABLE_NAME).delete().eq("slug", slug).execute()
    if not res.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200

@app.route('/')
def index():
    return jsonify({"message": "Portfolio API is running"}), 200

if __name__ == '__main__':
    app.run()