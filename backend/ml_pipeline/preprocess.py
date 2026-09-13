import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def load_and_preprocess(csv_path):
    print('Loading data...')
    df = pd.read_csv(csv_path)
    # Mock the ETL aggregated features for the pipeline
    df['response_time_hours'] = df['first_response_minutes'] / 60.0
    df['waiting_ratio'] = np.random.uniform(0.1, 0.9, len(df))
    df['blocker_density'] = np.random.uniform(0.0, 0.5, len(df))
    df['reassignment_rate'] = np.random.uniform(0.0, 0.3, len(df))
    df['dependency_count'] = np.random.randint(0, 5, len(df))
    df['workflow_complexity'] = np.random.uniform(1.0, 10.0, len(df))
    
    features = ['customer_tenure_months', 'previous_tickets_90d', 'avg_sentiment_score', 'message_length', 'contains_urgent_keyword', 'contains_refund_keyword', 'agent_queue_length_at_submit', 'agent_experience_months', 'backlog_age_hours', 'response_time_hours', 'waiting_ratio', 'blocker_density', 'reassignment_rate', 'dependency_count', 'workflow_complexity']
    
    X = df[features].fillna(0)
    y = df['sla_breached']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    joblib.dump(scaler, 'backend/ml_pipeline/sla_scaler_new.pkl')
    print('Preprocessing complete! Scaler saved.')
    return X_train_scaled, X_test_scaled, y_train, y_test

