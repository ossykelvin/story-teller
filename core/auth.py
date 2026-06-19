import hashlib
import hmac
import json
from pathlib import Path
from core.config import LOCAL_STORAGE_PATH, env
from core.utils import now_iso

USERS_FILE = LOCAL_STORAGE_PATH / "users.json"


def _hash_password(password: str, salt: str = "local-mvp") -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def init_users() -> None:
    LOCAL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    admin_username = env("LOCAL_ADMIN_USERNAME", "admin")
    admin_password = env("LOCAL_ADMIN_PASSWORD", "change-me")
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({
            admin_username: {
                "username": admin_username,
                "password_hash": _hash_password(admin_password),
                "role": "admin",
                "created_at": now_iso(),
            }
        }, indent=2), encoding="utf-8")


def load_users() -> dict:
    init_users()
    return json.loads(USERS_FILE.read_text(encoding="utf-8"))


def authenticate(username: str, password: str) -> bool:
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    return hmac.compare_digest(user.get("password_hash", ""), _hash_password(password))


def create_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."
    users = load_users()
    if username in users:
        return False, "User already exists."
    users[username] = {
        "username": username,
        "password_hash": _hash_password(password),
        "role": "writer",
        "created_at": now_iso(),
    }
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")
    return True, "User created."
