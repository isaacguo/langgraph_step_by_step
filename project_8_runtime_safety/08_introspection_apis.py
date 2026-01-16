"""
Runtime Safety - Introspection APIs
Demonstrates decision rationale APIs, safety metrics exposure, and diagnostics
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime

# Load environment variables
load_dotenv()


class IntrospectionState(TypedDict):
    decisions: Annotated[List[Dict], "decision history"]
    decision_rationale: Dict[str, Any]
    safety_metrics: Dict[str, Any]
    diagnostics: Dict[str, Any]
    api_responses: Annotated[List[Dict], "API response cache"]
    step_count: int


def decision_rationale_api():
    """API to expose decision rationale"""
    print("=" * 60)
    print("Example 1: Decision Rationale API")
    print("=" * 60)
    
    def make_decision_node(state: IntrospectionState):
        """Make a decision with rationale"""
        print("  [Decision] Making decision with rationale...")
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "decision_id": f"decision_{state.get('step_count', 0)}",
            "action": "process_data",
            "rationale": {
                "reasoning": "Data validation passed, proceeding with processing",
                "alternatives_considered": ["skip", "delay", "process"],
                "chosen_alternative": "process",
                "confidence": 0.85,
                "factors": ["data_quality", "system_load", "priority"]
            },
            "outcome": "success"
        }
        
        decisions = state.get("decisions", [])
        
        return {
            "decisions": decisions + [decision],
            "decision_rationale": decision["rationale"],
            "step_count": state.get("step_count", 0) + 1
        }
    
    def expose_rationale_node(state: IntrospectionState):
        """Expose decision rationale via API"""
        print("  [API] Exposing decision rationale...")
        latest_decision = state.get("decisions", [])[-1] if state.get("decisions") else None
        
        if latest_decision:
            api_response = {
                "endpoint": "/api/v1/decisions/rationale",
                "decision_id": latest_decision["decision_id"],
                "rationale": latest_decision["rationale"],
                "timestamp": latest_decision["timestamp"]
            }
            
            return {
                "api_responses": state.get("api_responses", []) + [api_response],
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IntrospectionState)
    workflow.add_node("make_decision", make_decision_node)
    workflow.add_node("expose_rationale", expose_rationale_node)
    
    workflow.set_entry_point("make_decision")
    workflow.add_edge("make_decision", "expose_rationale")
    workflow.add_edge("expose_rationale", END)
    
    app = workflow.compile()
    
    initial_state = {
        "decisions": [],
        "decision_rationale": {},
        "safety_metrics": {},
        "diagnostics": {},
        "api_responses": [],
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nDecision rationale API result:")
    if result.get("api_responses"):
        response = result["api_responses"][-1]
        print(f"  Endpoint: {response['endpoint']}")
        print(f"  Decision ID: {response['decision_id']}")
        print(f"  Rationale: {response['rationale']['reasoning']}")
        print(f"  Confidence: {response['rationale']['confidence']}")
    print()


def safety_metrics_exposure():
    """Expose safety metrics via API"""
    print("=" * 60)
    print("Example 2: Safety Metrics Exposure")
    print("=" * 60)
    
    def collect_metrics_node(state: IntrospectionState):
        """Collect safety metrics"""
        print("  [Metrics] Collecting safety metrics...")
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "safety_score": 0.92,
            "policy_compliance": 0.95,
            "error_rate": 0.02,
            "anomaly_count": 1,
            "drift_detected": False,
            "misalignment_detected": False,
            "confidence_score": 0.88
        }
        
        return {
            "safety_metrics": metrics,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def expose_metrics_node(state: IntrospectionState):
        """Expose metrics via API"""
        print("  [API] Exposing safety metrics...")
        metrics = state.get("safety_metrics", {})
        
        api_response = {
            "endpoint": "/api/v1/metrics/safety",
            "metrics": metrics,
            "format": "json"
        }
        
        return {
            "api_responses": state.get("api_responses", []) + [api_response],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IntrospectionState)
    workflow.add_node("collect_metrics", collect_metrics_node)
    workflow.add_node("expose_metrics", expose_metrics_node)
    
    workflow.set_entry_point("collect_metrics")
    workflow.add_edge("collect_metrics", "expose_metrics")
    workflow.add_edge("expose_metrics", END)
    
    app = workflow.compile()
    
    initial_state = {
        "decisions": [],
        "decision_rationale": {},
        "safety_metrics": {},
        "diagnostics": {},
        "api_responses": [],
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nSafety metrics API result:")
    if result.get("api_responses"):
        response = result["api_responses"][-1]
        print(f"  Endpoint: {response['endpoint']}")
        print(f"  Safety Score: {response['metrics'].get('safety_score', 0):.2f}")
        print(f"  Policy Compliance: {response['metrics'].get('policy_compliance', 0):.2f}")
        print(f"  Error Rate: {response['metrics'].get('error_rate', 0):.2f}")
    print()


def performance_diagnostics():
    """Performance diagnostics API"""
    print("=" * 60)
    print("Example 3: Performance Diagnostics")
    print("=" * 60)
    
    def collect_diagnostics_node(state: IntrospectionState):
        """Collect performance diagnostics"""
        print("  [Diagnostics] Collecting performance diagnostics...")
        
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "avg_latency_ms": 45,
                "p95_latency_ms": 120,
                "p99_latency_ms": 200,
                "throughput": 100,
                "error_rate": 0.01
            },
            "resource_usage": {
                "cpu_percent": 45.2,
                "memory_mb": 512,
                "disk_io_mb": 10.5
            },
            "health": {
                "status": "healthy",
                "uptime_seconds": 3600,
                "last_error": None
            }
        }
        
        return {
            "diagnostics": diagnostics,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def expose_diagnostics_node(state: IntrospectionState):
        """Expose diagnostics via API"""
        print("  [API] Exposing diagnostics...")
        diagnostics = state.get("diagnostics", {})
        
        api_response = {
            "endpoint": "/api/v1/diagnostics/performance",
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "api_responses": state.get("api_responses", []) + [api_response],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IntrospectionState)
    workflow.add_node("collect_diagnostics", collect_diagnostics_node)
    workflow.add_node("expose_diagnostics", expose_diagnostics_node)
    
    workflow.set_entry_point("collect_diagnostics")
    workflow.add_edge("collect_diagnostics", "expose_diagnostics")
    workflow.add_edge("expose_diagnostics", END)
    
    app = workflow.compile()
    
    initial_state = {
        "decisions": [],
        "decision_rationale": {},
        "safety_metrics": {},
        "diagnostics": {},
        "api_responses": [],
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nPerformance diagnostics API result:")
    if result.get("api_responses"):
        response = result["api_responses"][-1]
        print(f"  Endpoint: {response['endpoint']}")
        perf = response["diagnostics"].get("performance", {})
        print(f"  Avg Latency: {perf.get('avg_latency_ms', 0)}ms")
        print(f"  Throughput: {perf.get('throughput', 0)} req/s")
        print(f"  Health Status: {response['diagnostics'].get('health', {}).get('status', 'unknown')}")
    print()


def real_time_dashboard_data():
    """Real-time dashboard data API"""
    print("=" * 60)
    print("Example 4: Real-Time Dashboard Data")
    print("=" * 60)
    
    def generate_dashboard_data_node(state: IntrospectionState):
        """Generate dashboard data"""
        print("  [Dashboard] Generating dashboard data...")
        
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_decisions": len(state.get("decisions", [])),
                "safety_score": state.get("safety_metrics", {}).get("safety_score", 0.0),
                "system_health": "healthy"
            },
            "recent_activity": [
                {"time": "10:00", "event": "Decision made", "status": "success"},
                {"time": "10:01", "event": "Metrics updated", "status": "success"},
                {"time": "10:02", "event": "Diagnostics collected", "status": "success"}
            ],
            "alerts": [],
            "trends": {
                "safety_score_trend": "stable",
                "error_rate_trend": "decreasing"
            }
        }
        
        api_response = {
            "endpoint": "/api/v1/dashboard/realtime",
            "data": dashboard_data,
            "update_frequency": "1s"
        }
        
        return {
            "api_responses": state.get("api_responses", []) + [api_response],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IntrospectionState)
    workflow.add_node("generate_dashboard", generate_dashboard_data_node)
    workflow.set_entry_point("generate_dashboard")
    workflow.add_edge("generate_dashboard", END)
    
    app = workflow.compile()
    
    initial_state = {
        "decisions": [{"test": "decision1"}, {"test": "decision2"}],
        "decision_rationale": {},
        "safety_metrics": {"safety_score": 0.92},
        "diagnostics": {},
        "api_responses": [],
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nDashboard data API result:")
    if result.get("api_responses"):
        response = result["api_responses"][-1]
        print(f"  Endpoint: {response['endpoint']}")
        summary = response["data"].get("summary", {})
        print(f"  Total Decisions: {summary.get('total_decisions', 0)}")
        print(f"  Safety Score: {summary.get('safety_score', 0):.2f}")
        print(f"  System Health: {summary.get('system_health', 'unknown')}")
    print()


def comprehensive_introspection_api():
    """Comprehensive introspection API combining all features"""
    print("=" * 60)
    print("Example 5: Comprehensive Introspection API")
    print("=" * 60)
    
    def comprehensive_api_node(state: IntrospectionState):
        """Comprehensive introspection API"""
        print("  [Comprehensive API] Generating comprehensive introspection data...")
        
        api_response = {
            "endpoint": "/api/v1/introspection/comprehensive",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "decisions": {
                    "total": len(state.get("decisions", [])),
                    "recent": state.get("decisions", [])[-5:] if state.get("decisions") else []
                },
                "safety_metrics": state.get("safety_metrics", {}),
                "diagnostics": state.get("diagnostics", {}),
                "system_status": {
                    "health": "healthy",
                    "uptime": 3600,
                    "version": "1.0.0"
                }
            }
        }
        
        return {
            "api_responses": state.get("api_responses", []) + [api_response],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(IntrospectionState)
    workflow.add_node("comprehensive_api", comprehensive_api_node)
    workflow.set_entry_point("comprehensive_api")
    workflow.add_edge("comprehensive_api", END)
    
    app = workflow.compile()
    
    initial_state = {
        "decisions": [{"id": "1"}, {"id": "2"}],
        "decision_rationale": {"reasoning": "Test reasoning"},
        "safety_metrics": {"safety_score": 0.92, "error_rate": 0.01},
        "diagnostics": {"performance": {"latency": 45}},
        "api_responses": [],
        "step_count": 0
    }
    
    result = app.invoke(initial_state)
    print(f"\nComprehensive introspection API result:")
    if result.get("api_responses"):
        response = result["api_responses"][-1]
        print(f"  Endpoint: {response['endpoint']}")
        data = response["data"]
        print(f"  Total Decisions: {data['decisions']['total']}")
        print(f"  Safety Score: {data['safety_metrics'].get('safety_score', 0):.2f}")
        print(f"  System Health: {data['system_status']['health']}")
    print()


if __name__ == "__main__":
    try:
        decision_rationale_api()
        safety_metrics_exposure()
        performance_diagnostics()
        real_time_dashboard_data()
        comprehensive_introspection_api()
        
        print("=" * 60)
        print("All introspection API examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

