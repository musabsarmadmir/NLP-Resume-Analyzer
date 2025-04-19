import sys
from auth_system import AuthUI
from parser_nltk import ResumeParser

def main():
    auth_ui = AuthUI(on_login_success=on_successful_login)
    user = auth_ui.run()
    
    if user:
        print(f"User authenticated: {user[1]} (ID: {user[0]})")
        parser = ResumeParser(user_id=user[0])
    else:
        print("Authentication failed or was cancelled")
        sys.exit(0)

def on_successful_login(user):
    print(f"Login successful: {user[1]}")

if __name__ == "__main__":
    main()