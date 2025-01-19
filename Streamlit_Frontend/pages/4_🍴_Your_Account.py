import streamlit as st
import sqlite3
import streamlit_authenticator as stauth
# from streamlit_authenticator.utilities.hasher import Hasher
import bcrypt

# Database setup
DATABASE = "recipes.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            hashed_password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT,
            ingredients TEXT,
            instructions TEXT,
            nutrition_values TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    conn.commit()
    conn.close()

# Insert user into database
def add_user(username, name, hashed_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, name, hashed_password) VALUES (?, ?, ?)
    """, (username, name, hashed_password))
    conn.commit()
    conn.close()

# Fetch recipes for a user
def get_recipes(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, ingredients, instructions, nutrition_values FROM recipes WHERE username=?
    """, (username,))
    recipes = cursor.fetchall()
    conn.close()
    return recipes

# Add a recipe to the database
def add_recipe(username, name, ingredients, instructions, nutrition_values):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipes (username, name, ingredients, instructions, nutrition_values)
        VALUES (?, ?, ?, ?, ?)
    """, (username, name, ingredients, instructions, nutrition_values))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Authentication setup
names = ["Admin"]
usernames = ["admin"]
passwords = ["password123"]

# Hash the passwords
# hashed_passwords = stauth.Hasher(passwords).generate()

# Create the authenticator object
authenticator = stauth.Authenticate(names, usernames, passwords, "auth_cookie", "auth_key", cookie_expiry_days=1)

# Streamlit page
st.set_page_config(page_title="Your Account", page_icon="🍴", layout="wide")

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.write(f"Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")

    # Recipe submission form
    st.title("Submit Your Recipe")

    with st.form("recipe_form"):
        recipe_name = st.text_input("Recipe Name", max_chars=50)
        ingredients = st.text_area("Ingredients (comma-separated)", height=100)
        instructions = st.text_area("Instructions (step-by-step)", height=150)
        nutrition_values = st.text_area("Nutritional Values (JSON format)", height=100)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if recipe_name and ingredients and instructions:
            add_recipe(username, recipe_name, ingredients, instructions, nutrition_values)
            st.success("Recipe submitted successfully!")
        else:
            st.error("All fields are required!")

    # View saved recipes
    st.title("Your Saved Recipes")
    recipes = get_recipes(username)
    if recipes:
        for recipe in recipes:
            with st.expander(recipe[0]):  # Recipe name as title
                st.write("**Ingredients:**")
                st.write(recipe[1])
                st.write("**Instructions:**")
                st.write(recipe[2])
                if recipe[3]:
                    st.write("**Nutritional Values:**")
                    st.json(eval(recipe[3]))
    else:
        st.info("No recipes found. Submit your first recipe!")
elif authentication_status is False:
    st.error("Username/password is incorrect.")
elif authentication_status is None:
    st.warning("Please enter your username and password to continue.")
