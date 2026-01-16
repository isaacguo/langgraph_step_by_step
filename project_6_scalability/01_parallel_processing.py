"""
Scalability - Parallel Processing
Demonstrates parallel processing patterns
"""

import os
import asyncio
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    tasks: Annotated[list, "list of tasks"]
    results: Annotated[list, "list of results"]
    step_count: int


def async_parallel_example():
    """Async parallel processing"""
    print("=" * 60)
    print("Example 1: Async Parallel Processing")
    print("=" * 60)
    
    async def process_task(task_id: int):
        """Process a single task"""
        await asyncio.sleep(0.1)  # Simulate work
        return f"Result_{task_id}"
    
    async def parallel_processor(state: GraphState):
        """Process multiple tasks in parallel"""
        tasks = state.get("tasks", [])
        
        # Process all tasks in parallel
        results = await asyncio.gather(*[
            process_task(i) for i in range(len(tasks))
        ])
        
        return {
            "results": results,
            "step_count": state.get("step_count", 0) + 1
        }
    
    # Note: This is a simplified example
    # Real LangGraph async support would use async nodes
    
    print("Async parallel processing pattern demonstrated")
    print("In production, use LangGraph's async node support")
    print()


def batch_processing_example():
    """Batch processing pattern"""
    print("=" * 60)
    print("Example 2: Batch Processing")
    print("=" * 60)
    
    def process_batch_node(state: GraphState):
        """Process items in batches"""
        tasks = state.get("tasks", [])
        batch_size = 3
        results = []
        
        # Process in batches
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = [f"Processed_{item}" for item in batch]
            results.extend(batch_results)
            print(f"  Processed batch: {batch}")
        
        return {
            "results": results,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GraphState)
    workflow.add_node("process_batch", process_batch_node)
    workflow.set_entry_point("process_batch")
    workflow.add_edge("process_batch", END)
    
    app = workflow.compile()
    
    state = {
        "tasks": list(range(10)),
        "results": [],
        "step_count": 0
    }
    
    result = app.invoke(state)
    print(f"\nProcessed {len(result['results'])} items in batches")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(async_parallel_example())
        batch_processing_example()
        
        print("=" * 60)
        print("All parallel processing examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

