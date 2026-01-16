"""
Runtime Safety - Safety Scoring
Demonstrates safety score calculation, promotion gates, and runtime certification
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Literal
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class SafetyScoringState(TypedDict):
    safety_factors: Dict[str, float]
    safety_score: float
    promotion_gate_status: str
    certification_status: str
    trust_metrics: Dict[str, float]
    evaluation_history: Annotated[List[Dict], "evaluation history"]
    step_count: int


def safety_score_calculation():
    """Calculate comprehensive safety score"""
    print("=" * 60)
    print("Example 1: Safety Score Calculation")
    print("=" * 60)
    
    def calculate_safety_score_node(state: SafetyScoringState):
        """Calculate safety score from multiple factors"""
        print("  [Safety Score] Calculating safety score...")
        factors = state.get("safety_factors", {})
        
        # Weighted factors
        weights = {
            "policy_compliance": 0.3,
            "error_rate": 0.2,
            "anomaly_detection": 0.2,
            "intent_alignment": 0.15,
            "system_stability": 0.15
        }
        
        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0
        
        for factor_name, weight in weights.items():
            factor_value = factors.get(factor_name, 0.5)
            # For error_rate, invert (lower is better)
            if factor_name == "error_rate":
                factor_value = 1.0 - min(1.0, factor_value * 10)  # Scale error rate
            
            total_score += factor_value * weight
            total_weight += weight
        
        # Normalize
        safety_score = total_score / total_weight if total_weight > 0 else 0.5
        
        return {
            "safety_score": safety_score,
            "trust_metrics": {
                "overall_trust": safety_score,
                "factor_breakdown": factors
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(SafetyScoringState)
    workflow.add_node("calculate", calculate_safety_score_node)
    workflow.set_entry_point("calculate")
    workflow.add_edge("calculate", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "safety_factors": {
                "policy_compliance": 0.95,
                "error_rate": 0.02,
                "anomaly_detection": 0.90,
                "intent_alignment": 0.88,
                "system_stability": 0.92
            },
            "safety_score": 0.0,
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0
        },
        {
            "safety_factors": {
                "policy_compliance": 0.70,
                "error_rate": 0.15,
                "anomaly_detection": 0.65,
                "intent_alignment": 0.60,
                "system_stability": 0.55
            },
            "safety_score": 0.0,
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = app.invoke(test_case)
        print(f"  Safety Score: {result['safety_score']:.3f}")
        print(f"  Overall Trust: {result['trust_metrics'].get('overall_trust', 0):.3f}")
    print()


def promotion_gate_integration():
    """Integration with promotion gates"""
    print("=" * 60)
    print("Example 2: Promotion Gate Integration")
    print("=" * 60)
    
    # Promotion gate thresholds
    PROMOTION_THRESHOLDS = {
        "development": 0.6,
        "staging": 0.75,
        "production": 0.90
    }
    
    def evaluate_promotion_gate_node(state: SafetyScoringState):
        """Evaluate promotion gate"""
        print("  [Promotion Gate] Evaluating promotion gate...")
        safety_score = state.get("safety_score", 0.0)
        target_environment = state.get("target_environment", "production")
        
        threshold = PROMOTION_THRESHOLDS.get(target_environment, 0.9)
        passed = safety_score >= threshold
        
        gate_status = "passed" if passed else "failed"
        
        return {
            "promotion_gate_status": gate_status,
            "evaluation_history": state.get("evaluation_history", []) + [{
                "timestamp": "2024-01-01T00:00:00",
                "score": safety_score,
                "threshold": threshold,
                "environment": target_environment,
                "passed": passed
            }],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(SafetyScoringState)
    workflow.add_node("evaluate_gate", evaluate_promotion_gate_node)
    workflow.set_entry_point("evaluate_gate")
    workflow.add_edge("evaluate_gate", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "safety_factors": {},
            "safety_score": 0.95,  # High score
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0,
            "target_environment": "production"
        },
        {
            "safety_factors": {},
            "safety_score": 0.65,  # Low score
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0,
            "target_environment": "production"
        },
        {
            "safety_factors": {},
            "safety_score": 0.70,  # Medium score
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0,
            "target_environment": "staging"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Score = {test_case['safety_score']:.2f}, Environment = {test_case.get('target_environment', 'production')}")
        result = app.invoke(test_case)
        print(f"  Promotion gate: {result['promotion_gate_status']}")
        if result.get("evaluation_history"):
            eval_result = result["evaluation_history"][-1]
            print(f"  Threshold: {eval_result['threshold']:.2f}, Passed: {eval_result['passed']}")
    print()


def runtime_certification():
    """Runtime certification based on safety score"""
    print("=" * 60)
    print("Example 3: Runtime Certification")
    print("=" * 60)
    
    CERTIFICATION_LEVELS = {
        "certified": 0.90,
        "provisional": 0.75,
        "uncertified": 0.0
    }
    
    def certify_node(state: SafetyScoringState):
        """Certify system based on safety score"""
        print("  [Certification] Certifying system...")
        safety_score = state.get("safety_score", 0.0)
        
        # Determine certification level
        if safety_score >= CERTIFICATION_LEVELS["certified"]:
            certification_status = "certified"
        elif safety_score >= CERTIFICATION_LEVELS["provisional"]:
            certification_status = "provisional"
        else:
            certification_status = "uncertified"
        
        return {
            "certification_status": certification_status,
            "trust_metrics": {
                **state.get("trust_metrics", {}),
                "certification_level": certification_status,
                "certification_score": safety_score
            },
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(SafetyScoringState)
    workflow.add_node("certify", certify_node)
    workflow.set_entry_point("certify")
    workflow.add_edge("certify", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "safety_factors": {},
            "safety_score": 0.92,
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0
        },
        {
            "safety_factors": {},
            "safety_score": 0.80,
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0
        },
        {
            "safety_factors": {},
            "safety_score": 0.60,
            "promotion_gate_status": "",
            "certification_status": "",
            "trust_metrics": {},
            "evaluation_history": [],
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}: Safety Score = {test_case['safety_score']:.2f}")
        result = app.invoke(test_case)
        print(f"  Certification Status: {result['certification_status']}")
        print(f"  Certification Score: {result['trust_metrics'].get('certification_score', 0):.2f}")
    print()


def trust_evaluation_metrics():
    """Comprehensive trust evaluation metrics"""
    print("=" * 60)
    print("Example 4: Trust Evaluation Metrics")
    print("=" * 60)
    
    def evaluate_trust_node(state: SafetyScoringState):
        """Evaluate trust metrics"""
        print("  [Trust Evaluation] Evaluating trust metrics...")
        safety_score = state.get("safety_score", 0.0)
        factors = state.get("safety_factors", {})
        
        # Calculate various trust dimensions
        trust_metrics = {
            "overall_trust": safety_score,
            "reliability": factors.get("system_stability", 0.5),
            "safety": factors.get("policy_compliance", 0.5) * (1.0 - factors.get("error_rate", 0.1)),
            "predictability": factors.get("intent_alignment", 0.5),
            "transparency": factors.get("anomaly_detection", 0.5),
            "trust_score": (
                safety_score * 0.4 +
                factors.get("system_stability", 0.5) * 0.2 +
                factors.get("policy_compliance", 0.5) * 0.2 +
                factors.get("intent_alignment", 0.5) * 0.2
            )
        }
        
        return {
            "trust_metrics": trust_metrics,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(SafetyScoringState)
    workflow.add_node("evaluate_trust", evaluate_trust_node)
    workflow.set_entry_point("evaluate_trust")
    workflow.add_edge("evaluate_trust", END)
    
    app = workflow.compile()
    
    test_case = {
        "safety_factors": {
            "policy_compliance": 0.90,
            "error_rate": 0.05,
            "anomaly_detection": 0.85,
            "intent_alignment": 0.88,
            "system_stability": 0.92
        },
        "safety_score": 0.88,
        "promotion_gate_status": "",
        "certification_status": "",
        "trust_metrics": {},
        "evaluation_history": [],
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nTrust evaluation result:")
    metrics = result["trust_metrics"]
    print(f"  Overall Trust: {metrics.get('overall_trust', 0):.3f}")
    print(f"  Trust Score: {metrics.get('trust_score', 0):.3f}")
    print(f"  Reliability: {metrics.get('reliability', 0):.3f}")
    print(f"  Safety: {metrics.get('safety', 0):.3f}")
    print(f"  Predictability: {metrics.get('predictability', 0):.3f}")
    print()


def continuous_safety_evaluation():
    """Continuous safety evaluation over time"""
    print("=" * 60)
    print("Example 5: Continuous Safety Evaluation")
    print("=" * 60)
    
    def continuous_evaluation_node(state: SafetyScoringState):
        """Continuous evaluation"""
        print("  [Continuous Evaluation] Performing continuous evaluation...")
        safety_score = state.get("safety_score", 0.0)
        evaluation_history = state.get("evaluation_history", [])
        
        # Add current evaluation
        evaluation = {
            "timestamp": "2024-01-01T00:00:00",
            "score": safety_score,
            "trend": "stable"
        }
        
        # Calculate trend
        if len(evaluation_history) >= 2:
            recent_scores = [e.get("score", 0.5) for e in evaluation_history[-2:]]
            if safety_score > recent_scores[-1]:
                evaluation["trend"] = "improving"
            elif safety_score < recent_scores[-1]:
                evaluation["trend"] = "degrading"
        
        return {
            "evaluation_history": evaluation_history + [evaluation],
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(SafetyScoringState)
    workflow.add_node("evaluate", continuous_evaluation_node)
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", END)
    
    app = workflow.compile()
    
    # Simulate continuous evaluation
    state = {
        "safety_factors": {},
        "safety_score": 0.85,
        "promotion_gate_status": "",
        "certification_status": "",
        "trust_metrics": {},
        "evaluation_history": [
            {"timestamp": "2024-01-01T00:00:00", "score": 0.80, "trend": "stable"},
            {"timestamp": "2024-01-01T00:01:00", "score": 0.82, "trend": "improving"}
        ],
        "step_count": 0
    }
    
    result = app.invoke(state)
    print(f"\nContinuous evaluation result:")
    print(f"  Total evaluations: {len(result['evaluation_history'])}")
    if result.get("evaluation_history"):
        latest = result["evaluation_history"][-1]
        print(f"  Latest score: {latest['score']:.2f}")
        print(f"  Trend: {latest['trend']}")
    print()


if __name__ == "__main__":
    try:
        safety_score_calculation()
        promotion_gate_integration()
        runtime_certification()
        trust_evaluation_metrics()
        continuous_safety_evaluation()
        
        print("=" * 60)
        print("All safety scoring examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

