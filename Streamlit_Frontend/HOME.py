import streamlit as st
import json
from streamlit_lottie import st_lottie

# Page Configuration
st.set_page_config(
    page_title="Savorium",
    page_icon="🥗",
    layout="wide"
)

# Function to Load Lottie Animations
def load_lottie(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Load Cooking Animation (Replace with your own Lottie animation file)
cooking_animation = load_lottie("cooking_anime.json")

# Custom Styling & Animation
st.markdown(
    """
    <style>
        /* Animated Gradient Background */
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .main-container {
            background: linear-gradient(45deg, #ff9a9e, #fad0c4, #fad0c4, #ffdde1);
            background-size: 400% 400%;
            animation: gradient 10s ease infinite;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        /* Title Styling */
        .title {
            font-size: 50px;
            font-weight: bold;
            color: #2c3e50;
            animation: fadeIn 2s ease-in-out;
        }

        /* Subtitle */
        .subtitle {
            font-size: 22px;
            color: #34495e;
            margin-bottom: 20px;
            animation: fadeIn 2s ease-in-out;
        }

        /* Description */
        .description {
            font-size: 18px;
            color: #555;
            margin-bottom: 30px;
            animation: fadeIn 3s ease-in-out;
        }

        /* Animated Button */
        .animated-btn {
            background: #2c3e50;
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            transition: 0.3s ease-in-out;
            animation: fadeIn 3.5s ease-in-out;
            display: inline-block;
        }

        .animated-btn:hover {
            background: #1d2731;
            transform: scale(1.05);
        }

        /* Feature List Styling */
        .features-container {
            margin-top: 30px;
            text-align: left;
            padding: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
        }

        .feature-item {
            font-size: 18px;
            margin: 10px 0;
            display: flex;
            align-items: center;
        }

        .feature-icon {
            font-size: 24px;
            margin-right: 10px;
            color: #27ae60;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Title & Subtitle
st.markdown('<div class="title">Savorium 🥗</div>', unsafe_allow_html=True)

# Cooking Animation
st_lottie(cooking_animation, height=300, key="cooking")

st.markdown('<div class="subtitle">Your AI-Powered Personalized Diet Companion</div>', unsafe_allow_html=True)

# Description
st.markdown(
    '<div class="description">🍽️ Eat smarter with AI! Savorium analyzes your preferences and provides the best diet recommendations tailored for you. 🍏</div>',
    unsafe_allow_html=True
)

# Features Section
st.markdown(
    """
    <div class="features-container">
        <h3>🔹 Features of Savorium</h3>
        <div class="feature-item"><span class="feature-icon">✅</span> AI-driven personalized meal recommendations</div>
        <div class="feature-item"><span class="feature-icon">✅</span> Content-based filtering for better diet choices</div>
        <div class="feature-item"><span class="feature-icon">✅</span> FastAPI-powered backend for quick responses</div>
        <div class="feature-item"><span class="feature-icon">✅</span> Seamless user experience with Streamlit</div>
        <div class="feature-item"><span class="feature-icon">✅</span> Beautiful and intuitive user interface</div>
    </div>
    """,
    unsafe_allow_html=True
)

# GitHub Contribution Button
github_link = "https://github.com/your-github-repo-link"  # Replace with your actual GitHub repository link
st.markdown(
    f'<a class="animated-btn" href="{github_link}" target="_blank">🚀 Contribute on GitHub</a>',
    unsafe_allow_html=True
)

# Close Main Container
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar Message
st.sidebar.success("Select a recommendation app.")
