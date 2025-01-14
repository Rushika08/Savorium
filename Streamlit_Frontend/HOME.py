import streamlit as st

st.set_page_config(
    page_title="Savorium",
    page_icon="👋",
)

# st.image(r"D:\Sem 6-7 project\Diet-Recommendation-System-main\Assets\Savorium_logo.jpg")

st.image("Savorium_logo.jpg", width=150)

st.write("# Savorium 👋")

st.sidebar.success("Select a recommendation app.")

st.markdown(
    """
    A diet recommendation web application using content-based approach with Scikit-Learn, FastAPI and Streamlit.
    You can find more details and the whole project on my [repo](https://github.com/zakaria-narjis/Diet-Recommendation-System).
    """
)





# Load Google Fonts
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kablammo&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

    .kablammo {
        font-family: 'Kablammo', cursive; /* Use Kablammo font */
        font-size: 24px; /* Adjust size as needed */
        color: #d32f2f; /* Example color for Kablammo */
    }

    .langar {
        font-family: 'Langar', cursive; /* Use Langar font */
        font-size: 22px; /* Adjust size as needed */
        color: #1976d2; /* Example color for Langar */
    }

    .libre-baskerville {
        font-family: 'Libre Baskerville', serif; /* Use Libre Baskerville font */
        font-size: 18px; /* Adjust size as needed */
        color: #333; /* Example color for Libre Baskerville */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Example usage
st.markdown('<h1 class="langar">SAVORIUM</h1>', unsafe_allow_html=True)
st.markdown('<p class="libre-baskerville">HI...This paragraph is using the Libre Baskerville font.</p>', unsafe_allow_html=True)

