from backend.db import execute_query

def create_users():
    print("🚀 Seeding Users...")
    
    users = [
        {"username": "admin", "password": "password123", "role": "admin"},
        {"username": "doctor_smith", "password": "password123", "role": "doctor"},
        {"username": "billing_user", "password": "password123", "role": "billing"}
    ]
    
    for u in users:
        try:
            # Check if exists
            check = execute_query(f"SELECT * FROM users WHERE username = '{u['username']}'")
            if not check:
                print(f"Creating {u['username']}...")
                execute_query(f"INSERT INTO users (username, password, role) VALUES ('{u['username']}', '{u['password']}', '{u['role']}')")
            else:
                print(f"User {u['username']} already exists.")
        except Exception as e:
            print(f"❌ Failed to create {u['username']}: {e}")

    print("✅ Seed complete.")

if __name__ == "__main__":
    create_users()
