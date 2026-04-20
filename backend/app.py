import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from functools import wraps

app = Flask(__name__)

# ============================================================
# CORS CONFIGURATION – Guaranteed to work
# ============================================================
CORS(app, origins=[
    "https://nersocials-1.onrender.com",
    "https://nersocials-frontend.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
], supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# ============================================================
# Configuration
# ============================================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SUPABASE_URL'] = os.environ.get('SUPABASE_URL')
app.config['SUPABASE_KEY'] = os.environ.get('SUPABASE_KEY')

def get_supabase() -> Client:
    return create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

# Admin email(s) – only these emails get admin access
ADMIN_EMAILS = ["nereadnan1@gmail.com"]

# ============================================================
# Decorators
# ============================================================
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
        except Exception:
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

# ============================================================
# Authentication Routes (Username = Email, Password)
# ============================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return jsonify({
            "message": "Registration successful. Please check your email to confirm.",
            "user": response.user.email
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return jsonify({
            "access_token": response.session.access_token,
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
        return jsonify({"message": "Logged out"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me():
    user = request.user
    return jsonify({
        "id": user.id,
        "email": user.email,
        "is_admin": user.email in ADMIN_EMAILS
    }), 200

# ============================================================
# Public Blog Routes
# ============================================================
TABLE_NAME = "blog_posts"

@app.route('/api/blog/posts', methods=['GET'])
def get_posts():
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME)\
            .select("*")\
            .eq("published", True)\
            .order("created_at", desc=True)\
            .execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blog/posts/<slug>', methods=['GET'])
def get_post(slug):
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME)\
            .select("*")\
            .eq("slug", slug)\
            .eq("published", True)\
            .single()\
            .execute()
        if not res.data:
            return jsonify({"error": "Post not found"}), 404
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# Admin Blog Routes
# ============================================================
@app.route('/api/blog/admin/posts', methods=['GET'])
@admin_required
def admin_get_posts():
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME)\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/blog/admin/posts', methods=['POST'])
@admin_required
def admin_create_post():
    data = request.get_json()
    required = ['title', 'slug', 'content']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    supabase = get_supabase()
    post = {
        "title": data['title'],
        "slug": data['slug'],
        "content": data['content'],
        "excerpt": data.get('excerpt', ''),
        "published": data.get('published', False)
    }
    try:
        res = supabase.table(TABLE_NAME).insert(post).execute()
        return jsonify(res.data[0]), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/blog/admin/posts/<slug>', methods=['PUT'])
@admin_required
def admin_update_post(slug):
    data = request.get_json()
    update = {k: v for k, v in data.items() if k in ['title', 'slug', 'content', 'excerpt', 'published']}
    if not update:
        return jsonify({"error": "No valid fields"}), 400
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME).update(update).eq("slug", slug).execute()
        if not res.data:
            return jsonify({"error": "Post not found"}), 404
        return jsonify(res.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/blog/admin/posts/<slug>', methods=['DELETE'])
@admin_required
def admin_delete_post(slug):
    supabase = get_supabase()
    try:
        res = supabase.table(TABLE_NAME).delete().eq("slug", slug).execute()
        if not res.data:
            return jsonify({"error": "Post not found"}), 404
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============================================================
# Health Check & Debug
# ============================================================
@app.route('/')
def index():
    return jsonify({"message": "Portfolio API is running"}), 200

@app.route('/debug')
def debug():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": sys.version
    })

if __name__ == '__main__':
    app.run()