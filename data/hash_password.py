import bcrypt

password = "4@3Yedgar888"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed)
