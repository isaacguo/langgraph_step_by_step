"""
Observability - Logging
Demonstrates logging patterns for LangGraph applications
"""

import os
import logging
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    messages: Annotated[list, "messages"]
    step_count: int
    data: dict


def logging_example():
    """Basic logging in nodes"""
    print("=" * 60)
    print("Example 1: Node Logging")
    print("=" * 60)
    
    def logged_node(state: GraphState):
        """Node with logging"""
        logger.info(f"Executing node, step_count: {state.get('step_count', 0)}")
        
        try:
            step = state.get("step_count", 0) + 1
            logger.debug(f"Incrementing step to {step}")
            
            return {
                "step_count": step
            }
        except Exception as e:
            logger.error(f"Error in node: {e}", exc_info=True)
            raise
    
    workflow = StateGraph(GraphState)
    workflow.add_node("logged", logged_node)
    workflow.set_entry_point("logged")
    workflow.add_edge("logged", END)
    
    app = workflow.compile()
    
    state = {"messages": [], "step_count": 0, "data": {}}
    result = app.invoke(state)
    
    print(f"Result: step_count = {result['step_count']}")
    print()


def structured_logging_example():
    """Structured logging with context"""
    print("=" * 60)
    print("Example 2: Structured Logging")
    print("=" * 60)
    
    def structured_node(state: GraphState):
        """Node with structured logging"""
        step = state.get("step_count", 0) + 1
        
        # Structured log with context
        logger.info("Node execution", extra={
            "step_count": step,
            "node_name": "structured_node",
            "state_keys": list(state.keys())
        })
        
        return {
            "step_count": step,
            "data": {"logged": True}
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("structured", structured_node)
    workflow.set_entry_point("structured")
    workflow.add_edge("structured", END)
    
    app = workflow.compile()
    
    state = {"messages": [], "step_count": 0, "data": {}}
    result = app.invoke(state)
    
    print(f"Result: {result['data']}")
    print()


def performance_logging_example():
    """Performance logging"""
    print("=" * 60)
    print("Example 3: Performance Logging")
    print("=" * 60)
    
    import time
    
    def timed_node(state: GraphState):
        """Node with performance logging"""
        start_time = time.time()
        
        # Simulate work
        time.sleep(0.1)
        
        step = state.get("step_count", 0) + 1
        elapsed = time.time() - start_time
        
        logger.info(f"Node completed in {elapsed:.3f}s", extra={
            "execution_time": elapsed,
            "step_count": step
        })
        
        return {
            "step_count": step,
            "data": {"execution_time": elapsed}
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("timed", timed_node)
    workflow.set_entry_point("timed")
    workflow.add_edge("timed", END)
    
    app = workflow.compile()
    
    state = {"messages": [], "step_count": 0, "data": {}}
    result = app.invoke(state)
    
    print(f"Execution time: {result['data'].get('execution_time', 0):.3f}s")
    print()


if __name__ == "__main__":
    try:
        logging_example()
        structured_logging_example()
        performance_logging_example()
        
        print("=" * 60)
        print("All logging examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

