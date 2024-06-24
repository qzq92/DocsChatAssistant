from backend.core import run_llm
from streamlit_chat import message
from typing import Set
import streamlit as st

# Define header for page
st.header("Documentation Helper Bot")

# Persist history of user and chat answers to avoid reset due to streamlit session interaction by first creating such object
if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []

if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []

# Persist history of entire chat
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# UI prompt
prompt = st.text_input(label="Prompt", placeholder="Enter your prompt here....")

def create_sources_string(source_urls: Set[str]) -> str:
    # For empty string:
    if not source_urls:
        return ""

    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}) {source}\n"
    return sources_string

if prompt:
    with st.spinner("Generating response..."):
        # Feed llm with promp and history
        generated_response = run_llm(
            query=prompt, 
            chat_history=st.session_state["chat_history"]
        )
    
        # Get source info from response and format them
        sources = set([docs.metadata["source"] for docs in generated_response["source_documents"]])

        # formatted_response = f"{generated_response["result"]} \n\n {create_sources_string(sources)}"
        # ConversationalRetrievalQA
        formatted_response = f"{generated_response["answer"]} \n\n {create_sources_string(sources)}"

        # Append state with prompt/response values for Streamlit to persist as part of state sharing
        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)

        # Store raw prompt/answers
        # st.session_state["chat_history"].append(prompt, generated_response["result"])
        # ConversationalRetrievalQA
        st.session_state["chat_history"].append((prompt, generated_response["answer"]))

# Show chatbot construct if there is chat answer history
if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answers_history"],
        st.session_state["user_prompt_history"]
    ):
        # Show message in chat structure. Seed controls the avatar used
        message(user_query, is_user=True, seed=55) # align's the message to the right
        message(generated_response, seed=41)
