"""
LangGraph Basics - Graph Visualization
Demonstrates visualizing graph structure and execution flow
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list, "list of messages"]
    step_count: int
    path_taken: Annotated[list, "execution path"]


def visualize_simple_graph():
    """Create and visualize a simple graph"""
    print("=" * 60)
    print("Example 1: Simple Graph Visualization")
    print("=" * 60)
    
    def node_a(state: GraphState):
        return {
            "step_count": state.get("step_count", 0) + 1,
            "path_taken": state.get("path_taken", []) + ["A"]
        }
    
    def node_b(state: GraphState):
        return {
            "step_count": state["step_count"] + 1,
            "path_taken": state["path_taken"] + ["B"]
        }
    
    def node_c(state: GraphState):
        return {
            "step_count": state["step_count"] + 1,
            "path_taken": state["path_taken"] + ["C"]
        }
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("A", node_a)
    workflow.add_node("B", node_b)
    workflow.add_node("C", node_c)
    
    workflow.set_entry_point("A")
    workflow.add_edge("A", "B")
    workflow.add_edge("B", "C")
    workflow.add_edge("C", END)
    
    app = workflow.compile()
    
    # Get graph structure
    print("\nGraph Structure:")
    print("=" * 60)
    print("Nodes:", list(app.nodes.keys()))
    print("\nEdges:")
    for node in app.nodes:
        edges = app.edges.get(node, [])
        if edges:
            print(f"  {node} -> {edges}")
        else:
            print(f"  {node} -> END")
    
    # Visualize as text
    print("\nText Visualization:")
    print("=" * 60)
    print("START -> A -> B -> C -> END")
    
    # Execute and show path
    result = app.invoke({"messages": [], "step_count": 0, "path_taken": []})
    print(f"\nExecution Path: {' -> '.join(result['path_taken'])}")
    print(f"Total Steps: {result['step_count']}")
    print()


def visualize_conditional_graph():
    """Visualize graph with conditional edges"""
    print("=" * 60)
    print("Example 2: Conditional Graph Visualization")
    print("=" * 60)
    
    def start_node(state: GraphState):
        return {
            "step_count": state.get("step_count", 0) + 1,
            "path_taken": state.get("path_taken", []) + ["START"]
        }
    
    def path_x_node(state: GraphState):
        return {
            "step_count": state["step_count"] + 1,
            "path_taken": state["path_taken"] + ["X"]
        }
    
    def path_y_node(state: GraphState):
        return {
            "step_count": state["step_count"] + 1,
            "path_taken": state["path_taken"] + ["Y"]
        }
    
    def route_decision(state: GraphState) -> Literal["x", "y"]:
        # Simple routing based on step count
        return "x" if state["step_count"] % 2 == 0 else "y"
    
    # Build graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("start", start_node)
    workflow.add_node("path_x", path_x_node)
    workflow.add_node("path_y", path_y_node)
    
    workflow.set_entry_point("start")
    workflow.add_conditional_edges(
        "start",
        route_decision,
        {
            "x": "path_x",
            "y": "path_y"
        }
    )
    workflow.add_edge("path_x", END)
    workflow.add_edge("path_y", END)
    
    app = workflow.compile()
    
    print("\nGraph Structure:")
    print("=" * 60)
    print("""
    START
      |
      v
    start
      |
      +--[condition]--+
      |              |
      v              v
    path_x        path_y
      |              |
      +------+-------+
             |
            END
    """)
    
    # Execute multiple times to see different paths
    print("\nExecution Paths:")
    for i in range(3):
        result = app.invoke({"messages": [], "step_count": i, "path_taken": []})
        print(f"  Run {i+1}: {' -> '.join(result['path_taken'])}")
    print()


def visualize_complex_graph():
    """Visualize a more complex graph structure"""
    print("=" * 60)
    print("Example 3: Complex Graph Visualization")
    print("=" * 60)
    
    def create_node(name):
        def node(state: GraphState):
            return {
                "step_count": state.get("step_count", 0) + 1,
                "path_taken": state.get("path_taken", []) + [name]
            }
        return node
    
    # Build complex graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    for name in ["A", "B", "C", "D", "E", "F"]:
        workflow.add_node(name, create_node(name))
    
    # Define edges
    workflow.set_entry_point("A")
    workflow.add_edge("A", "B")
    workflow.add_edge("A", "C")
    workflow.add_edge("B", "D")
    workflow.add_edge("C", "E")
    workflow.add_edge("D", "F")
    workflow.add_edge("E", "F")
    workflow.add_edge("F", END)
    
    app = workflow.compile()
    
    print("\nGraph Structure:")
    print("=" * 60)
    print("""
         START
           |
           v
           A
          / \\
         v   v
         B   C
         |   |
         v   v
         D   E
          \\ /
           v
           F
           |
          END
    """)
    
    print("\nNode Details:")
    for node_name in app.nodes:
        edges = app.edges.get(node_name, [])
        print(f"  {node_name}: {len(edges)} outgoing edge(s)")
    
    # Note: In a real scenario, both B->D and C->E would execute
    # but the graph structure shows the branching
    print()


def export_graph_schema():
    """Export graph schema for documentation"""
    print("=" * 60)
    print("Example 4: Graph Schema Export")
    print("=" * 60)
    
    def node1(state: GraphState):
        return state
    
    def node2(state: GraphState):
        return state
    
    workflow = StateGraph(GraphState)
    workflow.add_node("node1", node1)
    workflow.add_node("node2", node2)
    workflow.set_entry_point("node1")
    workflow.add_edge("node1", "node2")
    workflow.add_edge("node2", END)
    
    app = workflow.compile()
    
    print("\nGraph Schema:")
    print("=" * 60)
    print(f"Entry Point: {app.get_graph().first}")
    print(f"Nodes: {list(app.nodes.keys())}")
    print(f"Edges: {dict(app.edges)}")
    
    # Get graph representation
    graph_dict = app.get_graph().to_json()
    print(f"\nGraph JSON (first 500 chars):")
    print(str(graph_dict)[:500] + "...")
    print()


if __name__ == "__main__":
    try:
        visualize_simple_graph()
        visualize_conditional_graph()
        visualize_complex_graph()
        export_graph_schema()
        
        print("=" * 60)
        print("All visualization examples completed successfully!")
        print("=" * 60)
        print("\nNote: For interactive visualization, consider using:")
        print("  - LangGraph Studio")
        print("  - Graphviz (pip install graphviz)")
        print("  - NetworkX for network analysis")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

