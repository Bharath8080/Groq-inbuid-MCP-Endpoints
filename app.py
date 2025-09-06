import chainlit as cl
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define chat profiles (Groq models available in Chainlit UI)
@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="moonshotai/kimi-k2-instruct-0905",
            markdown_description="Using **Kimi-K2 Instruct 0905** model for instruction following and structured outputs.",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxsh0CyhpofrQ95jBcDBlDhWHOQ1ZRLQPwdQ&s",
        ),
        cl.ChatProfile(
            name="openai/gpt-oss-120b",
            markdown_description="Using **GPT-OSS-120B** model for general-purpose Q&A, reasoning, and creative tasks.",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxsh0CyhpofrQ95jBcDBlDhWHOQ1ZRLQPwdQ&s",
        ),
    ]

@cl.on_chat_start
async def start_chat():
    await cl.Message(
        content="👋 Hi! Choose a model (gpt-oss-120b or kimi-k2-instruct-0905) and ask me about ICC 2025 Finals or anything else."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # Get the selected chat profile (defaults to kimi-k2-instruct-0905 if none chosen)
    selected_profile = cl.user_session.get("chat_profile") or "moonshotai/kimi-k2-instruct-0905"

    # Create a streaming completion request with the chosen model
    completion = client.chat.completions.create(
        model=selected_profile,
        messages=[{"role": "user", "content": message.content}],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        # reasoning_effort="medium",
        stream=True,  # Streamed response
        tools=[
            {
                "type": "mcp",
                "server_label": "Serper",
                "server_url": "https://server.smithery.ai/@marcopesani/mcp-server-serper/mcp?api_key=318135fb-4ad4-4437-b916-9e19a8840f62&profile=yearning-rattlesnake-WM9iJg",
                "headers": {}
            }
        ]
    )

    # Prepare message object for streaming tokens
    msg = cl.Message(content="")

    # Iterate synchronously (Groq stream is NOT async)
    for chunk in completion:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            await msg.stream_token(delta)

    # Send final assembled message
    await msg.send()
