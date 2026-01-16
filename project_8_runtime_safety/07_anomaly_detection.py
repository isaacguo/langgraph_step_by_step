"""
Runtime Safety - Anomaly Detection
Demonstrates drift detection, misalignment monitoring, and confidence-scored safety gating
"""

import os
import statistics
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Literal
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class AnomalyState(TypedDict):
    telemetry_data: Annotated[List[Dict], "telemetry data"]
    baseline_metrics: Dict[str, float]
    detected_anomalies: Annotated[List[Dict], "detected anomalies"]
    drift_detected: bool
    misalignment_detected: bool
    policy_violations: Annotated[List[str], "policy violations"]
    safety_gate_status: str
    confidence_score: float
    step_count: int


def statistical_drift_detection():
    """Detect statistical drift in metrics"""
    print("=" * 60)
    print("Example 1: Statistical Drift Detection")
    print("=" * 60)
    
    def detect_drift_node(state: AnomalyState):
        """Detect statistical drift"""
        print("  [Drift Detection] Analyzing for drift...")
        baseline = state.get("baseline_metrics", {})
        telemetry = state.get("telemetry_data", [])
        
        if not baseline or not telemetry:
            return {
                "drift_detected": False,
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Extract current metrics
        current_metrics = {}
        for tel in telemetry[-5:]:  # Last 5 points
            if "metrics" in tel:
                for key, value in tel["metrics"].items():
                    if isinstance(value, (int, float)):
                        if key not in current_metrics:
                            current_metrics[key] = []
                        current_metrics[key].append(value)
        
        # Calculate drift
        drift_detected = False
        anomalies = []
        
        for metric_name, baseline_value in baseline.items():
            if metric_name in current_metrics:
                current_values = current_metrics[metric_name]
                current_mean = statistics.mean(current_values)
                
                # Drift if current mean deviates by more than 20% from baseline
                threshold = baseline_value * 0.2
                if abs(current_mean - baseline_value) > threshold:
                    drift_detected = True
                    anomalies.append({
                        "metric": metric_name,
                        "baseline": baseline_value,
                        "current": current_mean,
                        "drift": abs(current_mean - baseline_value)
                    })
        
        return {
            "drift_detected": drift_detected,
            "detected_anomalies": state.get("detected_anomalies", []) + anomalies,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(AnomalyState)
    workflow.add_node("detect_drift", detect_drift_node)
    workflow.set_entry_point("detect_drift")
    workflow.add_edge("detect_drift", END)
    
    app = workflow.compile()
    
    # Test with baseline and current data
    test_case = {
        "telemetry_data": [
            {"metrics": {"latency": 50}},
            {"metrics": {"latency": 55}},
            {"metrics": {"latency": 60}},
            {"metrics": {"latency": 65}},
            {"metrics": {"latency": 70}}  # Drifting upward
        ],
        "baseline_metrics": {"latency": 40},  # Baseline is 40
        "detected_anomalies": [],
        "drift_detected": False,
        "misalignment_detected": False,
        "policy_violations": [],
        "safety_gate_status": "open",
        "confidence_score": 0.0,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nDrift detection result:")
    print(f"  Drift detected: {result['drift_detected']}")
    if result.get("detected_anomalies"):
        for anomaly in result["detected_anomalies"]:
            print(f"  Anomaly: {anomaly['metric']} - Baseline: {anomaly['baseline']:.2f}, Current: {anomaly['current']:.2f}")
    print()


def misalignment_detection():
    """Detect misalignment in agent behavior"""
    print("=" * 60)
    print("Example 2: Misalignment Detection")
    print("=" * 60)
    
    def detect_misalignment_node(state: AnomalyState):
        """Detect misalignment"""
        print("  [Misalignment Detection] Checking for misalignment...")
        telemetry = state.get("telemetry_data", [])
        
        # Expected behavior pattern
        expected_pattern = {
            "success_rate": 0.95,  # Expected 95% success
            "response_time": 100,  # Expected response time
            "confidence": 0.85  # Expected confidence
        }
        
        # Analyze recent telemetry
        misalignment_detected = False
        violations = []
        
        for tel in telemetry[-3:]:  # Last 3 points
            if "metrics" in tel:
                metrics = tel["metrics"]
                
                # Check success rate
                if "success" in metrics:
                    if not metrics["success"] and expected_pattern["success_rate"] > 0.9:
                        misalignment_detected = True
                        violations.append("Success rate below expected")
                
                # Check response time
                if "response_time" in metrics:
                    if metrics["response_time"] > expected_pattern["response_time"] * 1.5:
                        misalignment_detected = True
                        violations.append("Response time exceeds threshold")
        
        return {
            "misalignment_detected": misalignment_detected,
            "policy_violations": state.get("policy_violations", []) + violations,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(AnomalyState)
    workflow.add_node("detect_misalignment", detect_misalignment_node)
    workflow.set_entry_point("detect_misalignment")
    workflow.add_edge("detect_misalignment", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "telemetry_data": [
                {"metrics": {"success": True, "response_time": 90}},
                {"metrics": {"success": True, "response_time": 95}},
                {"metrics": {"success": True, "response_time": 100}}
            ],
            "baseline_metrics": {},
            "detected_anomalies": [],
            "drift_detected": False,
            "misalignment_detected": False,
            "policy_violations": [],
            "safety_gate_status": "open",
            "confidence_score": 0.0,
            "step_count": 0
        },
        {
            "telemetry_data": [
                {"metrics": {"success": False, "response_time": 200}},  # Misaligned
                {"metrics": {"success": False, "response_time": 250}},
                {"metrics": {"success": False, "response_time": 300}}
            ],
            "baseline_metrics": {},
            "detected_anomalies": [],
            "drift_detected": False,
            "misalignment_detected": False,
            "policy_violations": [],
            "safety_gate_status": "open",
            "confidence_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = app.invoke(test_case)
        print(f"  Misalignment detected: {result['misalignment_detected']}")
        if result.get("policy_violations"):
            print(f"  Violations: {result['policy_violations']}")
    print()


def policy_violation_monitoring():
    """Monitor for policy violations"""
    print("=" * 60)
    print("Example 3: Policy Violation Monitoring")
    print("=" * 60)
    
    # Policy definitions
    POLICIES = {
        "max_latency": 200,
        "min_success_rate": 0.9,
        "max_error_rate": 0.1
    }
    
    def monitor_policies_node(state: AnomalyState):
        """Monitor policy violations"""
        print("  [Policy Monitor] Monitoring policies...")
        telemetry = state.get("telemetry_data", [])
        violations = []
        
        for tel in telemetry:
            if "metrics" in tel:
                metrics = tel["metrics"]
                
                # Check latency policy
                if "latency" in metrics and metrics["latency"] > POLICIES["max_latency"]:
                    violations.append(f"Latency {metrics['latency']} exceeds max {POLICIES['max_latency']}")
                
                # Check success rate
                if "success_rate" in metrics and metrics["success_rate"] < POLICIES["min_success_rate"]:
                    violations.append(f"Success rate {metrics['success_rate']} below min {POLICIES['min_success_rate']}")
                
                # Check error rate
                if "error_rate" in metrics and metrics["error_rate"] > POLICIES["max_error_rate"]:
                    violations.append(f"Error rate {metrics['error_rate']} exceeds max {POLICIES['max_error_rate']}")
        
        return {
            "policy_violations": state.get("policy_violations", []) + violations,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(AnomalyState)
    workflow.add_node("monitor", monitor_policies_node)
    workflow.set_entry_point("monitor")
    workflow.add_edge("monitor", END)
    
    app = workflow.compile()
    
    test_case = {
        "telemetry_data": [
            {"metrics": {"latency": 250, "success_rate": 0.85, "error_rate": 0.15}}  # Multiple violations
        ],
        "baseline_metrics": {},
        "detected_anomalies": [],
        "drift_detected": False,
        "misalignment_detected": False,
        "policy_violations": [],
        "safety_gate_status": "open",
        "confidence_score": 0.0,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nPolicy violations detected: {len(result['policy_violations'])}")
    for violation in result["policy_violations"]:
        print(f"  - {violation}")
    print()


def confidence_scored_safety_gating():
    """Confidence-scored safety gating"""
    print("=" * 60)
    print("Example 4: Confidence-Scored Safety Gating")
    print("=" * 60)
    
    def calculate_confidence_node(state: AnomalyState):
        """Calculate confidence score"""
        print("  [Confidence] Calculating confidence score...")
        
        # Factors affecting confidence
        drift_detected = state.get("drift_detected", False)
        misalignment = state.get("misalignment_detected", False)
        violations = len(state.get("policy_violations", []))
        anomalies = len(state.get("detected_anomalies", []))
        
        # Start with high confidence
        confidence = 1.0
        
        # Reduce confidence based on issues
        if drift_detected:
            confidence -= 0.2
        if misalignment:
            confidence -= 0.3
        confidence -= violations * 0.1
        confidence -= anomalies * 0.05
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "confidence_score": confidence,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def safety_gate_node(state: AnomalyState):
        """Apply safety gate based on confidence"""
        print("  [Safety Gate] Evaluating safety gate...")
        confidence = state.get("confidence_score", 1.0)
        
        # Gate thresholds
        if confidence >= 0.8:
            gate_status = "open"
        elif confidence >= 0.5:
            gate_status = "restricted"
        else:
            gate_status = "closed"
        
        return {
            "safety_gate_status": gate_status,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(AnomalyState)
    workflow.add_node("calculate_confidence", calculate_confidence_node)
    workflow.add_node("safety_gate", safety_gate_node)
    
    workflow.set_entry_point("calculate_confidence")
    workflow.add_edge("calculate_confidence", "safety_gate")
    workflow.add_edge("safety_gate", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "telemetry_data": [],
            "baseline_metrics": {},
            "detected_anomalies": [],
            "drift_detected": False,
            "misalignment_detected": False,
            "policy_violations": [],
            "safety_gate_status": "open",
            "confidence_score": 0.0,
            "step_count": 0
        },
        {
            "telemetry_data": [],
            "baseline_metrics": {},
            "detected_anomalies": [{"test": "anomaly"}],
            "drift_detected": True,
            "misalignment_detected": False,
            "policy_violations": ["violation1"],
            "safety_gate_status": "open",
            "confidence_score": 0.0,
            "step_count": 0
        },
        {
            "telemetry_data": [],
            "baseline_metrics": {},
            "detected_anomalies": [{"test": "anomaly1"}, {"test": "anomaly2"}],
            "drift_detected": True,
            "misalignment_detected": True,
            "policy_violations": ["violation1", "violation2", "violation3"],
            "safety_gate_status": "open",
            "confidence_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = app.invoke(test_case)
        print(f"  Confidence score: {result['confidence_score']:.2f}")
        print(f"  Safety gate status: {result['safety_gate_status']}")
    print()


def real_time_anomaly_alerting():
    """Real-time anomaly alerting"""
    print("=" * 60)
    print("Example 5: Real-Time Anomaly Alerting")
    print("=" * 60)
    
    def alert_on_anomaly_node(state: AnomalyState):
        """Alert on detected anomalies"""
        print("  [Alerting] Checking for anomalies...")
        anomalies = state.get("detected_anomalies", [])
        drift = state.get("drift_detected", False)
        misalignment = state.get("misalignment_detected", False)
        violations = state.get("policy_violations", [])
        
        alerts = []
        
        if drift:
            alerts.append({"level": "warning", "message": "Statistical drift detected"})
        
        if misalignment:
            alerts.append({"level": "critical", "message": "Misalignment detected"})
        
        if violations:
            alerts.append({"level": "warning", "message": f"{len(violations)} policy violations"})
        
        if anomalies:
            alerts.append({"level": "info", "message": f"{len(anomalies)} anomalies detected"})
        
        return {
            "alerts": state.get("alerts", []) + alerts,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(AnomalyState)
    workflow.add_node("alert", alert_on_anomaly_node)
    workflow.set_entry_point("alert")
    workflow.add_edge("alert", END)
    
    app = workflow.compile()
    
    test_case = {
        "telemetry_data": [],
        "baseline_metrics": {},
        "detected_anomalies": [{"metric": "latency", "drift": 50}],
        "drift_detected": True,
        "misalignment_detected": True,
        "policy_violations": ["Policy violation 1"],
        "safety_gate_status": "open",
        "confidence_score": 0.5,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nGenerated {len(result.get('alerts', []))} alerts")
    for alert in result.get("alerts", []):
        print(f"  [{alert['level'].upper()}] {alert['message']}")
    print()


if __name__ == "__main__":
    try:
        statistical_drift_detection()
        misalignment_detection()
        policy_violation_monitoring()
        confidence_scored_safety_gating()
        real_time_anomaly_alerting()
        
        print("=" * 60)
        print("All anomaly detection examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

