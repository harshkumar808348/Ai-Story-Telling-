# app.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Configure the Gemini API key
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in .env file or environment variables. Please set it.")
        st.stop()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# Select the model
# For text generation, 'gemini-1.5-flash' is a good, fast, and cost-effective choice.
# You can also use 'gemini-pro'
MODEL_NAME = "gemini-1.5-flash"
try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Error initializing Gemini model ({MODEL_NAME}): {e}")
    st.stop()

# --- Helper Function to Generate Story Idea ---
def generate_story_idea(genre, keyword=None):
    """
    Generates a story idea using the Gemini API.
    """
    prompt_parts = [
        f"Generate a short, unique, and intriguing story idea for a {genre} story.",
        "The idea should be a single paragraph, sparking curiosity and suggesting conflict or mystery.",
        "Avoid cliches if possible."
    ]
    if keyword:
        prompt_parts.append(f"The story should somehow incorporate the keyword: '{keyword}'.")
    
    prompt_parts.append("Make the idea compelling enough that someone would want to read or write this story.")
    
    full_prompt = "\n".join(prompt_parts)

    st.sidebar.subheader("Full Prompt Sent to AI:")
    st.sidebar.markdown(f"```\n{full_prompt}\n```")


    try:
        # More advanced generation config (optional)
        generation_config = genai.types.GenerationConfig(
            temperature=0.8, # Controls randomness: Lower is more predictable, higher is more creative
            top_p=0.95,      # Nucleus sampling
            top_k=40,        # Top-k sampling
            max_output_tokens=250
        )
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
            )
        
        if response.parts:
            return response.text
        else:
            # Investigate response.prompt_feedback if content is blocked
            if response.prompt_feedback:
                st.warning(f"Content generation might have been blocked. Reason: {response.prompt_feedback}")
            return "Sorry, I couldn't generate a story idea at this moment. The content might have been blocked or an unknown error occurred."

    except Exception as e:
        st.error(f"An error occurred during story idea generation: {e}")
        return None

# --- Streamlit App UI ---
st.set_page_config(page_title="AI Story Idea Generator", layout="wide")

st.title("🚀 AI Creative Story Idea Generator")
st.markdown("Let AI spark your next narrative masterpiece! Choose a genre and optionally add a keyword.")

# Sidebar for API Key status (optional, good for debugging)
st.sidebar.header("Configuration")
if api_key:
    st.sidebar.success("Gemini API Key Loaded!")
else:
    st.sidebar.error("Gemini API Key NOT Loaded!")


# Main Area
col1, col2 = st.columns([1, 2]) # Column for inputs, column for output

with col1:
    st.subheader("Your Preferences")
    
    # Genre selection
    genres = [
        "Science Fiction", "Fantasy", "Mystery", "Thriller", 
        "Horror", "Romance", "Historical Fiction", "Comedy", 
        "Adventure", "Dystopian", "Cyberpunk", "Steampunk"
    ]
    selected_genre = st.selectbox("Choose a Genre:", genres, index=0)

    # Optional keyword
    keyword_input = st.text_input("Optional: Enter a Keyword or Theme (e.g., 'time travel', 'hidden artifact')")

    # Generate button
    if st.button("✨ Generate Story Idea ✨", use_container_width=True, type="primary"):
        if not selected_genre:
            st.warning("Please select a genre.")
        else:
            with st.spinner(f"🧠 Generating a {selected_genre} story idea..."):
                story_idea = generate_story_idea(selected_genre, keyword_input)
                
                # Store in session state to keep it if the user changes input and reruns
                st.session_state.generated_idea = story_idea
                st.session_state.genre_for_idea = selected_genre
                st.session_state.keyword_for_idea = keyword_input

with col2:
    st.subheader("💡 Your Generated Story Idea")
    if 'generated_idea' in st.session_state and st.session_state.generated_idea:
        st.markdown(f"**Genre:** {st.session_state.genre_for_idea}")
        if st.session_state.keyword_for_idea:
            st.markdown(f"**Keyword:** {st.session_state.keyword_for_idea}")
        
        st.info(st.session_state.generated_idea) # Using st.info for a nice bordered box
        
        if st.button("🔄 Generate Another One (Same Settings)"):
             with st.spinner(f"🧠 Generating another {st.session_state.genre_for_idea} story idea..."):
                new_story_idea = generate_story_idea(st.session_state.genre_for_idea, st.session_state.keyword_for_idea)
                st.session_state.generated_idea = new_story_idea # Update session state
                st.rerun() # Rerun the script to update the display immediately
    else:
        st.write("Your story idea will appear here once generated.")

st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Google Gemini API](https://ai.google.dev/docs/gemini_api_overview).")