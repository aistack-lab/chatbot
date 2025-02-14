from __future__ import annotations

import asyncio
import os

import streamlit as st
from llmling_agent import Agent
from openai import OpenAI


async def run():
    # Show title and description.
    st.title("💬 EU-blabla Chatbot")
    st.write("Welcome. To use this app, you need to provide an OpenAI API key.")
    # `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    else:
        client = OpenAI(api_key=openai_api_key)
        # Create a session state variable to store the chat messages.
        if "agent" not in st.session_state:
            st.session_state.agent = Agent[None](model="gpt-3.5-turbo")
        agent = st.session_state.agent
        # Display the existing chat messages via `st.chat_message`.
        for message in agent._logger.message_history:
            with st.chat_message(message.role):
                st.markdown(str(message.content))

        # Create a chat input field to allow the user to enter a message.
        if prompt := st.chat_input("What is up?"):
            with st.chat_message("user"):
                st.markdown(prompt)

            async with agent.run_stream(prompt) as stream:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    async for chunk in stream.stream():
                        message_placeholder.markdown(chunk)
            # msg = await agent.run(prompt)
            # with st.chat_message("assistant"):
            #     st.markdown(msg.format())


if __name__ == "__main__":
    asyncio.run(run())
