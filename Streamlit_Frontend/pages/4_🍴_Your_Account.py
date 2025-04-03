import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_functions import *
# from ..db_functions import *
import streamlit_authenticator as stauth
import secrets

# Streamlit page setup
st.set_page_config(page_title="My profile", page_icon="👨‍💼", layout="wide")

# Open the database connection
conn = get_db_connection()

# Fetch credentials from the database
credentials = get_user_credentials(conn)

# Setup authentication
authenticator = stauth.Authenticate(
    credentials,
    "savorium_cookie",  # Cookie name
    secrets.token_hex(16),  # Generates a secure 32-character key
    1              # Expiry days
)

def register_user(username, password, email, name, role="user"):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, email, nickname, role) 
            VALUES (?, ?, ?, ?, ?);
        """, (username, password, email, name, role))
        
        conn.commit()
        st.success("✅ User registered successfully! You can now log in.")
    except sqlite3.IntegrityError:
        st.error("⚠️ Username or Email already exists!")
    finally:
        cursor.close()

def create_ingredient_text(recipe):
    """Create a text string of ingredients for downloading"""
    lines = [f"Ingredients for {recipe['title']}:\n"]
    lines.append("=" * (len(lines[0]) - 1) + "\n\n")
    
    for ingredient in recipe['ingredients']:
        lines.append(f"- {ingredient['quantity']} {ingredient['unit']} {ingredient['name']}\n")
    
    return "".join(lines)

auth_mode = None

if not st.session_state['authentication_status']:
    # Toggle between Login & Register
    auth_mode = st.radio("Choose an option:", ["Login", "Register"])

if auth_mode == "Register":
    st.subheader("📝 Register as a New User")
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        # role = st.selectbox("Role", ["user", "admin"])

        submit = st.form_submit_button("Register")

    if submit:
        if password != confirm_password:
            st.error("❌ Passwords do not match!")
        elif not username or not email or not password:
            st.error("⚠️ Please fill in all fields!")
        else:
            register_user(username, password, email, name, role="user")

else:
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    # main_option = st.sidebar.radio("Choose an option:", ["🍽️ Recipes", "📊 Other Option"])
    # Main application logic
    if st.session_state['authentication_status']:
        authenticator.logout()
        st.subheader(f'Welcome *{st.session_state["name"]}*', divider=True)

        # Main navigation options
        main_option = st.sidebar.radio("Choose an Option:", ["📖 Manage Recipes", "🔧 Search Recipes"], horizontal=True)

        if main_option == "📖 Manage Recipes":
            # --- 🎯 Show Tabs After Login ---
            # tab1, tab2, tab3, tab4 = st.tabs(["📜 My Recipes", "➕ Add Recipe", "⭐ Favorites", "⚙️ Manage Account"])
            tab1, tab2, tab3 = st.tabs(["📜 My Recipes", "➕ Add Recipe", "⭐ Favorites"])

            with tab1:
                st.header("📜 Your Recipes")
                st.write("Here you can see all the recipes you've added.")

                # Fetch user ID and recipes
                user_id = get_user_id(conn, st.session_state["username"])
                recipes = get_user_recipes(conn, user_id)

                if not recipes:
                    st.write("No recipes found.")
                else:
                    for recipe in recipes:
                        # Create a container for each recipe
                        with st.container():
                            col1, col2 = st.columns([4, 1])  # Split the row into two columns
                            
                            with col1:
                                # Display recipe details in an expander
                                with st.expander(recipe["title"]):
                                    st.subheader("Recipe ID:")
                                    st.write(recipe["recipe_id"])

                                    st.subheader("Description:")
                                    st.write(recipe["description"])
                                    
                                    st.subheader("Instructions:")
                                    st.write(recipe["instructions"])
                                    
                                    st.subheader("Ingredients:")
                                    for ingredient in recipe["ingredients"]:
                                        st.write(f"- {ingredient['name']} ({ingredient['quantity']} {ingredient['unit']})")
                                    
                                    st.subheader("Tags:")
                                    st.write(", ".join(recipe["tags"]))  # Display tags as comma-separated

                                    st.subheader("Visibility:")
                                    st.write(recipe["visibility"])

                                    # Download button for ingredients
                                    ingredient_text = create_ingredient_text(recipe)
                                    st.download_button(
                                        label="📥 Download Ingredients",
                                        data=ingredient_text,
                                        file_name=f"{recipe['title']}_ingredients.txt",
                                        mime="text/plain",
                                        key=f"download_{recipe['recipe_id']}_myrecipes"
                                    )

                            with col2:
                                recipe_id = recipe['recipe_id']
                                if recipe_id is not None:
                                    if st.button(f"Delete {recipe['title']}", key=f"delete_{recipe_id}"):
                                        delete_recipe(conn, recipe_id)
                                        st.success(f"Recipe '{recipe['title']}' deleted successfully!")
                                        st.rerun()
                                else:
                                    st.warning(f"Recipe ID missing for {recipe['title']}. Unable to delete.")

                        st.write("---")  # Divider between recipes


            with tab2:
                st.header("➕ Add a New Recipe")
                with st.form("add_recipe_form"):
                    title = st.text_input("Recipe Title")
                    description = st.text_area("Recipe Description")
                    instructions = st.text_area("Recipe Instructions")
                    visibility = st.radio("👀 Visibility", ["Public", "Private"], horizontal=True)
                    
                    # Ingredients section
                    ingredient_list = []
                    unit_options = ["grams", "kg", "cups", "tbsp", "tsp", "ml", "liters", "pieces"]
                    ingredient_count = st.session_state.get("ingredient_count", 1)

                    for i in range(ingredient_count):
                        col1, col2, col3 = st.columns([3, 2, 2])
                        with col1:
                            ingredient_name = st.text_input(f"Ingredient {i+1} Name", key=f"ingredient_{i}_name")
                        with col2:
                            unit = st.selectbox(f"Unit {i+1}", unit_options, key=f"ingredient_{i}_unit")
                        with col3:
                            quantity = st.number_input(f"Quantity {i+1}", min_value=0.1, step=0.1, key=f"ingredient_{i}_quantity")

                        ingredient_list.append((ingredient_name, unit, quantity))

                    # Buttons to add or remove ingredient fields dynamically
                    col_add, col_remove = st.columns([1, 1])
                    with col_add:
                        if st.form_submit_button("➕ Add Ingredient"):
                            st.session_state["ingredient_count"] = ingredient_count + 1
                            st.rerun()
                    with col_remove:
                        if ingredient_count > 1 and st.form_submit_button("➖ Remove Last Ingredient"):
                            st.session_state["ingredient_count"] = ingredient_count - 1
                            st.rerun()

                    # Tags section
                    available_tags = get_all_tags(conn)
                    tags = st.multiselect("🏷️ Select Tags", available_tags, help="Choose relevant tags for your recipe")

                    # Option to add custom tags
                    custom_tag = st.text_input("🔖 Add Custom Tag")
                    addcustomtag = st.form_submit_button("➕ Add Custom Tag")

                    if custom_tag and addcustomtag:
                        if custom_tag not in tags:
                            tags.append(custom_tag)
                            st.success(f"Added custom tag: {custom_tag}")

                    for tag in tags:
                        st.write(f"- {tag}")

                    add_recipe_btn = st.form_submit_button("Add Recipe")

                if add_recipe_btn:
                    if not title or not description or not instructions or not visibility or not ingredient_list:
                        st.error("⚠️ Please fill in all fields!")
                    else:
                        user_id = get_user_id(conn, st.session_state["username"])
                        
                        # Ensure custom tags are added to the database
                        for tag in tags:
                            add_tag(conn, tag)  # Add the tag to the database if it doesn't exist

                        # Add the recipe
                        add_recipe(conn, user_id, title, description, instructions, ingredient_list, tags, visibility)
                        
                        st.success("✅ Recipe added successfully!")
                        st.rerun()

            with tab3:
                st.header("⭐ Favourite Recipes")
                st.write("Here you can see all your favorite recipes you've saved.")

                # Fetch user ID and recipes
                user_id = get_user_id(conn, st.session_state["username"])
                recipes = get_favorites(conn, user_id)

                if not recipes:
                    st.write("No recipes found.")
                else:
                    for recipe in recipes:
                        # Create a container for each recipe
                        with st.container():
                            col1, col2 = st.columns([4, 1])  # Split the row into two columns
                            
                            with col1:
                                # Display recipe details in an expander
                                with st.expander(recipe["title"]):
                                    st.subheader("Recipe ID:")
                                    st.write(recipe["recipe_id"])

                                    st.subheader("Description:")
                                    st.write(recipe["description"])
                                    
                                    st.subheader("Instructions:")
                                    st.write(recipe["instructions"])
                                    
                                    st.subheader("Ingredients:")
                                    for ingredient in recipe["ingredients"]:
                                        st.write(f"- {ingredient['name']} ({ingredient['quantity']} {ingredient['unit']})")
                                    
                                    st.subheader("Tags:")
                                    st.write(", ".join(recipe["tags"]))  # Display tags as comma-separated

                                    # Download button for ingredients
                                    ingredient_text = create_ingredient_text(recipe)
                                    st.download_button(
                                        label="📥 Download Ingredients",
                                        data=ingredient_text,
                                        file_name=f"{recipe['title']}_ingredients.txt",
                                        mime="text/plain",
                                        key=f"download_{recipe['recipe_id']}_favorites"
                                    )

                            with col2:
                                recipe_id = recipe['recipe_id']
                                if recipe_id is not None:
                                    if st.button(f"Delete {recipe['title']}", key=f"delete_{recipe_id}"):
                                        delete_recipe(conn, recipe_id)
                                        st.success(f"Recipe '{recipe['title']}' deleted successfully!")
                                        st.rerun()
                                else:
                                    st.warning(f"Recipe ID missing for {recipe['title']}. Unable to delete.")

                        st.write("---")  # Divider between recipes

        else:
            st.header("🔧 Search Recipes")
            conn.row_factory = sqlite3.Row
            
            # Search functionality
            search_query = st.text_input("Search for a recipe:")

            if search_query:
                search_results = search_public_recipes(conn, search_query)

                if search_results:
                    st.subheader("Search Results")
                    for recipe in search_results:
                        with st.expander(f"🍴 {recipe['title']}"):
                            st.markdown(f"**Description:** {recipe['description']}")
                            
                            st.markdown("**Ingredients:**")
                            for ingredient in recipe['ingredients']:
                                st.write(f"- {ingredient['quantity']} {ingredient['unit']} {ingredient['name']}")
                            
                            st.markdown("**Instructions:**")
                            st.write(recipe['instructions'])
                            
                            if recipe['tags']:
                                st.markdown("**Tags:** " + ", ".join(recipe['tags']))
                            
                            st.markdown(f"*Posted by user ID: {recipe['user_id']}*")
                            
                            # Download button for ingredients
                            ingredient_text = create_ingredient_text(recipe)
                            st.download_button(
                                label="📥 Download Ingredients",
                                data=ingredient_text,
                                file_name=f"{recipe['title']}_ingredients.txt",
                                mime="text/plain",
                                key=f"download_{recipe['recipe_id']}_search"
                            )
                        st.write("---")
                else:
                    st.warning("No matching recipes found.")

            # Show random recipes initially
            st.subheader("Featured Public Recipes")
            random_recipes = get_random_public_recipes(conn)

            if random_recipes:
                for recipe in random_recipes:
                    with st.expander(f"⭐ {recipe['title']}"):
                        st.markdown(f"**Description:** {recipe['description']}")
                        
                        st.markdown("**Ingredients:**")
                        for ingredient in recipe['ingredients']:
                            st.write(f"- {ingredient['quantity']} {ingredient['unit']} {ingredient['name']}")
                        
                        st.markdown("**Instructions:**")
                        st.write(recipe['instructions'])
                        
                        if recipe['tags']:
                            st.markdown("**Tags:** " + ", ".join(recipe['tags']))
                        
                        st.markdown(f"*Posted by user ID: {recipe['user_id']}*")
                        
                        # Download button for ingredients
                        ingredient_text = create_ingredient_text(recipe)
                        st.download_button(
                            label="📥 Download Ingredients",
                            data=ingredient_text,
                            file_name=f"{recipe['title']}_ingredients.txt",
                            mime="text/plain",
                            key=f"download_{recipe['recipe_id']}_featured"
                        )
                    st.write("---")
            else:
                st.warning("No public recipes available.")


    elif st.session_state['authentication_status'] == None:
        st.warning('Please enter your username and password')
    else:
        st.error('Username/password is incorrect')

# Close the connection when the app is done
conn.close()

# import streamlit as st
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from db_functions import *
# # from ..db_functions import *
# import streamlit_authenticator as stauth
# import secrets

# # Streamlit page setup
# st.set_page_config(page_title="My profile", page_icon="👨‍💼", layout="wide")

# # Open the database connection
# conn = get_db_connection()

# # Fetch credentials from the database
# credentials = get_user_credentials(conn)

# # Setup authentication
# authenticator = stauth.Authenticate(
#     credentials,
#     "savorium_cookie",  # Cookie name
#     secrets.token_hex(16),  # Generates a secure 32-character key
#     1              # Expiry days
# )

# def register_user(username, password, email, name, role="user"):
#     cursor = conn.cursor()
#     try:
#         cursor.execute("""
#             INSERT INTO users (username, password, email, nickname, role) 
#             VALUES (?, ?, ?, ?, ?);
#         """, (username, password, email, name, role))
        
