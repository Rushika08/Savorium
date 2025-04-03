import streamlit as st
import sqlite3
import random

def get_random_public_recipes(conn, limit=5):
    cursor = conn.cursor()
    
    # Fetch basic recipe details
    cursor.execute("""
        SELECT * FROM recipes
        WHERE visibility = 'Public'
        ORDER BY RANDOM()
        LIMIT ?;
    """, (limit,))
    recipes = cursor.fetchall()

    formatted_recipes = []

    for recipe in recipes:
        recipe_id = recipe["recipe_id"]
        user_id = recipe["user_id"]
        title = recipe["title"]
        description = recipe["description"]
        instructions = recipe["instructions"]
        visibility = recipe["visibility"]

        # Fetch ingredients for the current recipe
        cursor.execute("""
            SELECT i.name, ri.quantity, ri.unit 
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
            WHERE ri.recipe_id = ?;
        """, (recipe_id,))
        ingredients = cursor.fetchall()

        # Format ingredients
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append({
                "name": ingredient["name"],
                "quantity": ingredient["quantity"],
                "unit": ingredient["unit"]
            })

        # Fetch tags for the current recipe
        cursor.execute("""
            SELECT rt.tag_name 
            FROM recipe_tag_map rtm
            JOIN recipe_tags rt ON rtm.tag_id = rt.tag_id
            WHERE rtm.recipe_id = ?;
        """, (recipe_id,))
        tags = cursor.fetchall()

        # Format tags
        tag_list = [tag["tag_name"] for tag in tags]

        # Format the recipe data
        formatted_recipe = {
            "recipe_id": recipe_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "instructions": instructions,
            "ingredients": ingredient_list,
            "tags": tag_list,
            "visibility": visibility
        }

        formatted_recipes.append(formatted_recipe)

    cursor.close()
    return formatted_recipes

def search_public_recipes(conn, query):
    cursor = conn.cursor()
    search_query = f"%{query}%"
    
    # Fetch basic recipe details
    cursor.execute("""
        SELECT * FROM recipes
        WHERE visibility = 'Public' AND (title LIKE ? OR description LIKE ?);
    """, (search_query, search_query))
    recipes = cursor.fetchall()

    formatted_recipes = []

    for recipe in recipes:
        recipe_id = recipe["recipe_id"]
        user_id = recipe["user_id"]
        title = recipe["title"]
        description = recipe["description"]
        instructions = recipe["instructions"]
        visibility = recipe["visibility"]

        # Fetch ingredients for the current recipe
        cursor.execute("""
            SELECT i.name, ri.quantity, ri.unit 
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
            WHERE ri.recipe_id = ?;
        """, (recipe_id,))
        ingredients = cursor.fetchall()

        # Format ingredients
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append({
                "name": ingredient["name"],
                "quantity": ingredient["quantity"],
                "unit": ingredient["unit"]
            })

        # Fetch tags for the current recipe
        cursor.execute("""
            SELECT rt.tag_name 
            FROM recipe_tag_map rtm
            JOIN recipe_tags rt ON rtm.tag_id = rt.tag_id
            WHERE rtm.recipe_id = ?;
        """, (recipe_id,))
        tags = cursor.fetchall()

        # Format tags
        tag_list = [tag["tag_name"] for tag in tags]

        # Format the recipe data
        formatted_recipe = {
            "recipe_id": recipe_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "instructions": instructions,
            "ingredients": ingredient_list,
            "tags": tag_list,
            "visibility": visibility
        }

        formatted_recipes.append(formatted_recipe)

    cursor.close()
    return formatted_recipes

# Streamlit UI
st.title("Search for Public Recipes 🍽️")

# Database connection
conn = sqlite3.connect("recipes.db")
conn.row_factory = sqlite3.Row  # This allows us to access columns by name

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
        st.write("---")
else:
    st.warning("No public recipes available.")

# Close the database connection
conn.close()
