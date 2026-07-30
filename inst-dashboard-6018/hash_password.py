from backend.auth_utils import get_password_hash

password = "test"
print(get_password_hash(password))
