from app.auth import hash_password, verify_password

plain = "mysecretpassword"
hashed = hash_password(plain)

print(f"Plain: {plain}")
print(f"Hashed: {hashed}")
print(f"Verification (correct): {verify_password(plain, hashed)}")
print(f"Verification (incorrect): {verify_password('wrongpassword', hashed)}")