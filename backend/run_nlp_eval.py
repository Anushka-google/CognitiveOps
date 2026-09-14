import time
import json
from sklearn.metrics import classification_report, precision_recall_fscore_support
from rouge_score import rouge_scorer
from app.services.nlp_service import nlp_service

def evaluate_classifier():
    print("\n--- Evaluating Zero-Shot Classifier ---")
    
    # Ground truth test dataset
    test_data = [
        {"text": "The database is completely down, all users are blocked.", "true_label": "BLOCKER"},
        {"text": "We need approval for the Q3 budget increase.", "true_label": "APPROVAL"},
        {"text": "Waiting on the security team to finish their review.", "true_label": "DEPENDENCY"},
        {"text": "Just letting you know the migration is 50% done.", "true_label": "STATUS_UPDATE"},
        {"text": "We might miss the deadline if AWS keeps rate-limiting us.", "true_label": "RISK"}
    ]
    
    y_true = [item["true_label"] for item in test_data]
    y_pred = []
    
    start_time = time.time()
    for item in test_data:
        pred = nlp_service.classify_workflow(item["text"])
        y_pred.append(pred)
        print(f"Text: '{item['text']}' \n-> Predicted: {pred} | Actual: {item['true_label']}\n")
        
    latency = time.time() - start_time
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    print(f"Classification Metrics:")
    print(f"Precision: {precision:.2f}")
    print(f"Recall:    {recall:.2f}")
    print(f"F1-Score:  {f1:.2f}")
    print(f"Latency:   {latency/len(test_data):.2f}s per message")
    
    nlp_service.free_memory()

def evaluate_summarizer():
    print("\n--- Evaluating T5 Summarizer ---")
    
    sample_workflow_data = """
    The backend API is currently experiencing intermittent 502 Bad Gateway errors. 
    This started happening after the recent deployment of the billing microservice. 
    Several enterprise customers have reported that they cannot download their invoices. 
    The DevOps team is currently rolling back the deployment and investigating the logs.
    We expect a full resolution within the next 2 hours.
    """
    
    expected_summary = "Backend API is returning 502 errors after the billing deployment, blocking enterprise invoice downloads. DevOps is rolling back and expects resolution in 2 hours."
    
    start_time = time.time()
    generated_summary = nlp_service.summarize_workflow(sample_workflow_data)
    latency = time.time() - start_time
    
    print(f"Generated Summary: {generated_summary}")
    print(f"Latency: {latency:.2f}s")
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(expected_summary, generated_summary)
    
    print(f"\nROUGE Metrics:")
    print(f"ROUGE-1: {scores['rouge1'].fmeasure:.2f}")
    print(f"ROUGE-2: {scores['rouge2'].fmeasure:.2f}")
    print(f"ROUGE-L: {scores['rougeL'].fmeasure:.2f}")
    
    nlp_service.free_memory()

if __name__ == "__main__":
    print("Initializing NLP Evaluation on Edge Hardware (CPU)...")
    evaluate_classifier()
    evaluate_summarizer()
    print("\nEvaluation Complete!")