#         conn.commit()
#         st.success("✅ User registered successfully! You can now log in.")
#     except sqlite3.IntegrityError:
#         st.error("⚠️ Username or Email already exists!")
#     finally:
#         cursor.close()

# auth_mode = None

# if not st.session_state['authentication_status']:
#     # Toggle between Login & Register
#     auth_mode = st.radio("Choose an option:", ["Login", "Register"])

# if auth_mode == "Register":
#     st.subheader("📝 Register as a New User")
#     with st.form("register_form"):
#         username = st.text_input("Username")
#         email = st.text_input("Email")
#         name = st.text_input("Name")
#         password = st.text_input("Password", type="password")
#         confirm_password = st.text_input("Confirm Password", type="password")
#         # role = st.selectbox("Role", ["user", "admin"])

#         submit = st.form_submit_button("Register")

#     if submit:
#         if password != confirm_password:
#             st.error("❌ Passwords do not match!")
#         elif not username or not email or not password:
#             st.error("⚠️ Please fill in all fields!")
#         else:
#             register_user(username, password, email, name, role="user")

# else:
#     try:
#         authenticator.login()
#     except Exception as e:
#         st.error(e)

#     # main_option = st.sidebar.radio("Choose an option:", ["🍽️ Recipes", "📊 Other Option"])
#     # Main application logic
#     if st.session_state['authentication_status']:
#         authenticator.logout()
#         st.subheader(f'Welcome *{st.session_state["name"]}*', divider=True)

