import subprocess
import json
import time

def extract_mrr_from_output(output):
    for line in output.split("\n"):
        if "Mean Reciprocal Rank (MRR):" in line:
            try:
                return float(line.split(":")[-1].strip())
            except ValueError:
                return None
    return None

def run_test_suite(suite_name, file_pattern):
    print(f"\n--- Running {suite_name} ---")
    start_time = time.time()
    
    # Run pytest and capture standard output
    args = ["pytest"] + file_pattern.split() + ["-s", "-q", "--disable-warnings"]
    result = subprocess.run(
        args, 
        capture_output=True, 
        text=True
    )
    
    duration = time.time() - start_time
    output = result.stdout
    
    # Count pass/fail
    passed = output.count(" .") + output.count("\n.")
    failed = output.count(" F") + output.count("\nF")
    total = passed + failed
    
    # Extract MRR if it's the retrieval suite
    mrr = extract_mrr_from_output(output)
    
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Results: {passed} Passed, {failed} Failed (Time: {duration:.2f}s)")
    
    return {
        "suite": suite_name,
        "files_tested": file_pattern,
        "metrics": {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "execution_latency_seconds": round(duration, 2),
            "mrr_score": mrr if mrr is not None else "N/A"
        }
    }

def main():
    print("======================================================")
    print("BOOTING COGNITIVEOPS UNIFIED EVALUATION ENGINE")
    print("Running LIVE against your actual pytest suite!")
    print("======================================================")
    
    report = {"evaluations": []}
    
    # Phase 9.1 & 9.4: Agent and LLM Evaluation
    report["evaluations"].append(
        run_test_suite("LLM & Agent Evaluation", "test_planner.py test_gemini_insight.py test_agentic_loop.py")
    )
    
    # Phase 9.2 & 9.3: RAG and Retrieval Evaluation
    report["evaluations"].append(
        run_test_suite("RAG & Retrieval Evaluation", "test_retrieval.py test_rag_reliability.py")
    )
    
    # Phase 9.5: ML / SLA Evaluation
    report["evaluations"].append(
        run_test_suite("ML SLA Predictive Evaluation", "test_sla_features.py test_sla_reasoning.py")
    )
    
    # Save Report
    with open("evaluation_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print("\nEvaluation Complete! Saved to evaluation_report.json")
    print("\n--- LIVE EXECUTIVE SUMMARY ---")
    
    for eval_result in report["evaluations"]:
        print(f"[{eval_result['suite']}] Success Rate: {eval_result['metrics']['success_rate']}%")
        if eval_result['metrics']['mrr_score'] != "N/A":
            print(f"[{eval_result['suite']}] Hit Rate / MRR: {eval_result['metrics']['mrr_score']}")
            
if __name__ == "__main__":
    main()
