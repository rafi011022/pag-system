# auth/auth.py
import jwt
import bcrypt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
from database.db import get_db_connection

SECRET_KEY = "pag-system-secret-key-2026"  # Replace with env variable in production
TOKEN_EXPIRY_HOURS = 8

# ── User roles ──────────────────────────────────────────────
ROLES = {
    "admin":   ["read", "write", "delete", "manage_users"],
    "ddm":     ["read", "write"],
    "uno":     ["read", "write"],
    "ngo":     ["read"],
    "viewer":  ["read"],
}

# ── Password helpers ─────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ── Token helpers ────────────────────────────────────────────
def generate_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "permissions": ROLES.get(role, []),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")

# ── Decorators ───────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Authentication token missing"}), 401
        try:
            request.user = decode_token(token)
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if request.user.get("role") not in allowed_roles:
                return jsonify({"error": "Access denied: insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ── Flask Auth App ────────────────────────────────────────────
app = Flask(__name__)

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    required = ["username", "password", "role", "full_name", "organization"]
    if not all(k in data for k in required):
        return jsonify({"error": f"Required fields: {required}"}), 400
    if data["role"] not in ROLES:
        return jsonify({"error": f"Invalid role. Choose from: {list(ROLES.keys())}"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username = %s", (data["username"],))
        if cur.fetchone():
            return jsonify({"error": "Username already exists"}), 409

        hashed = hash_password(data["password"])
        cur.execute(
            """INSERT INTO users (username, password_hash, role, full_name, organization, created_at)
               VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id""",
            (data["username"], hashed, data["role"], data["full_name"], data["organization"])
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, password_hash, role, full_name FROM users WHERE username = %s",
            (data["username"],)
        )
        user = cur.fetchone()
        if not user or not verify_password(data["password"], user[2]):
            return jsonify({"error": "Invalid username or password"}), 401

        cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user[0],))
        conn.commit()

        token = generate_token(user[0], user[1], user[3])
        return jsonify({
            "token": token,
            "user": {"id": user[0], "username": user[1], "role": user[3], "full_name": user[4]},
            "expires_in": f"{TOKEN_EXPIRY_HOURS} hours"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/api/auth/me", methods=["GET"])
@login_required
def me():
    return jsonify({"user": request.user}), 200

@app.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    # In production: add token to a blacklist in Redis
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)