#         # Main navigation options
#         main_option = st.sidebar.radio("Choose an Option:", ["📖 Manage Recipes", "🔧 Other Feature"], horizontal=True)

#         if main_option == "📖 Manage Recipes":
#             # --- 🎯 Show Tabs After Login ---
#             tab1, tab2, tab3, tab4 = st.tabs(["📜 My Recipes", "➕ Add Recipe", "⭐ Favorites", "⚙️ Manage Account"])

#             with tab1:
#                 st.header("📜 Your Recipes")
#                 st.write("Here you can see all the recipes you've added.")

#                 # Fetch user ID and recipes
#                 user_id = get_user_id(conn, st.session_state["username"])
#                 recipes = get_user_recipes(conn, user_id)

#                 if not recipes:
#                     st.write("No recipes found.")
#                 else:
#                     for recipe in recipes:
#                         # Create a container for each recipe
#                         with st.container():
#                             col1, col2 = st.columns([4, 1])  # Split the row into two columns
                            
#                             with col1:
#                                 # Display recipe details in an expander
#                                 with st.expander(recipe["title"]):
#                                     st.subheader("Recipe ID:")
#                                     st.write(recipe["recipe_id"])

#                                     st.subheader("Description:")
#                                     st.write(recipe["description"])
                                    
#                                     st.subheader("Instructions:")
#                                     st.write(recipe["instructions"])
                                    
