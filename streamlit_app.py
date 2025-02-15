from __future__ import annotations

import asyncio

import streamlit as st
from llmling_agent import Agent

SYS_PROMPT = """
Du bist Uschi, eine deutschsprachige Expertin bezüglich des EU-AI Acts und kennst dich mit dem Gesetzeswerk perfekt aus.
Spreche deutsch. Stelle dich mit Namen vor.
Dein Job ist es, einkommende Information zu klassifizieren nach folgenden Kriterien:

- Rechtliche Konsequenzen
- Technische Konsequenzen
- Ethische Konsequenzen
- Wirtschaftliche Konsequenzen

Falls dir Informationen fehlen, bitte frag nach.

"""


async def run():
    # Show title and description.
    st.title("💬 EU-AI Act Chatbot")
    st.write("Willommen. Um diese App zu nutzen, benötigst du einen OpenAI API key.")
    # `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    model = st.text_input("Modell auswählen", value="gpt-4o-mini")
    sys_prompt = st.text_area("System prompt", value=SYS_PROMPT)
    if "agent" not in st.session_state:
        new_agent = Agent[None](model=model, system_prompt=sys_prompt)
        st.session_state.agent = new_agent

    agent = st.session_state.agent

    def reset_agent():
        new_agent = Agent[None](model=model, system_prompt=sys_prompt)
        st.session_state.agent = new_agent

    _ = st.button("Reset", on_click=reset_agent)

    # Display the existing chat messages via `st.chat_message`.
    for message in agent._logger.message_history:
        with st.chat_message(message.role):
            st.markdown(str(message.content))

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("Wie kann ich behilflich sein?"):
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
