"""
Memory Management - Memory Types
Demonstrates different memory types and their use cases
"""

import os
import sys
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_classic.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "conversation messages"]
    memory_type: str
    step_count: int


def buffer_memory_example():
    """Conversation buffer memory - stores all messages"""
    print("=" * 60)
    print("Example 1: Buffer Memory")
    print("=" * 60)
    
    memory = ConversationBufferMemory(return_messages=True)
    
    # Save context
    memory.save_context(
        {"input": "My name is Alice"},
        {"output": "Nice to meet you, Alice!"}
    )
    memory.save_context(
        {"input": "What's my name?"},
        {"output": "Your name is Alice."}
    )
    
    # Load memory
    memory_vars = memory.load_memory_variables({})
    print(f"Memory variables: {list(memory_vars.keys())}")
    print(f"Message count: {len(memory.chat_memory.messages)}")
    print()


def summary_memory_example():
    """Summary memory - summarizes old messages"""
    print("=" * 60)
    print("Example 2: Summary Memory")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    memory = ConversationSummaryMemory(llm=llm, return_messages=True)
    
    # Add multiple messages
    for i in range(5):
        memory.save_context(
            {"input": f"Message {i+1}: This is conversation turn {i+1}"},
            {"output": f"Response {i+1}: Acknowledged"}
        )
    
    print(f"Total messages: {len(memory.chat_memory.messages)}")
    print(f"Summary: {memory.moving_summary_buffer[:200]}...")
    print()


def window_memory_example():
    """Window memory - only keeps recent messages"""
    print("=" * 60)
    print("Example 3: Window Memory")
    print("=" * 60)
    
    memory = ConversationBufferWindowMemory(k=3, return_messages=True)
    
    # Add more messages than window size
    for i in range(5):
        memory.save_context(
            {"input": f"Input {i+1}"},
            {"output": f"Output {i+1}"}
        )
    
    print(f"Window size: 3")
    print(f"Total messages stored: {len(memory.chat_memory.messages)}")
    print(f"Should be <= 6 (3 pairs): {len(memory.chat_memory.messages) <= 6}")
    print()


def graph_with_memory():
    """Graph using checkpoint memory"""
    print("=" * 60)
    print("Example 4: Graph with Checkpoint Memory")
    print("=" * 60)
    
    def add_message_node(state: GraphState):
        """Add a message"""
        step = state.get("step_count", 0) + 1
        return {
            "messages": state.get("messages", []) + [
                {"role": "user", "content": f"Message {step}"}
            ],
            "step_count": step
        }
    
    # Build graph
    workflow = StateGraph(GraphState)
    workflow.add_node("add_message", add_message_node)
    workflow.set_entry_point("add_message")
    workflow.add_edge("add_message", END)
    
    # Use memory checkpoint
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "memory_thread_1"}}
    
    # Multiple invocations with state persistence
    state = {"messages": [], "memory_type": "checkpoint", "step_count": 0}
    
    for i in range(3):
        state = app.invoke(state, config)
        print(f"After invocation {i+1}: {state['step_count']} steps, {len(state['messages'])} messages")
    
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
        buffer_memory_example()
        #summary_memory_example()
        window_memory_example()
        graph_with_memory()
        
        print("=" * 60)
        print("All memory type examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

