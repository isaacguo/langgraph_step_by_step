"""
Runtime Safety - Telemetry Pipeline
Demonstrates comprehensive telemetry, trace capture, and metrics collection
"""

import os
import time
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime

# Load environment variables
load_dotenv()


class TelemetryState(TypedDict):
    messages: Annotated[List[Dict], "messages"]
    telemetry_data: Annotated[List[Dict], "collected telemetry"]
    reasoning_traces: Annotated[List[Dict], "agent reasoning traces"]
    metrics: Dict[str, Any]
    health_status: str
    step_count: int


def reasoning_trace_capture():
    """Capture agent reasoning traces"""
    print("=" * 60)
    print("Example 1: Reasoning Trace Capture")
    print("=" * 60)
    
    def capture_trace_node(state: TelemetryState):
        """Capture reasoning trace"""
        print("  [Telemetry] Capturing reasoning trace...")
        step = state.get("step_count", 0) + 1
        
        trace = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "node": "capture_trace",
            "reasoning": f"Processing step {step}",
            "decisions": ["Decision A", "Decision B"],
            "confidence": 0.85
        }
        
        reasoning_traces = state.get("reasoning_traces", [])
        
        return {
            "reasoning_traces": reasoning_traces + [trace],
            "step_count": step
        }
    
    def process_node(state: TelemetryState):
        """Process with trace capture"""
        print("  [Process] Processing with telemetry...")
        trace = {
            "timestamp": datetime.now().isoformat(),
            "step": state.get("step_count", 0) + 1,
            "node": "process",
            "reasoning": "Executing main processing logic",
            "decisions": ["Process data", "Validate output"],
            "confidence": 0.90
        }
        
        reasoning_traces = state.get("reasoning_traces", [])
        
        return {
            "reasoning_traces": reasoning_traces + [trace],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(TelemetryState)
    workflow.add_node("capture", capture_trace_node)
    workflow.add_node("process", process_node)
    
    workflow.set_entry_point("capture")
    workflow.add_edge("capture", "process")
    workflow.add_edge("process", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "telemetry_data": [],
        "reasoning_traces": [],
        "metrics": {},
        "health_status": "healthy",
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nCaptured {len(result['reasoning_traces'])} reasoning traces")
    for i, trace in enumerate(result["reasoning_traces"], 1):
        print(f"  Trace {i}: {trace['node']} - {trace['reasoning']}")
    print()


def simulation_telemetry_collection():
    """Collect simulation telemetry"""
    print("=" * 60)
    print("Example 2: Simulation Telemetry Collection")
    print("=" * 60)
    
    def collect_simulation_telemetry_node(state: TelemetryState):
        """Collect simulation telemetry"""
        print("  [Telemetry] Collecting simulation telemetry...")
        
        # Simulate telemetry collection
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "simulation_id": "sim_001",
            "iteration": state.get("step_count", 0) + 1,
            "metrics": {
                "execution_time": 0.5,
                "memory_usage": 128,
                "cpu_usage": 45.2,
                "success": True
            },
            "events": ["start", "process", "validate"]
        }
        
        telemetry_data = state.get("telemetry_data", [])
        
        return {
            "telemetry_data": telemetry_data + [telemetry],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(TelemetryState)
    workflow.add_node("collect", collect_simulation_telemetry_node)
    workflow.set_entry_point("collect")
    workflow.add_edge("collect", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "telemetry_data": [],
        "reasoning_traces": [],
        "metrics": {},
        "health_status": "healthy",
        "step_count": 0
    }
    
    # Collect multiple telemetry points
    result = initial_state
    for i in range(3):
        result = app.invoke(result)
    
    print(f"\nCollected {len(result['telemetry_data'])} telemetry points")
    for i, tel in enumerate(result["telemetry_data"], 1):
        print(f"  Point {i}: Iteration {tel['iteration']}, Success: {tel['metrics']['success']}")
    print()


def orchestration_health_metrics():
    """Collect orchestration health metrics"""
    print("=" * 60)
    print("Example 3: Orchestration Health Metrics")
    print("=" * 60)
    
    def collect_health_metrics_node(state: TelemetryState):
        """Collect health metrics"""
        print("  [Health Metrics] Collecting health metrics...")
        
        # Calculate health metrics
        step_count = state.get("step_count", 0)
        telemetry_count = len(state.get("telemetry_data", []))
        trace_count = len(state.get("reasoning_traces", []))
        
        # Determine health status
        if step_count > 0 and telemetry_count > 0:
            health_status = "healthy"
        elif step_count > 0:
            health_status = "degraded"
        else:
            health_status = "unknown"
        
        metrics = {
            "step_count": step_count,
            "telemetry_points": telemetry_count,
            "reasoning_traces": trace_count,
            "timestamp": datetime.now().isoformat(),
            "health_score": 1.0 if health_status == "healthy" else 0.7
        }
        
        return {
            "metrics": metrics,
            "health_status": health_status,
            "step_count": step_count + 1
        }
    
    workflow = StateGraph(TelemetryState)
    workflow.add_node("collect_health", collect_health_metrics_node)
    workflow.set_entry_point("collect_health")
    workflow.add_edge("collect_health", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "telemetry_data": [{"test": "data"}],
        "reasoning_traces": [{"test": "trace"}],
        "metrics": {},
        "health_status": "unknown",
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nHealth metrics:")
    print(f"  Health status: {result['health_status']}")
    print(f"  Health score: {result['metrics'].get('health_score', 0):.2f}")
    print(f"  Metrics: {result['metrics']}")
    print()


def unified_telemetry_aggregation():
    """Aggregate telemetry from multiple sources"""
    print("=" * 60)
    print("Example 4: Unified Telemetry Aggregation")
    print("=" * 60)
    
    def aggregate_telemetry_node(state: TelemetryState):
        """Aggregate telemetry from multiple sources"""
        print("  [Aggregation] Aggregating telemetry...")
        
        telemetry_data = state.get("telemetry_data", [])
        reasoning_traces = state.get("reasoning_traces", [])
        metrics = state.get("metrics", {})
        
        # Aggregate all telemetry
        aggregated = {
            "timestamp": datetime.now().isoformat(),
            "sources": {
                "telemetry_points": len(telemetry_data),
                "reasoning_traces": len(reasoning_traces),
                "metrics": len(metrics)
            },
            "summary": {
                "total_events": len(telemetry_data) + len(reasoning_traces),
                "health_status": state.get("health_status", "unknown"),
                "average_confidence": sum(
                    t.get("confidence", 0) for t in reasoning_traces
                ) / len(reasoning_traces) if reasoning_traces else 0.0
            }
        }
        
        return {
            "telemetry_data": telemetry_data + [aggregated],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(TelemetryState)
    workflow.add_node("aggregate", aggregate_telemetry_node)
    workflow.set_entry_point("aggregate")
    workflow.add_edge("aggregate", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "telemetry_data": [
            {"source": "simulation", "value": 1},
            {"source": "simulation", "value": 2}
        ],
        "reasoning_traces": [
            {"node": "node1", "confidence": 0.8},
            {"node": "node2", "confidence": 0.9}
        ],
        "metrics": {"metric1": 10, "metric2": 20},
        "health_status": "healthy",
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nAggregated telemetry:")
    aggregated = result["telemetry_data"][-1]
    print(f"  Sources: {aggregated['sources']}")
    print(f"  Total events: {aggregated['summary']['total_events']}")
    print(f"  Average confidence: {aggregated['summary']['average_confidence']:.2f}")
    print()


def real_time_telemetry_streaming():
    """Real-time telemetry streaming"""
    print("=" * 60)
    print("Example 5: Real-Time Telemetry Streaming")
    print("=" * 60)
    
    def stream_telemetry_node(state: TelemetryState):
        """Stream telemetry in real-time"""
        print("  [Streaming] Streaming telemetry...")
        
        # Simulate real-time streaming
        stream_data = {
            "timestamp": datetime.now().isoformat(),
            "stream_id": f"stream_{state.get('step_count', 0)}",
            "data": {
                "current_step": state.get("step_count", 0),
                "latency_ms": 45,
                "throughput": 100
            },
            "streaming": True
        }
        
        telemetry_data = state.get("telemetry_data", [])
        
        return {
            "telemetry_data": telemetry_data + [stream_data],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(TelemetryState)
    workflow.add_node("stream", stream_telemetry_node)
    workflow.set_entry_point("stream")
    workflow.add_edge("stream", END)
    
    app = workflow.compile()
    
    initial_state = {
        "messages": [],
        "telemetry_data": [],
        "reasoning_traces": [],
        "metrics": {},
        "health_status": "healthy",
        "step_count": 0
    }
    
    # Stream multiple points
    print("Streaming telemetry points...")
    result = initial_state
    for i in range(3):
        time.sleep(0.1)  # Simulate real-time delay
        result = app.invoke(result)
        stream_point = result["telemetry_data"][-1]
        print(f"  Stream {i+1}: {stream_point['data']}")
    
    print(f"\nTotal streamed points: {len(result['telemetry_data'])}")
    print()


if __name__ == "__main__":
    try:
        reasoning_trace_capture()
        simulation_telemetry_collection()
        orchestration_health_metrics()
        unified_telemetry_aggregation()
        real_time_telemetry_streaming()
        
        print("=" * 60)
        print("All telemetry pipeline examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

