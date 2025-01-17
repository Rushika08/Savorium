import requests
import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import numpy as np
from keras.models import load_model

# # Load model and class names
# model = load_model("/app/model/keras_model.h5", compile=False)
# class_names = open("/app/model/labels.txt", "r").readlines()

# # Function to predict ingredient from an image
# def predict_ingredient(image):
#     size = (224, 224)
#     image = ImageOps.fit(image, size, Image.Resampling.LANCZOS).convert("RGB")
#     data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
#     normalized_image_array = (np.asarray(image).astype(np.float32) / 127.5) - 1
#     data[0] = normalized_image_array
#     prediction = model.predict(data)
#     index = np.argmax(prediction)
#     class_name = class_names[index].strip()
#     confidence_score = prediction[0][index]
#     return class_name, confidence_score

# # Tab 1: Image Recognition
# st.subheader("Image Recognition")
# uploaded_file = st.file_uploader("Upload an image of the ingredient", type=["jpg", "png", "jpeg"])

# if uploaded_file:
#     image = Image.open(uploaded_file)
#     st.image(image, caption="Uploaded Image", use_column_width=True)
#     if st.button("Predict Ingredient"):
#         class_name, confidence = predict_ingredient(image)
#         st.write(f"Model Suggestion: {class_name} (Confidence: {confidence:.2f})")
        
#         if st.button("Confirm", key="confirm_model"):
#             st.session_state.ingredients.append(class_name)
#             st.success(f"Added '{class_name}' to the ingredient list.")
#         elif st.button("Discard", key="discard_model"):
#             st.warning("Suggestion discarded.")

# # Page Configuration
# st.set_page_config(page_title="Recipe Finder by Ingredients", page_icon="🍳", layout="wide")

# def find_recipes(ingredients, number, ranking, ignore_pantry, api_key):
#     url = "https://api.spoonacular.com/recipes/findByIngredients"
#     params = {
#         "ingredients": ingredients,
#         "number": number,
#         "ranking": ranking,
#         "ignorePantry": str(ignore_pantry).lower(),
#         "apiKey": api_key
#     }
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         st.error(f"An error occurred: {e}")
#         return None

# # UI for Recipe Finder
# st.title("Recipe Finder by Ingredients")
# st.write("Find recipes based on the ingredients you have!")

# # Input section
# with st.form("ingredient_form"):
#     st.write("Enter the ingredients you have:")
#     ingredients_input = st.text_area(
#         "Ingredients (comma-separated)",
#         placeholder="e.g., apples, flour, sugar"
#     )
#     number_of_recipes = st.slider("Number of Recipes to Fetch", 1, 100, 10)
#     ranking_option = st.selectbox(
#         "Recipe Ranking",
#         options=[1, 2],
#         format_func=lambda x: "Maximize Used Ingredients" if x == 1 else "Minimize Missing Ingredients"
#     )
#     ignore_pantry_items = st.checkbox("Ignore pantry items (e.g., water, salt, flour)", value=True)
#     submitted = st.form_submit_button("Find Recipes")

# if submitted and ingredients_input:
#     # Call the API
#     api_key = "92d69d50485a4c429fdefc0cb5e2dbee"  # Replace with your API key
#     recipes = find_recipes(
#         ingredients=ingredients_input,
#         number=number_of_recipes,
#         ranking=ranking_option,
#         ignore_pantry=ignore_pantry_items,
#         api_key=api_key
#     )

#     if recipes:
#         st.success(f"Found {len(recipes)} recipe(s)!")
#         # Display the recipes
#         for recipe in recipes:
#             with st.expander(recipe['title']):
#                 # Display image if available
#                 if recipe.get('image'):
#                     st.image(recipe['image'], use_column_width=True)
                
#                 # Ingredients used and missed
#                 used_ingredients = [ing['original'] for ing in recipe['usedIngredients']]
#                 missed_ingredients = [ing['original'] for ing in recipe['missedIngredients']]

#                 st.write(f"**Used Ingredients ({len(used_ingredients)}):**")
#                 st.markdown("\n".join([f"- {ingredient}" for ingredient in used_ingredients]))

#                 st.write(f"**Missed Ingredients ({len(missed_ingredients)}):**")
#                 st.markdown("\n".join([f"- {ingredient}" for ingredient in missed_ingredients]))

#                 # Link to recipe
#                 st.markdown(f"[View Recipe Details](https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']})")






# Load model and class names
model = load_model("/app/model/keras_model.h5", compile=False)
class_names = open("/app/model/labels.txt", "r").readlines()

