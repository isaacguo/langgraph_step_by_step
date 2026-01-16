"""
LangChain Basics - Prompts and LLMs
Demonstrates basic prompt templates and LLM interactions
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()

def basic_llm_call():
    """Basic LLM call without prompts"""
    print("=" * 60)
    print("Example 1: Basic LLM Call")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    response = llm.invoke("What is the capital of France?")
    print(f"Response: {response.content}\n")


def prompt_template_example():
    """Using PromptTemplate for string formatting"""
    print("=" * 60)
    print("Example 2: Prompt Template")
    print("=" * 60)
    
    prompt = PromptTemplate(
        input_variables=["topic", "audience"],
        template="Explain {topic} to a {audience} in simple terms."
    )
    
    formatted_prompt = prompt.format(topic="quantum computing", audience="5-year-old")
    print(f"Formatted Prompt: {formatted_prompt}\n")
    
    llm = get_local_llm(temperature=0.7)
    response = llm.invoke(formatted_prompt)
    print(f"Response: {response.content}\n")


def chat_prompt_template_example():
    """Using ChatPromptTemplate for structured conversations"""
    print("=" * 60)
    print("Example 3: Chat Prompt Template")
    print("=" * 60)
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that explains concepts clearly."),
        ("human", "Explain {concept} with an example.")
    ])
    
    messages = chat_prompt.format_messages(concept="recursion")
    print("Messages:")
    for msg in messages:
        print(f"  {msg.__class__.__name__}: {msg.content}")
    print()
    
    llm = get_local_llm(temperature=0.7)
    response = llm.invoke(messages)
    print(f"Response: {response.content}\n")


def manual_message_construction():
    """Manually constructing messages"""
    print("=" * 60)
    print("Example 4: Manual Message Construction")
    print("=" * 60)
    
    messages = [
        SystemMessage(content="You are a coding assistant."),
        HumanMessage(content="Write a Python function to calculate factorial.")
    ]
    
    llm = get_local_llm(temperature=0.7)
    response = llm.invoke(messages)
    print(f"Response: {response.content}\n")


def streaming_example():
    """Streaming responses for better UX"""
    print("=" * 60)
    print("Example 5: Streaming Response")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7, streaming=True)
    
    prompt = "Tell me a short story about a robot learning to paint."
    print("Streaming response:")
    print("-" * 60)
    
    for chunk in llm.stream(prompt):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    # Check for LM Studio server
    import requests
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code != 200:
            print("WARNING: LM Studio server may not be running on port 1234")
    except requests.exceptions.RequestException:
        print("WARNING: Cannot connect to LM Studio server at http://localhost:1234")
        print("Make sure LM Studio is running and the server is started.")
        print("You can still try to run the examples, but they may fail if the server is not available.")
    
    try:
        basic_llm_call()
        prompt_template_example()
        chat_prompt_template_example()
        manual_message_construction()
        streaming_example()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. LM Studio is running and server is started on port 1234")
        print("2. Model 'qwen/qwen3-4b-2507' is loaded in LM Studio")
        print("3. Installed required packages: pip install langchain langchain-openai python-dotenv requests")

