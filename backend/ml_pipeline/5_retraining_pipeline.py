import subprocess
import os

def run_retraining_pipeline():
    print("==================================================")
    print("COGNITIVEOPS CONTINUOUS TRAINING PIPELINE")
    print("==================================================")
    
    # Step 1: Detect Drift
    print("\n[1/3] Running Data Drift Checks...")
    drift_result = subprocess.run(
        ["python", "backend/ml_pipeline/4_drift_detection.py"], 
        capture_output=True, text=True
    )
    print(drift_result.stdout)
    
    if "GLOBAL DATA DRIFT DETECTED" in drift_result.stdout:
        print("Data drift threshold exceeded. Retraining is required.")
        
        # Step 2: Ensure dataset is up-to-date (DVC)
        print("\n[2/3] Pulling latest dataset from DVC...")
        dvc_result = subprocess.run(["dvc", "pull"], capture_output=True, text=True)
        print("DVC Sync Complete.")
        
        # Step 3: Trigger MLflow Training Pipeline
        print("\n[3/3] Triggering Model Training & MLflow Registry...")
        train_result = subprocess.run(
            ["python", "backend/ml_pipeline/3_train_and_compare.py"], 
            capture_output=True, text=True
        )
        print(train_result.stdout)
        
        print("\nRETRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    else:
        print("\nNo significant drift detected. Retraining skipped.")

if __name__ == "__main__":
    run_retraining_pipeline()
