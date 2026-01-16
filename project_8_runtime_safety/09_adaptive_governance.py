"""
Runtime Safety - Adaptive Governance
Demonstrates self-healing, policy adaptation, and continuous learning
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Dict, Any, List, Literal
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class GovernanceState(TypedDict):
    policies: Dict[str, Any]
    performance_history: Annotated[List[Dict], "performance history"]
    adaptation_actions: Annotated[List[str], "adaptation actions taken"]
    self_healing_triggered: bool
    policy_updates: Annotated[List[Dict], "policy update history"]
    governance_score: float
    step_count: int


def adaptive_feedback_system():
    """Adaptive feedback system that adjusts based on performance"""
    print("=" * 60)
    print("Example 1: Adaptive Feedback System")
    print("=" * 60)
    
    def evaluate_performance_node(state: GovernanceState):
        """Evaluate current performance"""
        print("  [Performance] Evaluating performance...")
        performance_history = state.get("performance_history", [])
        
        if not performance_history:
            return {
                "governance_score": 0.5,
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Calculate average performance
        recent_performance = performance_history[-5:] if len(performance_history) >= 5 else performance_history
        avg_performance = sum(p.get("score", 0.5) for p in recent_performance) / len(recent_performance)
        
        return {
            "governance_score": avg_performance,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def adapt_parameters_node(state: GovernanceState):
        """Adapt parameters based on performance"""
        print("  [Adaptation] Adapting parameters...")
        score = state.get("governance_score", 0.5)
        policies = state.get("policies", {})
        
        adaptation_actions = []
        
        # Adjust parameters based on performance
        if score < 0.7:
            # Performance is low, be more conservative
            policies["strictness"] = policies.get("strictness", 0.5) + 0.1
            adaptation_actions.append("increased_strictness")
        
        if score > 0.9:
            # Performance is high, can be more lenient
            policies["strictness"] = max(0.3, policies.get("strictness", 0.5) - 0.05)
            adaptation_actions.append("decreased_strictness")
        
        return {
            "policies": policies,
            "adaptation_actions": state.get("adaptation_actions", []) + adaptation_actions,
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GovernanceState)
    workflow.add_node("evaluate", evaluate_performance_node)
    workflow.add_node("adapt", adapt_parameters_node)
    
    workflow.set_entry_point("evaluate")
    workflow.add_edge("evaluate", "adapt")
    workflow.add_edge("adapt", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "policies": {"strictness": 0.5},
            "performance_history": [{"score": 0.6}, {"score": 0.55}, {"score": 0.58}],  # Low performance
            "adaptation_actions": [],
            "self_healing_triggered": False,
            "policy_updates": [],
            "governance_score": 0.0,
            "step_count": 0
        },
        {
            "policies": {"strictness": 0.5},
            "performance_history": [{"score": 0.95}, {"score": 0.92}, {"score": 0.94}],  # High performance
            "adaptation_actions": [],
            "self_healing_triggered": False,
            "policy_updates": [],
            "governance_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = app.invoke(test_case)
        print(f"  Governance score: {result['governance_score']:.2f}")
        print(f"  Updated strictness: {result['policies'].get('strictness', 0):.2f}")
        if result.get("adaptation_actions"):
            print(f"  Adaptation actions: {result['adaptation_actions']}")
    print()


def self_correcting_safety_policies():
    """Self-correcting safety policies"""
    print("=" * 60)
    print("Example 2: Self-Correcting Safety Policies")
    print("=" * 60)
    
    def detect_instability_node(state: GovernanceState):
        """Detect instability in system"""
        print("  [Instability Detection] Checking for instability...")
        performance_history = state.get("performance_history", [])
        
        if len(performance_history) < 3:
            return {
                "self_healing_triggered": False,
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Check for instability (high variance in performance)
        recent_scores = [p.get("score", 0.5) for p in performance_history[-3:]]
        variance = sum((s - sum(recent_scores)/len(recent_scores))**2 for s in recent_scores) / len(recent_scores)
        
        is_unstable = variance > 0.1  # High variance indicates instability
        
        return {
            "self_healing_triggered": is_unstable,
            "step_count": state.get("step_count", 0) + 1
        }
    
    def self_correct_node(state: GovernanceState):
        """Self-correct policies"""
        print("  [Self-Correction] Self-correcting policies...")
        policies = state.get("policies", {})
        
        # Apply corrections
        policy_update = {
            "timestamp": "2024-01-01T00:00:00",
            "previous_policy": policies.copy(),
            "correction": "stabilized_thresholds",
            "new_policy": {
                **policies,
                "stability_mode": True,
                "threshold_adjustment": 0.1
            }
        }
        
        return {
            "policies": policy_update["new_policy"],
            "policy_updates": state.get("policy_updates", []) + [policy_update],
            "self_healing_triggered": False,  # Reset after correction
            "step_count": state.get("step_count", 0) + 1
        }
    
    def route_by_instability(state: GovernanceState) -> Literal["correct", "continue"]:
        """Route based on instability"""
        return "correct" if state.get("self_healing_triggered", False) else "continue"
    
    workflow = StateGraph(GovernanceState)
    workflow.add_node("detect", detect_instability_node)
    workflow.add_node("correct", self_correct_node)
    
    workflow.set_entry_point("detect")
    workflow.add_conditional_edges(
        "detect",
        route_by_instability,
        {
            "correct": "correct",
            "continue": END
        }
    )
    workflow.add_edge("correct", END)
    
    app = workflow.compile()
    
    test_case = {
        "policies": {"threshold": 0.5},
        "performance_history": [
            {"score": 0.3},
            {"score": 0.8},
            {"score": 0.2}  # High variance = instability
        ],
        "adaptation_actions": [],
        "self_healing_triggered": False,
        "policy_updates": [],
        "governance_score": 0.0,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nSelf-correction result:")
    print(f"  Self-healing triggered: {test_case.get('self_healing_triggered', False)} -> {result.get('self_healing_triggered', False)}")
    print(f"  Policy updates: {len(result.get('policy_updates', []))}")
    if result.get("policy_updates"):
        print(f"  Correction: {result['policy_updates'][-1]['correction']}")
    print()


def continuous_learning_from_instability():
    """Learn from past instability"""
    print("=" * 60)
    print("Example 3: Continuous Learning from Instability")
    print("=" * 60)
    
    def learn_from_history_node(state: GovernanceState):
        """Learn from performance history"""
        print("  [Learning] Learning from history...")
        performance_history = state.get("performance_history", [])
        policy_updates = state.get("policy_updates", [])
        
        # Analyze patterns
        if len(performance_history) >= 5:
            # Identify patterns
            low_performance_periods = [i for i, p in enumerate(performance_history) if p.get("score", 0.5) < 0.6]
            
            if len(low_performance_periods) > len(performance_history) * 0.4:
                # More than 40% low performance - need policy update
                learned_policy = {
                    "timestamp": "2024-01-01T00:00:00",
                    "learned_from": "performance_history",
                    "insight": "Frequent low performance detected",
                    "recommendation": "Increase safety thresholds",
                    "applied": True
                }
                
                policies = state.get("policies", {})
                policies["safety_threshold"] = policies.get("safety_threshold", 0.5) + 0.1
                
                return {
                    "policies": policies,
                    "policy_updates": policy_updates + [learned_policy],
                    "step_count": state.get("step_count", 0) + 1
                }
        
        return {
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GovernanceState)
    workflow.add_node("learn", learn_from_history_node)
    workflow.set_entry_point("learn")
    workflow.add_edge("learn", END)
    
    app = workflow.compile()
    
    test_case = {
        "policies": {"safety_threshold": 0.5},
        "performance_history": [
            {"score": 0.5},
            {"score": 0.4},
            {"score": 0.55},
            {"score": 0.45},
            {"score": 0.5}  # 60% low performance
        ],
        "adaptation_actions": [],
        "self_healing_triggered": False,
        "policy_updates": [],
        "governance_score": 0.0,
        "step_count": 0
    }
    
    result = app.invoke(test_case)
    print(f"\nLearning result:")
    print(f"  Policy updates: {len(result.get('policy_updates', []))}")
    if result.get("policy_updates"):
        update = result["policy_updates"][-1]
        print(f"  Insight: {update.get('insight', 'N/A')}")
        print(f"  Recommendation: {update.get('recommendation', 'N/A')}")
    print(f"  Updated safety threshold: {result['policies'].get('safety_threshold', 0):.2f}")
    print()


def performance_based_parameter_adjustment():
    """Adjust parameters based on observed performance"""
    print("=" * 60)
    print("Example 4: Performance-Based Parameter Adjustment")
    print("=" * 60)
    
    def adjust_parameters_node(state: GovernanceState):
        """Adjust parameters based on performance"""
        print("  [Adjustment] Adjusting parameters...")
        performance_history = state.get("performance_history", [])
        policies = state.get("policies", {})
        
        if not performance_history:
            return {
                "step_count": state.get("step_count", 0) + 1
            }
        
        # Calculate trend
        recent = performance_history[-3:] if len(performance_history) >= 3 else performance_history
        scores = [p.get("score", 0.5) for p in recent]
        
        if len(scores) >= 2:
            trend = "improving" if scores[-1] > scores[0] else "degrading"
            
            # Adjust based on trend
            if trend == "degrading":
                policies["retry_count"] = policies.get("retry_count", 3) + 1
                policies["timeout"] = policies.get("timeout", 30) + 5
                adaptation_actions = ["increased_retry_count", "increased_timeout"]
            else:
                policies["retry_count"] = max(1, policies.get("retry_count", 3) - 1)
                policies["timeout"] = max(10, policies.get("timeout", 30) - 5)
                adaptation_actions = ["decreased_retry_count", "decreased_timeout"]
            
            return {
                "policies": policies,
                "adaptation_actions": state.get("adaptation_actions", []) + adaptation_actions,
                "step_count": state.get("step_count", 0) + 1
            }
        
        return {
            "step_count": state.get("step_count", 0) + 1
        }
    
    workflow = StateGraph(GovernanceState)
    workflow.add_node("adjust", adjust_parameters_node)
    workflow.set_entry_point("adjust")
    workflow.add_edge("adjust", END)
    
    app = workflow.compile()
    
    test_cases = [
        {
            "policies": {"retry_count": 3, "timeout": 30},
            "performance_history": [{"score": 0.8}, {"score": 0.7}, {"score": 0.6}],  # Degrading
            "adaptation_actions": [],
            "self_healing_triggered": False,
            "policy_updates": [],
            "governance_score": 0.0,
            "step_count": 0
        },
        {
            "policies": {"retry_count": 3, "timeout": 30},
            "performance_history": [{"score": 0.6}, {"score": 0.7}, {"score": 0.8}],  # Improving
            "adaptation_actions": [],
            "self_healing_triggered": False,
            "policy_updates": [],
            "governance_score": 0.0,
            "step_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest case {i}:")
        result = app.invoke(test_case)
        print(f"  Retry count: {result['policies'].get('retry_count', 0)}")
        print(f"  Timeout: {result['policies'].get('timeout', 0)}s")
        if result.get("adaptation_actions"):
            print(f"  Actions: {result['adaptation_actions']}")
    print()


if __name__ == "__main__":
    try:
        adaptive_feedback_system()
        self_correcting_safety_policies()
        continuous_learning_from_instability()
        performance_based_parameter_adjustment()
        
        print("=" * 60)
        print("All adaptive governance examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

