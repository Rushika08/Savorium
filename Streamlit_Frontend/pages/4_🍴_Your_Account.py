# import streamlit as st
# import sqlite3
# import streamlit_authenticator as stauth
# # from streamlit_authenticator.utilities.hasher import Hasher
# import bcrypt

# # Database setup
# DATABASE = "recipes.db"

# # Initialize database
# def init_db():
#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             username TEXT PRIMARY KEY,
#             name TEXT,
#             hashed_password TEXT
#         )
#     """)
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS recipes (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT,
#             name TEXT,
#             ingredients TEXT,
#             instructions TEXT,
#             nutrition_values TEXT,
#             FOREIGN KEY (username) REFERENCES users(username)
#         )
#     """)
#     conn.commit()
#     conn.close()

# # Insert user into database
# def add_user(username, name, hashed_password):
#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO users (username, name, hashed_password) VALUES (?, ?, ?)
#     """, (username, name, hashed_password))
#     conn.commit()
#     conn.close()

# # Fetch recipes for a user
# def get_recipes(username):
#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT name, ingredients, instructions, nutrition_values FROM recipes WHERE username=?
#     """, (username,))
#     recipes = cursor.fetchall()
#     conn.close()
#     return recipes

# # Add a recipe to the database
# def add_recipe(username, name, ingredients, instructions, nutrition_values):
#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO recipes (username, name, ingredients, instructions, nutrition_values)
#         VALUES (?, ?, ?, ?, ?)
#     """, (username, name, ingredients, instructions, nutrition_values))
#     conn.commit()
#     conn.close()

# # Initialize the database
# init_db()

# # Authentication setup
# names = ["Admin"]
# usernames = ["admin"]
# passwords = ["password123"]

# # Hash the passwords
# # hashed_passwords = stauth.Hasher(passwords).generate()

# # Create the authenticator object
# # authenticator = stauth.Authenticate(names, usernames, passwords, "auth_cookie", "auth_key", cookie_expiry_days=1)

# authenticator = stauth.Authenticate(
#     names=names,
#     usernames=usernames,
#     passwords=passwords,
#     cookie_name="auth_cookie",
#     key="auth_key",
#     cookie_expiry_days=1
# )


# # Streamlit page
# st.set_page_config(page_title="Your Account", page_icon="🍴", layout="wide")

# name, authentication_status, username = authenticator.login("Login", "main")

# if authentication_status:
#     st.sidebar.write(f"Welcome, {name}!")
#     authenticator.logout("Logout", "sidebar")

#     # Recipe submission form
#     st.title("Submit Your Recipe")

#     with st.form("recipe_form"):
#         recipe_name = st.text_input("Recipe Name", max_chars=50)
#         ingredients = st.text_area("Ingredients (comma-separated)", height=100)
#         instructions = st.text_area("Instructions (step-by-step)", height=150)
#         nutrition_values = st.text_area("Nutritional Values (JSON format)", height=100)
#         submitted = st.form_submit_button("Submit")

#     if submitted:
#         if recipe_name and ingredients and instructions:
#             add_recipe(username, recipe_name, ingredients, instructions, nutrition_values)
#             st.success("Recipe submitted successfully!")
#         else:
#             st.error("All fields are required!")

#     # View saved recipes
#     st.title("Your Saved Recipes")
#     recipes = get_recipes(username)
#     if recipes:
#         for recipe in recipes:
#             with st.expander(recipe[0]):  # Recipe name as title
#                 st.write("**Ingredients:**")
#                 st.write(recipe[1])
#                 st.write("**Instructions:**")
#                 st.write(recipe[2])
#                 if recipe[3]:
#                     st.write("**Nutritional Values:**")
#                     st.json(eval(recipe[3]))
#     else:
#         st.info("No recipes found. Submit your first recipe!")
# elif authentication_status is False:
#     st.error("Username/password is incorrect.")
# elif authentication_status is None:
#     st.warning("Please enter your username and password to continue.")


import yaml
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

# Streamlit page setup
st.set_page_config(page_title="Account", page_icon="🍴", layout="wide")

# Initialize database
DATABASE = "recipes.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create the users table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            roles TEXT -- Store roles as a comma-separated string
        )
    """)

    # Create the recipes table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            recipe_name TEXT,
            ingredients TEXT,
            instructions TEXT,
            nutrition_values TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()


def add_user(username, email, first_name, last_name, roles="editor"):
    """
    Adds a new user to the database. If the user already exists, it does nothing.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, email, first_name, last_name, roles)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, first_name, last_name, ','.join(roles)))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()


