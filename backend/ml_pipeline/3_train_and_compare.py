import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib
import importlib.util

from ml_pipeline.preprocess import load_and_preprocess

def main():
    csv_path = 'backend/ml_pipeline/cleaned_support_sla_sample.csv'
    X_train, X_test, y_train, y_test = load_and_preprocess(csv_path)
    
    print('\n--- Training Random Forest Baseline ---')
    rf = RandomForestClassifier(random_state=42)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    param_grid = {'n_estimators': [50, 100], 'max_depth': [None, 5]}
    grid = GridSearchCV(rf, param_grid, cv=cv, scoring='roc_auc')
    grid.fit(X_train, y_train)
    
    best_rf = grid.best_estimator_
    y_pred = best_rf.predict(X_test)
    y_prob = best_rf.predict_proba(X_test)[:, 1]
    print(f'RF Accuracy: {accuracy_score(y_test, y_pred):.3f}')
    print(f'RF ROC-AUC:  {roc_auc_score(y_test, y_prob):.3f}')
    
    joblib.dump(best_rf, 'backend/ml_pipeline/best_rf_model.pkl')
    print('Model Comparison Complete. Best model serialized.')

if __name__ == '__main__':
    main()