#                                     st.subheader("Ingredients:")
#                                     for ingredient in recipe["ingredients"]:
#                                         st.write(f"- {ingredient['name']} ({ingredient['quantity']} {ingredient['unit']})")
                                    
#                                     st.subheader("Tags:")
#                                     st.write(", ".join(recipe["tags"]))  # Display tags as comma-separated

#                                     st.subheader("Visibility:")
#                                     st.write(recipe["visibility"])

#                             with col2:
#                                 recipe_id = recipe['recipe_id']
#                                 if recipe_id is not None:
#                                     if st.button(f"Delete {recipe['title']}", key=f"delete_{recipe_id}"):
#                                         delete_recipe(conn, recipe_id)
#                                         st.success(f"Recipe '{recipe['title']}' deleted successfully!")
#                                         st.rerun()
#                                 else:
#                                     st.warning(f"Recipe ID missing for {recipe['title']}. Unable to delete.")

#                         st.write("---")  # Divider between recipes


#             with tab2:
#                 st.header("➕ Add a New Recipe")
#                 with st.form("add_recipe_form"):
#                     title = st.text_input("Recipe Title")
#                     description = st.text_area("Recipe Description")
#                     instructions = st.text_area("Recipe Instructions")
#                     visibility = st.radio("👀 Visibility", ["Public", "Private"], horizontal=True)
                    
