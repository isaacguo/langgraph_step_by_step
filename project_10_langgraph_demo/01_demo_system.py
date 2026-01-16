"""
LangGraph Demo System
A comprehensive demonstration system showcasing LangGraph capabilities including:
- State management
- Conditional routing
- Multiple processing nodes
- Parallel execution
- Error handling
- Result aggregation
"""

import os
import sys
import operator
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()


class TaskState(TypedDict):
    """State schema for the task processing system"""
    task: str
    task_type: str
    messages: Annotated[list, "conversation messages"]
    research_result: str
    calculation_result: str
    writing_result: str
    analysis_result: str
    parallel_results: Annotated[list, operator.add]  # For parallel node results
    final_result: str
    step_count: int
    error: str
    status: str


def classify_task_node(state: TaskState):
    """Classify the incoming task into different categories"""
    print("\n" + "="*60)
    print("  [Task Classifier] Analyzing task type...")
    print("="*60)
    
    task = state.get("task", "")
    llm = get_local_llm(temperature=0.3)
    
    prompt = ChatPromptTemplate.from_template(
        "Analyze this task and classify it into one of these categories: "
        "'research', 'calculation', 'writing', 'analysis', or 'complex'.\n\n"
        "Task: {task}\n\n"
        "Respond with only the category name."
    )
    chain = prompt | llm
    response = chain.invoke({"task": task})
    
    task_type = response.content.strip().lower()
    # Normalize the response
    if "research" in task_type:
        task_type = "research"
    elif "calculation" in task_type or "calc" in task_type or "math" in task_type:
        task_type = "calculation"
    elif "writing" in task_type or "write" in task_type:
        task_type = "writing"
    elif "analysis" in task_type or "analyze" in task_type:
        task_type = "analysis"
    elif "complex" in task_type or "multiple" in task_type:
        task_type = "complex"
    else:
        task_type = "analysis"  # Default
    
    print(f"  → Task classified as: {task_type}")
    
    return {
        "task_type": task_type,
        "messages": state.get("messages", []) + [
            {"role": "classifier", "content": f"Task classified as: {task_type}"}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "classified"
    }


def research_node(state: TaskState):
    """Process research tasks"""
    print("\n  [Research Node] Conducting research...")
    task = state.get("task", "")
    llm = get_local_llm(temperature=0.7)
    
    prompt = ChatPromptTemplate.from_template(
        "As a research specialist, provide comprehensive research on: {task}\n\n"
        "Include key findings, relevant information, and sources."
    )
    chain = prompt | llm
    response = chain.invoke({"task": task})
    
    result = response.content
    
    print(f"  → Research completed ({len(result)} characters)")
    
    return {
        "research_result": result,
        "messages": state.get("messages", []) + [
            {"role": "researcher", "content": result}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "research_completed"
    }


def calculation_node(state: TaskState):
    """Process calculation tasks"""
    print("\n  [Calculation Node] Performing calculations...")
    task = state.get("task", "")
    llm = get_local_llm(temperature=0.3)
    
    prompt = ChatPromptTemplate.from_template(
        "As a calculation specialist, solve this mathematical problem: {task}\n\n"
        "Provide step-by-step calculation and the final answer."
    )
    chain = prompt | llm
    response = chain.invoke({"task": task})
    
    result = response.content
    
    print(f"  → Calculation completed")
    
    return {
        "calculation_result": result,
        "messages": state.get("messages", []) + [
            {"role": "calculator", "content": result}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "calculation_completed"
    }


def writing_node(state: TaskState):
    """Process writing tasks"""
    print("\n  [Writing Node] Creating content...")
    task = state.get("task", "")
    llm = get_local_llm(temperature=0.8)
    
    prompt = ChatPromptTemplate.from_template(
        "As a writing specialist, create engaging content about: {task}\n\n"
        "Make it clear, well-structured, and informative."
    )
    chain = prompt | llm
    response = chain.invoke({"task": task})
    
    result = response.content
    
    print(f"  → Writing completed ({len(result)} characters)")
    
    return {
        "writing_result": result,
        "messages": state.get("messages", []) + [
            {"role": "writer", "content": result}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "writing_completed"
    }


def analysis_node(state: TaskState):
    """Process analysis tasks"""
    print("\n  [Analysis Node] Performing analysis...")
    task = state.get("task", "")
    llm = get_local_llm(temperature=0.5)
    
    prompt = ChatPromptTemplate.from_template(
        "As an analysis specialist, provide detailed analysis of: {task}\n\n"
        "Include insights, patterns, and recommendations."
    )
    chain = prompt | llm
    response = chain.invoke({"task": task})
    
    result = response.content
    
    print(f"  → Analysis completed ({len(result)} characters)")
    
    return {
        "analysis_result": result,
        "messages": state.get("messages", []) + [
            {"role": "analyst", "content": result}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "analysis_completed"
    }


def parallel_research_node(state: TaskState):
    """Parallel research node - part 1"""
    print("\n  [Parallel Research 1] Researching aspect 1...")
    task = state.get("task", "")
    
    # Simulate parallel research
    result = f"Parallel Research 1: Found information about '{task}' from source A"
    
    return {
        "parallel_results": [{"source": "A", "content": result}],
        "step_count": state.get("step_count", 0) + 1
    }


def parallel_research_node_2(state: TaskState):
    """Parallel research node - part 2"""
    print("\n  [Parallel Research 2] Researching aspect 2...")
    task = state.get("task", "")
    
    # Simulate parallel research
    result = f"Parallel Research 2: Found information about '{task}' from source B"
    
    return {
        "parallel_results": [{"source": "B", "content": result}],
        "step_count": state.get("step_count", 0) + 1
    }


def merge_parallel_results_node(state: TaskState):
    """Merge results from parallel nodes"""
    print("\n  [Merge Node] Merging parallel results...")
    parallel_results = state.get("parallel_results", [])
    
    merged_content = "\n".join([
        f"{r.get('source', 'Unknown')}: {r.get('content', '')}" 
        for r in parallel_results
    ])
    
    print(f"  → Merged {len(parallel_results)} parallel results")
    
    return {
        "research_result": merged_content,
        "messages": state.get("messages", []) + [
            {"role": "merger", "content": f"Merged results: {merged_content}"}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "parallel_merged"
    }


def complex_task_node(state: TaskState):
    """Handle complex tasks that require multiple processing steps"""
    print("\n  [Complex Task Node] Processing complex task with multiple steps...")
    task = state.get("task", "")
    
    # Complex tasks go through multiple processing steps
    result = f"Complex task processed: {task}\n"
    result += "Step 1: Initial analysis completed\n"
    result += "Step 2: Data gathering completed\n"
    result += "Step 3: Synthesis completed"
    
    return {
        "research_result": result,
        "calculation_result": "N/A for complex task",
        "writing_result": result,
        "analysis_result": result,
        "messages": state.get("messages", []) + [
            {"role": "complex_processor", "content": result}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "complex_completed"
    }


def aggregate_results_node(state: TaskState):
    """Aggregate all results into final output"""
    print("\n  [Aggregator] Aggregating all results...")
    
    results = []
    if state.get("research_result"):
        results.append(f"Research: {state['research_result'][:200]}...")
    if state.get("calculation_result"):
        results.append(f"Calculation: {state['calculation_result'][:200]}...")
    if state.get("writing_result"):
        results.append(f"Writing: {state['writing_result'][:200]}...")
    if state.get("analysis_result"):
        results.append(f"Analysis: {state['analysis_result'][:200]}...")
    
    final_result = "\n\n".join(results) if results else "No results to aggregate"
    
    print(f"  → Aggregated {len(results)} result types")
    
    return {
        "final_result": final_result,
        "messages": state.get("messages", []) + [
            {"role": "aggregator", "content": f"Final aggregated result: {final_result[:300]}..."}
        ],
        "step_count": state.get("step_count", 0) + 1,
        "status": "completed"
    }


def route_by_task_type(state: TaskState) -> Literal["research", "calculation", "writing", "analysis", "complex", "parallel"]:
    """Route to appropriate processing node based on task type"""
    task_type = state.get("task_type", "analysis")
    print(f"\n  → Routing to: {task_type} processing")
    
    if task_type == "complex":
        return "complex"
    elif "parallel" in state.get("task", "").lower() or "multiple" in state.get("task", "").lower():
        return "parallel"
    else:
        return task_type


def route_after_parallel(state: TaskState) -> Literal["merge", "aggregate"]:
    """Route after parallel processing"""
    parallel_results = state.get("parallel_results", [])
    if len(parallel_results) >= 2:
        return "merge"
    else:
        return "aggregate"


def route_after_processing(state: TaskState) -> Literal["aggregate", "error"]:
    """Route after processing - check for errors"""
    error = state.get("error", "")
    if error:
        return "error"
    return "aggregate"


def error_handler_node(state: TaskState):
    """Handle errors in the workflow"""
    print("\n  [Error Handler] Handling error...")
    error = state.get("error", "Unknown error")
    
    return {
        "messages": state.get("messages", []) + [
            {"role": "error_handler", "content": f"Error handled: {error}"}
        ],
        "final_result": f"Error occurred: {error}",
        "status": "error_handled",
        "step_count": state.get("step_count", 0) + 1
    }


def create_demo_workflow():
    """Create the main demo workflow"""
    print("="*60)
    print("LangGraph Demo System - Intelligent Task Processing")
    print("="*60)
    
    # Build the workflow graph
    workflow = StateGraph(TaskState)
    
    # Add nodes
    workflow.add_node("classify", classify_task_node)
    workflow.add_node("research", research_node)
    workflow.add_node("calculation", calculation_node)
    workflow.add_node("writing", writing_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("complex", complex_task_node)
    workflow.add_node("parallel_research_1", parallel_research_node)
    workflow.add_node("parallel_research_2", parallel_research_node_2)
    workflow.add_node("merge_parallel", merge_parallel_results_node)
    workflow.add_node("aggregate", aggregate_results_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add conditional routing from classify
    workflow.add_conditional_edges(
        "classify",
        route_by_task_type,
        {
            "research": "research",
            "calculation": "calculation",
            "writing": "writing",
            "analysis": "analysis",
            "complex": "complex",
            "parallel": "parallel_research_1"
        }
    )
    
    # Parallel processing edges
    workflow.add_edge("parallel_research_1", "parallel_research_2")
    workflow.add_conditional_edges(
        "parallel_research_2",
        route_after_parallel,
        {
            "merge": "merge_parallel",
            "aggregate": "aggregate"
        }
    )
    workflow.add_edge("merge_parallel", "aggregate")
    
    # Processing nodes route to aggregate
    workflow.add_conditional_edges(
        "research",
        route_after_processing,
        {
            "aggregate": "aggregate",
            "error": "error_handler"
        }
    )
    workflow.add_conditional_edges(
        "calculation",
        route_after_processing,
        {
            "aggregate": "aggregate",
            "error": "error_handler"
        }
    )
    workflow.add_conditional_edges(
        "writing",
        route_after_processing,
        {
            "aggregate": "aggregate",
            "error": "error_handler"
        }
    )
    workflow.add_conditional_edges(
        "analysis",
        route_after_processing,
        {
            "aggregate": "aggregate",
            "error": "error_handler"
        }
    )
    workflow.add_edge("complex", "aggregate")
    
    # Error handler and aggregate route to END
    workflow.add_edge("error_handler", END)
    workflow.add_edge("aggregate", END)
    
    return workflow.compile()


def run_demo_examples():
    """Run multiple demo examples"""
    app = create_demo_workflow()
    
    # Example tasks
    examples = [
        {
            "task": "Research the latest developments in artificial intelligence",
            "description": "Research Task"
        },
        {
            "task": "Calculate the compound interest for $1000 at 5% for 10 years",
            "description": "Calculation Task"
        },
        {
            "task": "Write a blog post about Python programming",
            "description": "Writing Task"
        },
        {
            "task": "Analyze the impact of cloud computing on businesses",
            "description": "Analysis Task"
        },
        {
            "task": "Research multiple aspects of machine learning and analyze the results",
            "description": "Complex/Parallel Task"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print("\n" + "="*60)
        print(f"Example {i}: {example['description']}")
        print(f"Task: {example['task']}")
        print("="*60)
        
        initial_state: TaskState = {
            "task": example["task"],
            "task_type": "",
            "messages": [],
            "research_result": "",
            "calculation_result": "",
            "writing_result": "",
            "analysis_result": "",
            "parallel_results": [],
            "final_result": "",
            "step_count": 0,
            "error": "",
            "status": ""
        }
        
        try:
            result = app.invoke(initial_state)
            
            print("\n" + "-"*60)
            print("Final Results:")
            print("-"*60)
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Steps executed: {result.get('step_count', 0)}")
            print(f"Task type: {result.get('task_type', 'unknown')}")
            print(f"\nFinal Result Preview:")
            print(result.get('final_result', 'No result')[:500])
            print(f"\nTotal messages: {len(result.get('messages', []))}")
            print("-"*60)
            
        except Exception as e:
            print(f"\nError executing example: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n")


def interactive_demo():
    """Interactive demo mode"""
    print("="*60)
    print("LangGraph Demo System - Interactive Mode")
    print("="*60)
    print("Enter tasks to process. Type 'exit' to quit.\n")
    
    app = create_demo_workflow()
    
    while True:
        try:
            user_task = input("\nEnter task: ").strip()
            if user_task.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not user_task:
                continue
            
            initial_state: TaskState = {
                "task": user_task,
                "task_type": "",
                "messages": [],
                "research_result": "",
                "calculation_result": "",
                "writing_result": "",
                "analysis_result": "",
                "parallel_results": [],
                "final_result": "",
                "step_count": 0,
                "error": "",
                "status": ""
            }
            
            print("\nProcessing task...")
            result = app.invoke(initial_state)
            
            print(f"\n✓ Task completed!")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Steps: {result.get('step_count', 0)}")
            print(f"  Type: {result.get('task_type', 'unknown')}")
            print(f"\n  Result: {result.get('final_result', 'No result')[:300]}...")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


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
        print()
    
    try:
        run_demo_examples()
        
        print("="*60)
        print("All demo examples completed successfully!")
        print("="*60)
        print("\nTo run interactive mode, uncomment interactive_demo() in the code.")
        # Uncomment to run interactive mode:
        # interactive_demo()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
