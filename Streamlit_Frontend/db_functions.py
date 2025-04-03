import sqlite3
import threading

# Initialize database
DATABASE = "recipes.db"

# Create a thread-local storage for database connections
thread_local = threading.local()

def get_db_connection():
    # Check if the current thread already has a connection
    if not hasattr(thread_local, "connection"):
        # Create a new connection for this thread
        thread_local.connection = sqlite3.connect(DATABASE, check_same_thread=False)
        thread_local.connection.row_factory = sqlite3.Row  # Enables fetching results as dictionaries
    return thread_local.connection

# Function to retrieve user credentials from the database
def get_user_credentials(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, email, nickname, role FROM users")
    users = cursor.fetchall()

    credentials = {
        "usernames": {
            user[0]: {
                "email": user[2],
                "name": user[3],
                "password": user[1],
                "role": user[4]
            }
            for user in users
        }
    }
    return credentials

# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)  # Creates or opens the database file
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(10) NOT NULL UNIQUE,
            password VARCHAR(15) NOT NULL,
            nickname VARCHAR(10),
            email VARCHAR(30) NOT NULL UNIQUE,
            role VARCHAR(10) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Recipes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(50) NOT NULL,
            description VARCHAR(4000),
            instructions VARCHAR(4000),
            visibility VARCHAR(10) NOT NULL CHECK (visibility IN ('Public', 'Private', 'Friends')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)

    # Ingredients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Recipe_Ingredients Table (Many-to-Many Relationship)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity VARCHAR(50),
            unit VARCHAR(50),
            PRIMARY KEY (recipe_id, ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE
        );
    """)

    # Recipe_Tags Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name VARCHAR(10) NOT NULL UNIQUE
        );
    """)

    # Recipe_Tag_Map Table (Many-to-Many Relationship)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_tag_map (
            recipe_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (recipe_id, tag_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES recipe_tags(tag_id) ON DELETE CASCADE
        );
    """)

    # Favourites Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, recipe_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Function to create a new user
def create_user(conn, username, password, nickname, email, role="user"):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, nickname, email, role) 
            VALUES (?, ?, ?, ?, ?);
        """, (username, password, nickname, email, role))
        conn.commit()
        print("User created successfully!")
    except sqlite3.IntegrityError:
        print("Error: Username or email already exists.")
    finally:
        cursor.close()

# Function to get a user by username
def get_user(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

# Function to get user ID by username
def get_user_id(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id_row = cursor.fetchone()
    cursor.close()
    return user_id_row[0] if user_id_row else None

# Function to add a recipe
def add_recipe(conn, user_id, title, description, instructions, ingredients=[], tags=[], visibility="public"):
    cursor = conn.cursor()

    try:
        # Insert the recipe
        cursor.execute("""
            INSERT INTO recipes (user_id, title, description, instructions, visibility) 
            VALUES (?, ?, ?, ?, ?);
        """, (user_id, title, description, instructions, visibility))

        # Get the recipe_id of the newly added recipe
        recipe_id = cursor.lastrowid

        # Add ingredients to the recipe
        for ingredient in ingredients:
            name, unit, quantity = ingredient
            add_ingredient(conn, name)  # Add ingredient if it doesn't exist
            ingredient_id = cursor.execute("SELECT ingredient_id FROM ingredients WHERE name = ?", (name,)).fetchone()[0]
            add_recipe_ingredient(conn, recipe_id, ingredient_id, quantity, unit)  # Link ingredient to recipe

        # Add tags to the recipe
        for tag in tags:
            add_tag(conn, tag)  # Add tag if it doesn't exist
            tag_id = cursor.execute("SELECT tag_id FROM recipe_tags WHERE tag_name = ?", (tag,)).fetchone()[0]
            add_recipe_tag(conn, recipe_id, tag_id)  # Link tag to recipe
        
        conn.commit()
        print("Recipe added successfully!")
    
    except Exception as e:
        conn.rollback()
        print(f"Error adding recipe: {e}")
    
    finally:
        cursor.close()

# Function to add an ingredient
def add_ingredient(conn, name):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?);", (name,))
        conn.commit()
    except Exception as e:
        print(f"Error adding ingredient: {e}")
    finally:
        cursor.close()

# Function to link an ingredient to a recipe
def add_recipe_ingredient(conn, recipe_id, ingredient_id, quantity, unit):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
            VALUES (?, ?, ?, ?);
        """, (recipe_id, ingredient_id, quantity, unit))
        conn.commit()
    except Exception as e:
        print(f"Error linking ingredient to recipe: {e}")
    finally:
        cursor.close()

# Function to add a tag
def add_tag(conn, tag_name):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO recipe_tags (tag_name) VALUES (?);", (tag_name,))
        conn.commit()
    except Exception as e:
        print(f"Error adding tag: {e}")
    finally:
        cursor.close()

# Function to link a tag to a recipe
def add_recipe_tag(conn, recipe_id, tag_id):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO recipe_tag_map (recipe_id, tag_id)
            VALUES (?, ?);
        """, (recipe_id, tag_id))
        conn.commit()
    except Exception as e:
        print(f"Error linking tag to recipe: {e}")
    finally:
        cursor.close()