#                     # Ingredients section
#                     ingredient_list = []
#                     unit_options = ["grams", "kg", "cups", "tbsp", "tsp", "ml", "liters", "pieces"]
#                     ingredient_count = st.session_state.get("ingredient_count", 1)

#                     for i in range(ingredient_count):
#                         col1, col2, col3 = st.columns([3, 2, 2])
#                         with col1:
#                             ingredient_name = st.text_input(f"Ingredient {i+1} Name", key=f"ingredient_{i}_name")
#                         with col2:
#                             unit = st.selectbox(f"Unit {i+1}", unit_options, key=f"ingredient_{i}_unit")
#                         with col3:
#                             quantity = st.number_input(f"Quantity {i+1}", min_value=0.1, step=0.1, key=f"ingredient_{i}_quantity")

#                         ingredient_list.append((ingredient_name, unit, quantity))

#                     # Buttons to add or remove ingredient fields dynamically
#                     col_add, col_remove = st.columns([1, 1])
#                     with col_add:
#                         if st.form_submit_button("➕ Add Ingredient"):
#                             st.session_state["ingredient_count"] = ingredient_count + 1
#                             st.rerun()
#                     with col_remove:
#                         if ingredient_count > 1 and st.form_submit_button("➖ Remove Last Ingredient"):
#                             st.session_state["ingredient_count"] = ingredient_count - 1
#                             st.rerun()

#                     # Tags section
#                     available_tags = get_all_tags(conn)
#                     tags = st.multiselect("🏷️ Select Tags", available_tags, help="Choose relevant tags for your recipe")

#                     # Option to add custom tags
#                     custom_tag = st.text_input("🔖 Add Custom Tag")
#                     addcustomtag = st.form_submit_button("➕ Add Custom Tag")

#                     if custom_tag and addcustomtag:
#                         if custom_tag not in tags:
#                             tags.append(custom_tag)
#                             st.success(f"Added custom tag: {custom_tag}")

#                     for tag in tags:
#                         st.write(f"- {tag}")

#                     add_recipe_btn = st.form_submit_button("Add Recipe")

#                 if add_recipe_btn:
#                     if not title or not description or not instructions or not visibility or not ingredient_list:
#                         st.error("⚠️ Please fill in all fields!")
#                     else:
#                         user_id = get_user_id(conn, st.session_state["username"])
                        
#                         # Ensure custom tags are added to the database
#                         for tag in tags:
#                             add_tag(conn, tag)  # Add the tag to the database if it doesn't exist

#                         # Add the recipe
#                         add_recipe(conn, user_id, title, description, instructions, ingredient_list, tags, visibility)
                        
#                         st.success("✅ Recipe added successfully!")

