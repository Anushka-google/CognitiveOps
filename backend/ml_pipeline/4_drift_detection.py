import json
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

def detect_drift(reference_path, production_path, numerical_features):
    print("--- Starting Data Drift Detection ---")
    
    try:
        ref_df = pd.read_csv(reference_path)
        prod_df = pd.read_csv(production_path)
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return False
        
    drift_report = {"drift_detected": False, "features": {}}
    drift_count = 0
    
    # We will use the Kolmogorov-Smirnov test to detect distribution drift
    # p-value < 0.05 indicates the distributions are significantly different
    p_value_threshold = 0.05
    
    for feature in numerical_features:
        if feature in ref_df.columns and feature in prod_df.columns:
            ref_data = ref_df[feature].dropna()
            prod_data = prod_df[feature].dropna()
            
            statistic, p_value = ks_2samp(ref_data, prod_data)
            
            is_drifting = bool(p_value < p_value_threshold)
            if is_drifting:
                drift_count += 1
                
            drift_report["features"][feature] = {
                "ks_statistic": float(statistic),
                "p_value": float(p_value),
                "is_drifting": is_drifting
            }
            
    # If more than 20% of numerical features drift, we trigger global drift
    if drift_count / len(numerical_features) > 0.2:
        drift_report["drift_detected"] = True
        
    with open("backend/ml_pipeline/drift_report.json", "w") as f:
        json.dump(drift_report, f, indent=4)
        
    print(f"Drift Detection Complete. Found {drift_count} drifting features.")
    if drift_report["drift_detected"]:
        print("CRITICAL: GLOBAL DATA DRIFT DETECTED!")
    else:
        print("Data distributions are stable.")
        
    return drift_report["drift_detected"]

def simulate_production_drift():
    """Helper function to create a 'production' dataset with artificial drift."""
    print("Simulating production data with drift (increased backlog age & waiting ratio)...")
    df = pd.read_csv('backend/ml_pipeline/cleaned_support_sla_sample.csv')
    
    # Artificial Drift: Simulate a sudden massive backlog and slower responses
    df['backlog_age_hours'] = df['backlog_age_hours'] * np.random.uniform(1.5, 3.0, len(df))
    df['first_response_minutes'] = df['first_response_minutes'] * np.random.uniform(2.0, 5.0, len(df))
    
    prod_path = 'backend/ml_pipeline/production_sla_data.csv'
    df.to_csv(prod_path, index=False)
    return prod_path

if __name__ == "__main__":
    # Features to monitor for drift
    features_to_monitor = [
        'customer_tenure_months', 'contract_value_gbp', 
        'message_length', 'agent_queue_length_at_submit',
        'backlog_age_hours', 'first_response_minutes', 'resolution_hours'
    ]
    
    ref_dataset = 'backend/ml_pipeline/cleaned_support_sla_sample.csv'
    prod_dataset = simulate_production_drift()
    
    detect_drift(ref_dataset, prod_dataset, features_to_monitor)
