"""
LangChain Basics - Basic Memory
Demonstrates conversation memory and context management
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory
)

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()

def conversation_buffer_memory():
    """Basic conversation buffer - stores all messages"""
    print("=" * 60)
    print("Example 1: Conversation Buffer Memory")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    memory = ConversationBufferMemory(return_messages=True)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    print("Conversation 1:")
    response1 = chain.invoke({"input": "My name is Alice"})
    print(f"User: My name is Alice")
    print(f"Assistant: {response1['response']}\n")
    
    print("Conversation 2:")
    response2 = chain.invoke({"input": "What's my name?"})
    print(f"User: What's my name?")
    print(f"Assistant: {response2['response']}\n")
    
    print("Memory contents:")
    print(memory.chat_memory.messages)
    print()


def conversation_buffer_window_memory():
    """Window memory - only keeps last N messages"""
    print("=" * 60)
    print("Example 2: Conversation Buffer Window Memory")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    memory = ConversationBufferWindowMemory(
        k=2,  # Keep only last 2 exchanges
        return_messages=True
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    print("Adding multiple messages (window size = 2)...")
    chain.invoke({"input": "I like Python"})
    chain.invoke({"input": "I also like JavaScript"})
    chain.invoke({"input": "What programming languages do I like?"})
    
    print("\nMemory (should only contain last 2 exchanges):")
    print(f"Number of messages: {len(memory.chat_memory.messages)}")
    print()


def conversation_summary_memory():
    """Summary memory - summarizes old messages"""
    print("=" * 60)
    print("Example 3: Conversation Summary Memory")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    memory = ConversationSummaryMemory(
        llm=llm,
        return_messages=True
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    # Add several messages
    print("Building conversation history...")
    chain.invoke({"input": "I'm learning about machine learning"})
    chain.invoke({"input": "I'm particularly interested in neural networks"})
    chain.invoke({"input": "Can you explain backpropagation?"})
    
    print("\nMemory summary:")
    print(memory.moving_summary_buffer)
    print()


def conversation_summary_buffer_memory():
    """Summary buffer - combines summary and recent messages"""
    print("=" * 60)
    print("Example 4: Conversation Summary Buffer Memory")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=100,  # Summarize when exceeding this
        return_messages=True
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    print("Building conversation (will summarize when token limit reached)...")
    chain.invoke({"input": "I'm planning a trip to Japan"})
    chain.invoke({"input": "I want to visit Tokyo, Kyoto, and Osaka"})
    chain.invoke({"input": "I'm interested in temples and technology"})
    chain.invoke({"input": "What should I pack?"})
    
    print("\nMemory state:")
    print(f"Summary: {memory.moving_summary_buffer}")
    print(f"Recent messages: {len(memory.chat_memory.messages)} messages")
    print()


def memory_operations():
    """Manual memory operations"""
    print("=" * 60)
    print("Example 5: Manual Memory Operations")
    print("=" * 60)
    
    memory = ConversationBufferMemory(return_messages=True)
    
    # Save context manually
    memory.save_context(
        {"input": "My favorite color is blue"},
        {"output": "That's a nice color!"}
    )
    
    memory.save_context(
        {"input": "I also like green"},
        {"output": "Green is great too!"}
    )
    
    print("Saved messages:")
    for i, msg in enumerate(memory.chat_memory.messages, 1):
        print(f"{i}. {msg.__class__.__name__}: {msg.content}")
    
    # Load memory variables
    memory_vars = memory.load_memory_variables({})
    print(f"\nMemory variables: {list(memory_vars.keys())}")
    
    # Clear memory
    memory.clear()
    print(f"\nAfter clearing, messages: {len(memory.chat_memory.messages)}")
    print()


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
    
    try:
        conversation_buffer_memory()
        conversation_buffer_window_memory()
        conversation_summary_memory()
        conversation_summary_buffer_memory()
        memory_operations()
        
        print("=" * 60)
        print("All memory examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

