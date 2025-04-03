import sqlite3  # Assuming you're using SQLite for the database

# Directly establish the database connection
conn = sqlite3.connect('recipes.db')  # Use your actual database file path

# Fetch all recipes from the database
try:
    cursor = conn.cursor()  # Create a cursor object

    cursor.execute("SELECT recipe_id, title, description FROM recipes WHERE visibility = 'private' AND (title LIKE ? OR description LIKE ?);")
    result = cursor.fetchall()

    if result:
        # Display the fetched data if there are results
        print("Fetched Recipes:")
        for recipe in result:
            print(recipe)  # Print each recipe
    else:
        print("No recipes found.")

    cursor.close()  # Explicitly close the cursor after use
except Exception as e:
    print(f"Database error: {e}")
    result = []

# Close the connection when done
conn.close()
