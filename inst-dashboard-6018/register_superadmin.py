from backend.database import get_db_connection, get_user, create_user
from backend.auth_utils import get_password_hash

def register_superadmin_user():
    username = "superadmin"
    password = "superadmin"
    full_name = "Super Admin User"
    tenant_id = None # Superadmin is not tied to a specific tenant
    is_super_admin = 1 # Use 1 for True in SQLite
    is_admin = 1 # Superadmin is also an admin

    mobile_phone = None
    audience_type = None

    # Check if user already exists
    existing_user = get_user(username=username, tenant_id=tenant_id)
    if existing_user:
        print(f"User '{username}' already exists.")
        return

    hashed_password = get_password_hash(password)
    create_user(
        username=username,
        hashed_password=hashed_password,
        is_admin=is_admin,
        full_name=full_name,
        tenant_id=tenant_id,
        mobile_phone=mobile_phone,
        audience_type=audience_type
    )
    print(f"Superadmin user '{username}' registered successfully.")

if __name__ == "__main__":
    register_superadmin_user()