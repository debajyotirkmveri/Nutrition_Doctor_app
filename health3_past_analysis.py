from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

load_dotenv()  # Load environment variables

# Configure Google Gemini AI with the API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro Vision API and get response
def get_gemini_response(input_text, image, prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([input_text, image[0], prompt])
    return response.text

# Function to set up the image data for processing
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize Streamlit app
st.set_page_config(page_title="Gemini Health App")

st.header("Gemini Health App")
input_text = "Analyze the food items from the image and calculate the total calories, providing details for each item."

# File uploader for the image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = None

# Display the uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# Button to submit and analyze the image
submit = st.button("Analyze Food Items")

# Prompt for the AI model
input_prompt = """
You are an expert nutritionist tasked with analyzing the food items in the uploaded image.
Identify each food item, calculate the total calories, and provide details of each item in the format:

1. Item 1 - number of calories
2. Item 2 - number of calories
---
---

Additionally, indicate whether the food is healthy or unhealthy. For unhealthy items, provide a warning message with reasons (e.g., high sugar, high fat). Include a percentage split of carbohydrates, fats, fibers, sugars, and other essential nutrients.
"""

# Initialize past results in session state
if 'past_results' not in st.session_state:
    st.session_state['past_results'] = []

# Process the input when submit button is clicked
if submit:
    if uploaded_file is not None:
        try:
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_text, image_data, input_prompt)
            
            # Display current analysis
            st.subheader("Current Analysis")
            st.write(response)

            # Save the current analysis to past results
            st.session_state['past_results'].append({
                'input': input_text,
                'response': response,
                'image_data': image_data[0]['data']  # Store just the image data for display
            })

        except Exception as e:
            st.error(f"An error occurred: {e}")

    else:
        st.error("Please upload an image to analyze.")

# Display past results
if st.session_state['past_results']:
    st.subheader("Past Analyses")
    for idx, result in enumerate(st.session_state['past_results']):
        st.write(f"**Analysis {idx + 1}:**")
        st.write(result['response'])
        st.image(result['image_data'], caption=f"Past Image {idx + 1}", use_column_width=True)
        st.write("---")
else:
    st.write("No past analyses found.")
