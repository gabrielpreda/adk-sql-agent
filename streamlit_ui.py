import streamlit as st
import requests
from io import StringIO
import pandas as pd
import json
import ast

st.set_page_config(page_title='SQL Agent', 
                    page_icon = "assets/gemini_avatar.png",
                    initial_sidebar_state = 'auto')

st.markdown("<h2 style='text-align: center; color: #005aff;'>SQL Agent</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #005aff;'>Explore your SQL data with Gemini & ADK</h3>", unsafe_allow_html=True)

API_URL = "http://localhost:8000/query"

avatars = {
    "assistant" : "assets/gemini_avatar.png",
    "user": "assets/user_avatar.png"
}

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]


with st.sidebar:
    st.image("assets/gemini_avatar.png")
    st.button("Clear Chat History", on_click=clear_chat_history)

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]
for message in st.session_state.messages:
    with st.chat_message(message["role"], 
                         avatar=avatars[message["role"]]):

        st.write(message["content"], unsafe_allow_html=True)
        if message.get("sql"):
            st.markdown("<h5 style='text-align: left; color: #005aff;'>SQL</h5>", unsafe_allow_html=True)
            st.write(message["sql"], unsafe_allow_html=True)
        if message.get("raw_result"):
            st.markdown("<h5 style='text-align: left; color: #005aff;'>Result</h5>", unsafe_allow_html=True)
            st.write(message["raw_result"], unsafe_allow_html=True)
        if message.get("result_evaluation"):
            st.markdown("<h5 style='text-align: left; color: #005aff;'>Result evaluation</h5>", unsafe_allow_html=True)
            st.write(message["result_evaluation"], unsafe_allow_html=True)


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatars["user"]):
        st.write(prompt)

if "history" not in st.session_state:
    st.session_state.history = []

def parse_response_string(raw_input: str) -> dict:
    """
    Parses a string that may contain either:
    - a pure JSON string
    - a Markdown block starting with ```json ... ```

    Args:
        raw_input (str): the response string
    Returns:
        A dictionary with parsed fields, including raw_result as a structured list.
    """

    # Step 0: Test if we do have content
    if not raw_input:
        return {"error": "error encountered: empty response"}


    # Step 1: Remove markdown fences if they exist
    if raw_input.strip().startswith("```json"):
        clean_str = "\n".join(
            line for line in raw_input.strip().splitlines()
            if not line.strip().startswith("```")
        )
    else:
        clean_str = raw_input.strip()

    # Step 2: Try parsing JSON
    try:
        data = json.loads(clean_str)
    except json.JSONDecodeError as e:

        print(f"Invalid JSON input: {e}")

    return data

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        with st.spinner("Thinking..."):
            response = requests.post(API_URL, json={
                "query": prompt,
                "history": st.session_state.history})

            response_str = response.json().get("response_text")
            data = parse_response_string(response_str)

            # Update history for next round
            if data:
                st.session_state.history = data.get("history", [])

                data_summary = data_sql = data_summary = None
                if data.get("error"):
                    st.error(f"Error: {data['error']}")
                    message = {"role": "assistant", 
                        "content": data["error"],
                        "avatar": avatars["assistant"]}
                    st.session_state.messages.append(message)
                else:
                    # Show summary
                    if data.get("summary"):
                        st.markdown(data["summary"], unsafe_allow_html=True)
                        data_summary = data


                    # Show result
                    if data.get("raw_result"):
                        st.markdown("<h5 style='text-align: left; color: #005aff;'>Result</h5>", unsafe_allow_html=True)
                        st.markdown(data["raw_result"])


                    # Show result evaluation
                    if data.get("result_evaluation"):
                        st.markdown("<h5 style='text-align: left; color: #005aff;'>Result evaluation</h5>", unsafe_allow_html=True)
                        st.code(data["result_evaluation"])

                    # Show SQL query
                    if data.get("sql"):
                        st.markdown("<h5 style='text-align: left; color: #005aff;'>SQL</h5>", unsafe_allow_html=True)
                        st.code(data["sql"])


                    message = {"role": "assistant", 
                            "content": data.get("summary"),
                            "sql": data.get("sql"), 
                            "raw_result": data.get("raw_result"),
                            "avatar": avatars["assistant"]}
                    st.session_state.messages.append(message)

