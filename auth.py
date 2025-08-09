import streamlit as st
import hashlib
import json
import os

# File to store user credentials
USERS_FILE = "users.json"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def register_user(username, password, email):
    """Register a new user"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": hash_password(password),
        "email": email
    }
    save_users(users)
    return True, "Registration successful"

def verify_user(username, password):
    """Verify user credentials"""
    users = load_users()
    
    if username not in users:
        return False
    
    return users[username]["password"] == hash_password(password)
def login():
    """Professional, clean login system with registration"""
    st.markdown(
        """
        <style>
        /* Center the container vertically and horizontally */
        .full-page {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        .login-container {
            max-width: 380px;
            width: 100%;
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
        }
        .login-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .login-header h2 {
            color: #0d47a1;
            font-size: 1.5rem;
            margin: 0;
            font-weight: 600;
        }
        .stTextInput > div > div > input {
            border-radius: 6px;
        }
        .stButton>button {
            width: 100%;
            font-weight: 500;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "show_register" not in st.session_state:
        st.session_state.show_register = False

    if not st.session_state.logged_in:

        if not st.session_state.show_register:
            # Login form
            st.markdown(
                """
                <div class="login-header">
                    <h2>CrimeScan Login</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", placeholder="Enter your password", type="password")

            login_col, register_col = st.columns([1, 1])

            with login_col:
                if st.button("Login"):
                    if username and password:
                        if verify_user(username, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.error("Please fill in all fields")

            with register_col:
                if st.button("Create Account"):
                    st.session_state.show_register = True
                    st.rerun()

        else:
            # Registration form
            st.markdown(
                """
                <div class="login-header">
                    <h2>Create Your Account</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            reg_username = st.text_input("Choose a username")
            reg_email = st.text_input("Email address")
            reg_password = st.text_input("Create a password", type="password")
            reg_confirm = st.text_input("Confirm password", type="password")

            reg_col, back_col = st.columns([1, 1])

            with reg_col:
                if st.button("Register"):
                    if reg_username and reg_email and reg_password and reg_confirm:
                        if reg_password == reg_confirm:
                            if len(reg_password) >= 6:
                                success, message = register_user(
                                    reg_username, reg_password, reg_email
                                )
                                if success:
                                    st.success(message)
                                    st.session_state.show_register = False
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("Password must be at least 6 characters")
                        else:
                            st.error("Passwords don't match")
                    else:
                        st.error("Please fill in all fields")

            with back_col:
                if st.button("Back to Login"):
                    st.session_state.show_register = False
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # Close login-container
        st.markdown('</div>', unsafe_allow_html=True)  # Close full-page
        st.stop()


def logout():
    """Logout function"""
    for key in ["logged_in", "username", "show_register"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