# Function to predict ingredient from an image
def predict_ingredient(image):
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS).convert("RGB")
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    normalized_image_array = (np.asarray(image).astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence_score = prediction[0][index]
    return class_name, confidence_score

# Initialize session states
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []
if "pending_images" not in st.session_state:
    st.session_state.pending_images = []

# Function to crop and resize an image to a square
def crop_to_square(image, size=150):
    """Crop the image to a square and resize to the specified size."""
    return ImageOps.fit(image, (size, size), method=Image.Resampling.LANCZOS)

# Tab 1: Image Recognition
st.subheader("Image Recognition")

uploaded_files = st.file_uploader(
    "Upload images of ingredients", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True
)

# Store uploaded images in session state
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file not in st.session_state.pending_images:
            st.session_state.pending_images.append(uploaded_file)


# Function to remove the image from the pending list
def remove_image(uploaded_file):
    st.session_state.pending_images.remove(uploaded_file)

# Function to append the ingredient to the list
def append_ingredient(ingredient, uploaded_file):
    if ingredient.strip() not in st.session_state.ingredients:
        st.session_state.ingredients.append(ingredient.strip())
        st.success(f"Added '{ingredient}' to the ingredient list.")
        remove_image(uploaded_file)
    else:
        st.warning(f"'{ingredient}' is already in the ingredient list.")
        remove_image(uploaded_file)
    

# Display pending images
if st.session_state.pending_images:
    for i in range(0, len(st.session_state.pending_images), 4):
        cols = st.columns(4)  # Create 4 columns for each row
        for j, uploaded_file in enumerate(st.session_state.pending_images[i:i+4]):
            with cols[j]:
                image = Image.open(uploaded_file)
                cropped_image = crop_to_square(image)
                st.image(cropped_image, caption=f"{uploaded_file.name}", width=150)
                
                # Predict button
                if st.button(f"Predict {uploaded_file.name}", key=f"predict_{uploaded_file.name}"):
                    class_name, confidence = predict_ingredient(cropped_image)
                    class_name = " ".join(class_name.split()[1:])
                    st.write(f"Model Suggestion: {class_name} (Confidence: {confidence:.2f})")

                    # Confirm and Discard Buttons
                    if st.button(f"Confirm {uploaded_file.name}", key=f"confirm_{uploaded_file.name}", on_click=append_ingredient, args=(class_name, uploaded_file,)):
                        st.experimental_rerun()
                    if st.button(f"Discard {uploaded_file.name}", key=f"discard_{uploaded_file.name}", on_click=remove_image, args=(uploaded_file,)):
                        st.warning("Suggestion discarded.")
                        st.experimental_rerun()

# Tab 2: Manual Entry
st.subheader("Manual Entry")
manual_input = st.text_input("Enter ingredient name manually:")
if st.button("Add Ingredient", key="add_manual"):
    if manual_input.strip():
        st.session_state.ingredients.append(manual_input.strip())
        st.success(f"Added '{manual_input}' to the ingredient list.")
    else:
        st.error("Please enter a valid ingredient name.")


# Display the ingredient list
st.subheader("Ingredient List")
if st.session_state.ingredients:
    st.markdown("### Ingredients Added:")
    for i, ingredient in enumerate(st.session_state.ingredients, start=1):
        st.write(f"{i}. {ingredient}")
else:
    st.write("No ingredients added yet.")


def find_recipes(ingredients, number, ranking, ignore_pantry, api_key):
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": number,
        "ranking": ranking,
        "ignorePantry": str(ignore_pantry).lower(),
        "apiKey": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

# UI for Recipe Finder
st.title("Recipe Finder by Ingredients")
st.write("Find recipes based on the ingredients you have!")

# Input section
with st.form("ingredient_form"):
    # st.write("Enter the ingredients you have:")
    ingredients_input = st.text_area(
        "Ingredients (comma-separated)",
        placeholder="e.g., apples, flour, sugar"
    )
    number_of_recipes = st.slider("Number of Recipes to Fetch", 1, 100, 10)
    ranking_option = st.selectbox(
        "Recipe Ranking",
        options=[1, 2],
        format_func=lambda x: "Maximize Used Ingredients" if x == 1 else "Minimize Missing Ingredients"
    )
    ignore_pantry_items = st.checkbox("Ignore pantry items (e.g., water, salt, flour)", value=True)
    submitted = st.form_submit_button("Find Recipes")

# if submitted and ingredients_input:
#     # Call the API
#     api_key = "92d69d50485a4c429fdefc0cb5e2dbee"  # Replace with your API key
#     recipes = find_recipes(
#         ingredients=ingredients_input,
#         number=number_of_recipes,
#         ranking=ranking_option,
#         ignore_pantry=ignore_pantry_items,
#         api_key=api_key
#     )

#     if recipes:
#         st.success(f"Found {len(recipes)} recipe(s)!")
#         # Display the recipes
#         for recipe in recipes:
#             with st.expander(recipe['title']):
#                 # Display image if available
#                 if recipe.get('image'):
#                     st.image(recipe['image'], use_column_width=True)
                
#                 # Ingredients used and missed
#                 used_ingredients = [ing['original'] for ing in recipe['usedIngredients']]
#                 missed_ingredients = [ing['original'] for ing in recipe['missedIngredients']]

#                 st.write(f"**Used Ingredients ({len(used_ingredients)}):**")
#                 st.markdown("\n".join([f"- {ingredient}" for ingredient in used_ingredients]))

#                 st.write(f"**Missed Ingredients ({len(missed_ingredients)}):**")
#                 st.markdown("\n".join([f"- {ingredient}" for ingredient in missed_ingredients]))

#                 # Link to recipe
#                 st.markdown(f"[View Recipe Details](https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']})")

