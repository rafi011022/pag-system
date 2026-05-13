# tests/test_auth.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import jwt
from unittest.mock import patch, MagicMock
from auth.auth import (
    hash_password, verify_password,
    generate_token, decode_token,
    ROLES, SECRET_KEY
)

# ── Password tests ────────────────────────────────────────────
class TestPassword:
    def test_hash_password_returns_string(self):
        hashed = hash_password("TestPassword@123")
        assert isinstance(hashed, str)
        assert hashed != "TestPassword@123"

    def test_verify_correct_password(self):
        hashed = hash_password("CorrectPassword")
        assert verify_password("CorrectPassword", hashed) is True

    def test_reject_wrong_password(self):
        hashed = hash_password("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_same_password(self):
        h1 = hash_password("SamePass")
        h2 = hash_password("SamePass")
        assert h1 != h2   # bcrypt salts differ

# ── Token tests ───────────────────────────────────────────────
class TestToken:
    def test_generate_token_returns_string(self):
        token = generate_token(1, "testuser", "admin")
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        token = generate_token(1, "testuser", "ddm")
        payload = decode_token(token)
        assert payload["username"] == "testuser"
        assert payload["role"] == "ddm"
        assert payload["user_id"] == 1

    def test_permissions_in_token(self):
        token = generate_token(1, "ngo_user", "ngo")
        payload = decode_token(token)
        assert "read" in payload["permissions"]
        assert "delete" not in payload["permissions"]

    def test_admin_has_all_permissions(self):
        token = generate_token(1, "admin", "admin")
        payload = decode_token(token)
        assert set(["read", "write", "delete", "manage_users"]).issubset(payload["permissions"])

    def test_expired_token_raises(self):
        import datetime
        payload = {
            "user_id": 1, "username": "x", "role": "viewer",
            "permissions": [],
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            "iat": datetime.datetime.utcnow() - datetime.timedelta(hours=9),
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        with pytest.raises(ValueError, match="expired"):
            decode_token(expired_token)

    def test_invalid_token_raises(self):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token("this.is.not.a.valid.token")

# ── Role tests ────────────────────────────────────────────────
class TestRoles:
    def test_all_roles_defined(self):
        for role in ["admin", "ddm", "uno", "ngo", "viewer"]:
            assert role in ROLES

    def test_viewer_read_only(self):
        assert ROLES["viewer"] == ["read"]

    def test_ngo_read_only(self):
        assert "write" not in ROLES["ngo"]