def add_recipe(username, recipe_name, ingredients, instructions, nutrition_values=None):
    """
    Adds a new recipe to the database associated with a user.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO recipes (username, recipe_name, ingredients, instructions, nutrition_values)
            VALUES (?, ?, ?, ?, ?)
        """, (username, recipe_name, ingredients, instructions, nutrition_values))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding recipe: {e}")
    finally:
        conn.close()


def get_recipes(username):
    """
    Retrieves all recipes associated with a specific user.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT recipe_name, ingredients, instructions, nutrition_values FROM recipes
            WHERE username = ?
        """, (username,))
        recipes = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving recipes: {e}")
        recipes = []
    finally:
        conn.close()
    return recipes


def get_user_id(username):
    """
    Retrieves the user ID for a given username.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT userid FROM users WHERE username = ?
        """, (username,))
        user_id = cursor.fetchone()
        return user_id[0] if user_id else None
    except sqlite3.Error as e:
        print(f"Error retrieving user ID: {e}")
        return None
    finally:
        conn.close()


def update_recipe(recipe_id, recipe_name=None, ingredients=None, instructions=None, nutrition_values=None):
    """
    Updates an existing recipe in the database.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        updates = []
        params = []

        if recipe_name:
            updates.append("recipe_name = ?")
            params.append(recipe_name)
        if ingredients:
            updates.append("ingredients = ?")
            params.append(ingredients)
        if instructions:
            updates.append("instructions = ?")
            params.append(instructions)
        if nutrition_values:
            updates.append("nutrition_values = ?")
            params.append(nutrition_values)

        params.append(recipe_id)
        query = f"UPDATE recipes SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating recipe: {e}")
    finally:
        conn.close()


def delete_recipe(recipe_id):
    """
    Deletes a recipe from the database.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM recipes WHERE id = ?
        """, (recipe_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting recipe: {e}")
    finally:
        conn.close()


def get_all_users():
    """
    Retrieves all users in the database.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT userid, username, email, first_name, last_name, roles FROM users
        """)
        users = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
        users = []
    finally:
        conn.close()
    return users


# Initialize the database
init_db()

# Load YAML configuration
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Add users from the YAML file to the database
for username, details in config.get('credentials', {}).get('usernames', {}).items():
    add_user(
        username=username,
        email=details.get('email', ''),
        first_name=details.get('first_name', ''),
        last_name=details.get('last_name', ''),
        roles=details.get('roles', [])
    )

# Streamlit Authenticator setup
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

# Main application logic
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')

    # Get the logged-in user's ID
    user_id = get_user_id(st.session_state["username"])
    username = st.session_state["username"]
    st.write(f"Your user name is: {username}")
    st.write(f"Your user ID is: {user_id}")
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
    st.write(f"Debug: Retrieved Recipes: {recipes}")  # Display fetched recipes
    if recipes:
        for recipe in recipes:
            with st.expander(recipe[0]):  # Recipe name as title
                st.write("**Ingredients:**")
                st.write(recipe[1])
                st.write("**Instructions:**")
                st.write(recipe[2])
                if recipe[3]:
                    st.write("**Nutritional Values:**")
                    try:
                        st.json(eval(recipe[3]))  # Safely parse JSON string
                    except:
                        st.write(recipe[3])  # Display raw string if parsing fails
    else:
        st.info("No recipes found. Submit your first recipe!")

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

# if st.button("Register"):
#     new_user = authenticator.register_user(
#         preauthorized=config.get("preauthorized", {}).get("emails", [])
#     )
#     if new_user:
#         st.success("Registration successful!")
#     else:
#         st.error("Registration failed. Email not preauthorized.")

# if authentication_status:
#     authenticator.logout("Logout", "sidebar")
#     st.sidebar.write(f"Welcome, {name}!")

#     # Ensure the user is added to the database
#     add_user(username, name)

    

# elif authentication_status is False:
#     st.error("Username/password is incorrect.")
# elif authentication_status is None:
#     st.warning("Please enter your username and password.")
