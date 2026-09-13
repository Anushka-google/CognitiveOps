import json
import os
import sys
from datetime import datetime

# Add backend directory to sys path so we can run this directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.agent_llm_eval import AgentLLMEvaluator
from evaluation.rag_retrieval_eval import RAGEvaluator
from evaluation.ml_eval import MLEvaluator

def generate_unified_report():
    print("="*60)
    print("BOOTING COGNITIVEOPS UNIFIED EVALUATION ENGINE")
    print("="*60)
    
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "evaluations": []
    }
    
    # 1. Agent & LLM (Phases 9.1 & 9.4)
    print("\n[1/4] Running Agent & LLM Evaluation...")
    agent_evaluator = AgentLLMEvaluator()
    report["evaluations"].append(agent_evaluator.run_llm_evaluation())
    report["evaluations"].append(agent_evaluator.run_agent_evaluation())
    
    # 2. RAG & Retrieval (Phases 9.2 & 9.3)
    print("[2/4] Running RAG & Retrieval Evaluation...")
    rag_evaluator = RAGEvaluator()
    report["evaluations"].append(rag_evaluator.run_retrieval_experiment())
    report["evaluations"].append(rag_evaluator.run_rag_generation_eval())
    
    # 3. ML Models (Phase 9.5)
    print("[3/4] Running ML Predictive SLA Evaluation...")
    ml_evaluator = MLEvaluator()
    report["evaluations"].append(ml_evaluator.run_ml_evaluation())
    
    # 4. Output Results
    print("[4/4] Generating Output Report...")
    report_path = os.path.join(os.path.dirname(__file__), "evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    print("\nEvaluation Complete! Report saved to:", report_path)
    
    print("\n--- EXECUTIVE SUMMARY ---")
    print(f"RAG Hit Rate: {report['evaluations'][2]['hybrid_search']['hit_rate']}")
    print(f"LLM Avg Latency: {report['evaluations'][0]['avg_latency_ms']}ms")
    print(f"Agent Hallucination Rate: {report['evaluations'][1]['hallucination_rate']}")
    print(f"ML SLA Model Accuracy: {report['evaluations'][4]['metrics']['accuracy']}")

if __name__ == "__main__":
    generate_unified_report()