# Function to get all public recipes
def get_public_recipes(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE visibility = 'public';")
    recipes = cursor.fetchall()
    cursor.close()
    return recipes

# Function to get all recipes of a user
def get_user_recipes(conn, user_id):
    cursor = conn.cursor()

    # Fetch basic recipe details
    cursor.execute("SELECT * FROM recipes WHERE user_id = ?", (user_id,))
    recipes = cursor.fetchall()

    formatted_recipes = []

    for recipe in recipes:
        recipe_id = recipe["recipe_id"]
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

# Function to delete a recipe
def delete_recipe(conn, recipe_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recipes WHERE recipe_id = ?", (recipe_id,))
    conn.commit()
    cursor.close()
    print("Recipe deleted successfully!")

# Function to get all tags
def get_all_tags(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT tag_name FROM recipe_tags;")  # Fetch only the tag_name column
    tags = cursor.fetchall()
    cursor.close()

    # Convert sqlite3.Row objects to a list of tag names
    tag_names = [tag["tag_name"] for tag in tags]
    return tag_names

# Function to get tags for a recipe
def get_recipe_tags(conn, recipe_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rt.tag_name 
        FROM recipe_tag_map rtm
        JOIN recipe_tags rt ON rtm.tag_id = rt.tag_id
        WHERE rtm.recipe_id = ?;
    """, (recipe_id,))
    tags = cursor.fetchall()
    cursor.close()
    return tags

# Function to add a recipe to favorites
# def add_favorite(conn, user_id, recipe_id):
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO favourites (user_id, recipe_id) 
#         VALUES (?, ?);
#     """, (user_id, recipe_id))
#     conn.commit()
#     cursor.close()
#     print("Recipe added to favorites!")

# Function to add a recipe to a user's favorites
def add_favorite(conn, user_id, recipe_id):
    cursor = conn.cursor()

    # Check if the recipe is already in favorites
    cursor.execute("""
        SELECT 1 FROM favourites WHERE user_id = ? AND recipe_id = ?;
    """, (user_id, recipe_id))
    
    if cursor.fetchone():
        cursor.close()
        return {"message": "Recipe is already in favorites."}

    # Insert the favorite recipe entry
    cursor.execute("""
        INSERT INTO favourites (user_id, recipe_id) VALUES (?, ?);
    """, (user_id, recipe_id))

    conn.commit()
    cursor.close()
    return {"message": "Recipe added to favorites successfully."}

# Function to remove a recipe from a user's favorites
def remove_favorite(conn, user_id, recipe_id):
    cursor = conn.cursor()

    # Check if the recipe exists in favorites
    cursor.execute("""
        SELECT 1 FROM favourites WHERE user_id = ? AND recipe_id = ?;
    """, (user_id, recipe_id))

    if not cursor.fetchone():
        cursor.close()
        return {"message": "Recipe not found in favorites."}

    # Delete the favorite recipe entry
    cursor.execute("""
        DELETE FROM favourites WHERE user_id = ? AND recipe_id = ?;
    """, (user_id, recipe_id))

    conn.commit()
    cursor.close()
    return {"message": "Recipe removed from favorites successfully."}

# Function to get favorites for a user
# Function to get all favorite recipes of a user
def get_favorites(conn, user_id):
    cursor = conn.cursor()

    # Fetch favorite recipes for the user
    cursor.execute("""
        SELECT r.recipe_id, r.title, r.description, r.instructions, r.visibility 
        FROM favourites f
        JOIN recipes r ON f.recipe_id = r.recipe_id
        WHERE f.user_id = ?;
    """, (user_id,))
    favorite_recipes = cursor.fetchall()

    formatted_favorites = []

    for recipe in favorite_recipes:
        recipe_id = recipe["recipe_id"]
        title = recipe["title"]
        description = recipe["description"]
        instructions = recipe["instructions"]
        visibility = recipe["visibility"]

        # Fetch ingredients for the favorite recipe
        cursor.execute("""
            SELECT i.name, ri.quantity, ri.unit 
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
            WHERE ri.recipe_id = ?;
        """, (recipe_id,))
        ingredients = cursor.fetchall()

        # Format ingredients
        ingredient_list = [
            {"name": ingredient["name"], "quantity": ingredient["quantity"], "unit": ingredient["unit"]}
            for ingredient in ingredients
        ]

        # Fetch tags for the favorite recipe
        cursor.execute("""
            SELECT rt.tag_name 
            FROM recipe_tag_map rtm
            JOIN recipe_tags rt ON rtm.tag_id = rt.tag_id
            WHERE rtm.recipe_id = ?;
        """, (recipe_id,))
        tags = cursor.fetchall()

        # Format tags
        tag_list = [tag["tag_name"] for tag in tags]

        # Format the favorite recipe data
        formatted_recipe = {
            "recipe_id": recipe_id,
            "title": title,
            "description": description,
            "instructions": instructions,
            "ingredients": ingredient_list,
            "tags": tag_list,
            "visibility": visibility
        }

        formatted_favorites.append(formatted_recipe)

    cursor.close()
    return formatted_favorites

# Function to update recipe visibility
def update_recipe_visibility(conn, recipe_id, visibility):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recipes 
        SET visibility = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE recipe_id = ?;
    """, (visibility, recipe_id))
    conn.commit()
    cursor.close()
    print("Recipe visibility updated!")

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

# conn = get_db_connection()
# print(get_all_tags(conn))