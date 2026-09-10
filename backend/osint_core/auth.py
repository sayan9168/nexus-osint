"""Local-first authentication and JWT session management for NEXUS-OSINT."""
from __future__ import annotations
import hashlib, hmac, os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import JWTError, jwt
from .persistence import db, json_dumps

JWT_SECRET = os.getenv("NEXUS_JWT_SECRET", "change-me-in-production")
JWT_ALG = "HS256"
SESSION_MINUTES = int(os.getenv("NEXUS_SESSION_MINUTES", "480"))

def _hash(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return salt.hex(), digest.hex()

def create_user(username: str, password: str, role: str = "viewer") -> dict:
    username = username.strip().lower()
    if len(username) < 3 or len(password) < 10:
        raise ValueError("username must be 3+ chars and password 10+ chars")
    if role not in {"viewer", "analyst", "admin"}:
        raise ValueError("invalid role")
    if db.execute("SELECT id FROM users WHERE username=?", (username,)):
        raise ValueError("user already exists")
    salt, digest = _hash(password)
    uid = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    db.insert("INSERT INTO users(id,username,password_salt,password_hash,role,created_at) VALUES(?,?,?,?,?,?)", (uid, username, salt, digest, role, now))
    return {"id": uid, "username": username, "role": role, "created_at": now}

def authenticate(username: str, password: str) -> dict | None:
    rows = db.execute("SELECT * FROM users WHERE username=?", (username.strip().lower(),))
    if not rows: return None
    row = rows[0]
    _, digest = _hash(password, bytes.fromhex(row["password_salt"]))
    if not hmac.compare_digest(digest, row["password_hash"]): return None
    return {"id": row["id"], "username": row["username"], "role": row["role"]}

def issue_session(user: dict) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user["id"], "username": user["username"], "role": user["role"], "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=SESSION_MINUTES)).timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_session(token: str) -> dict:
    try: return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc: raise ValueError("invalid or expired session") from exc

def bootstrap_admin() -> None:
    username = os.getenv("NEXUS_BOOTSTRAP_ADMIN")
    password = os.getenv("NEXUS_BOOTSTRAP_PASSWORD")
    if username and password and not db.execute("SELECT id FROM users LIMIT 1"):
        create_user(username, password, "admin")