#             with tab3:
#                 st.header("⭐ Favourite Recipes")
#                 st.write("Here you can see all your favorite recipes you've saved.")

#                 # Fetch user ID and recipes
#                 user_id = get_user_id(conn, st.session_state["username"])
#                 recipes = get_favorites(conn, user_id)

#                 if not recipes:
#                     st.write("No recipes found.")
#                 else:
#                     for recipe in recipes:
#                         # Create a container for each recipe
#                         with st.container():
#                             col1, col2 = st.columns([4, 1])  # Split the row into two columns
                            
#                             with col1:
#                                 # Display recipe details in an expander
#                                 with st.expander(recipe["title"]):
#                                     st.subheader("Recipe ID:")
#                                     st.write(recipe["recipe_id"])

#                                     st.subheader("Description:")
#                                     st.write(recipe["description"])
                                    
#                                     st.subheader("Instructions:")
#                                     st.write(recipe["instructions"])
                                    
#                                     st.subheader("Ingredients:")
#                                     for ingredient in recipe["ingredients"]:
#                                         st.write(f"- {ingredient['name']} ({ingredient['quantity']} {ingredient['unit']})")
                                    
#                                     st.subheader("Tags:")
#                                     st.write(", ".join(recipe["tags"]))  # Display tags as comma-separated

#                                     # st.subheader("Visibility:")
#                                     # st.write(recipe["visibility"])

#                             with col2:
#                                 recipe_id = recipe['recipe_id']
#                                 if recipe_id is not None:
#                                     if st.button(f"Delete {recipe['title']}", key=f"delete_{recipe_id}"):
#                                         delete_recipe(conn, recipe_id)
#                                         st.success(f"Recipe '{recipe['title']}' deleted successfully!")
#                                         st.rerun()
#                                 else:
#                                     st.warning(f"Recipe ID missing for {recipe['title']}. Unable to delete.")

#                         st.write("---")  # Divider between recipes

#         else:
#             st.header("🔧 Other Feature")
#             conn.row_factory = sqlite3.Row
            
#             # Search functionality
#             search_query = st.text_input("Search for a recipe:")

#             if search_query:
#                 search_results = search_public_recipes(conn, search_query)

#                 if search_results:
#                     st.subheader("Search Results")
#                     for recipe in search_results:
#                         with st.expander(f"🍴 {recipe['title']}"):
#                             st.markdown(f"**Description:** {recipe['description']}")
                            
#                             st.markdown("**Ingredients:**")
#                             for ingredient in recipe['ingredients']:
#                                 st.write(f"- {ingredient['quantity']} {ingredient['unit']} {ingredient['name']}")
                            
#                             st.markdown("**Instructions:**")
#                             st.write(recipe['instructions'])
                            
#                             if recipe['tags']:
#                                 st.markdown("**Tags:** " + ", ".join(recipe['tags']))
                            
#                             st.markdown(f"*Posted by user ID: {recipe['user_id']}*")
#                         st.write("---")
#                 else:
#                     st.warning("No matching recipes found.")

#             # Show random recipes initially
#             st.subheader("Featured Public Recipes")
#             random_recipes = get_random_public_recipes(conn)

#             if random_recipes:
#                 for recipe in random_recipes:
#                     with st.expander(f"⭐ {recipe['title']}"):
#                         st.markdown(f"**Description:** {recipe['description']}")
                        
#                         st.markdown("**Ingredients:**")
#                         for ingredient in recipe['ingredients']:
#                             st.write(f"- {ingredient['quantity']} {ingredient['unit']} {ingredient['name']}")
                        
#                         st.markdown("**Instructions:**")
#                         st.write(recipe['instructions'])
                        
#                         if recipe['tags']:
#                             st.markdown("**Tags:** " + ", ".join(recipe['tags']))
                        
#                         st.markdown(f"*Posted by user ID: {recipe['user_id']}*")
#                     st.write("---")
#             else:
#                 st.warning("No public recipes available.")


#     elif st.session_state['authentication_status'] == None:
#         st.warning('Please enter your username and password')
#     else:
#         st.error('Username/password is incorrect')

# # Close the connection when the app is done
# conn.close()