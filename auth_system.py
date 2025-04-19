import sqlite3
import hashlib
import customtkinter as ctk
from tkinter import messagebox

class AuthSystem:
    def __init__(self, db_path='resumes_analyzer_ATS.db'):
        self.db_path = db_path
        self.current_user = None
        self.initialize_database()
        
    def initialize_database(self):
        """Initialize the database with required tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, name, age, email, password):
        hashed_password = self.hash_password(password)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, age, email, password)
                VALUES (?, ?, ?, ?)
            ''', (name, age, email, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def authenticate_user(self, email, password):
        hashed_password = self.hash_password(password)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed_password))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

class AuthUI:
    def __init__(self, on_login_success=None):
        self.auth_system = AuthSystem()
        self.on_login_success = on_login_success
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.title("Login/Register")
        self.window.geometry("800x600")
        
        self.container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_login_frame()
        
    def show_login_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        login_frame = ctk.CTkFrame(
            self.container,
            width=400,
            height=500,
            corner_radius=15,
            fg_color="#ffffff"
        )
        login_frame.pack(expand=True)
        login_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            login_frame,
            text="Login/Register",
            font=("Helvetica", 32, "bold")
        ).pack(pady=(40, 20))
        
        email_entry = ctk.CTkEntry(
            login_frame,
            width=300,
            height=50,
            placeholder_text="Email",
            corner_radius=25
        )
        email_entry.pack(pady=10)
        
        password_entry = ctk.CTkEntry(
            login_frame,
            width=300,
            height=50,
            placeholder_text="Password",
            show="•",
            corner_radius=25
        )
        password_entry.pack(pady=10)
        
        login_button = ctk.CTkButton(
            login_frame,
            width=300,
            height=50,
            text="Sign In",
            font=("Helvetica", 15, "bold"),
            corner_radius=25,
            command=lambda: self.login(email_entry.get(), password_entry.get())
        )
        login_button.pack(pady=20)
        
        signup_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        signup_frame.pack(pady=20)
        
        ctk.CTkLabel(
            signup_frame,
            text="Don't have an account? ",
            font=("Helvetica", 12),
            text_color="#666666"
        ).pack(side="left")
        
        ctk.CTkButton(
            signup_frame,
            text="Sign Up",
            font=("Helvetica", 12, "bold"),
            fg_color="transparent",
            text_color="#000000",
            hover_color="#eeeeee",
            command=self.show_register_frame
        ).pack(side="left")

    def show_register_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()
            
        register_frame = ctk.CTkFrame(
            self.container,
            width=400,
            height=600,
            corner_radius=15,
            fg_color="#ffffff"
        )
        register_frame.pack(expand=True)
        register_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            register_frame,
            text="Register",
            font=("Helvetica", 32, "bold")
        ).pack(pady=(40, 20))
        
        name_entry = ctk.CTkEntry(
            register_frame,
            width=300,
            height=50,
            placeholder_text="Name",
            corner_radius=25
        )
        name_entry.pack(pady=10)
        
        age_entry = ctk.CTkEntry(
            register_frame,
            width=300,
            height=50,
            placeholder_text="Age",
            corner_radius=25
        )
        age_entry.pack(pady=10)
        
        email_entry = ctk.CTkEntry(
            register_frame,
            width=300,
            height=50,
            placeholder_text="Email",
            corner_radius=25
        )
        email_entry.pack(pady=10)
        
        password_entry = ctk.CTkEntry(
            register_frame,
            width=300,
            height=50,
            placeholder_text="Password",
            show="•",
            corner_radius=25
        )
        password_entry.pack(pady=10)
        
        confirm_password_entry = ctk.CTkEntry(
            register_frame,
            width=300,
            height=50,
            placeholder_text="Confirm Password",
            show="•",
            corner_radius=25
        )
        confirm_password_entry.pack(pady=10)
        
        register_button = ctk.CTkButton(
            register_frame,
            width=300,
            height=50,
            text="Register",
            font=("Helvetica", 15, "bold"),
            corner_radius=25,
            command=lambda: self.register(
                name_entry.get(),
                age_entry.get(),
                email_entry.get(),
                password_entry.get(),
                confirm_password_entry.get()
            )
        )
        register_button.pack(pady=20)
        
        login_frame = ctk.CTkFrame(register_frame, fg_color="transparent")
        login_frame.pack(pady=20)
        
        ctk.CTkLabel(
            login_frame,
            text="Already have an account? ",
            font=("Helvetica", 12),
            text_color="#666666"
        ).pack(side="left")
        
        ctk.CTkButton(
            login_frame,
            text="Login",
            font=("Helvetica", 12, "bold"),
            fg_color="transparent",
            text_color="#000000",
            hover_color="#eeeeee",
            command=self.show_login_frame
        ).pack(side="left")

    def login(self, email, password):
        if not email or not password:
            self.show_message("Error", "Please enter both email and password")
            return
            
        user = self.auth_system.authenticate_user(email, password)
        if user:
            self.auth_system.current_user = user
            self.show_message("Success", f"Welcome back, {user[1]}!")
            if self.on_login_success:
                self.on_login_success(user)
            self.window.destroy()
        else:
            self.show_message("Error", "Invalid email or password")

    def register(self, name, age, email, password, confirm_password):
        if not name or not age or not email or not password or not confirm_password:
            self.show_message("Error", "Please fill in all fields")
            return
            
        try:
            age = int(age)
        except ValueError:
            self.show_message("Error", "Age is a postive integer")
            return
            
        if password != confirm_password:
            self.show_message("Error", "Passwords do not match")
            return
        
        success = self.auth_system.register_user(name, age, email, password)
        
        if success:
            self.show_message("Success", "Registration successful. Please login.")
            self.show_login_frame()
        else:
            self.show_message("Error", "Registration failed. Email may already be in use.")

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def run(self):
        self.window.mainloop()
        return self.auth_system.current_user