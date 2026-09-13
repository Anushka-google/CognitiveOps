import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib

from ml_pipeline.preprocess import load_and_preprocess

def train_model(name, model, param_grid, cv, X_train, y_train, X_test, y_test):
    print(f'\n--- Training {name} ---')
    grid = GridSearchCV(model, param_grid, cv=cv, scoring='roc_auc', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)
    
    print(f'{name} Accuracy: {acc:.3f}')
    print(f'{name} ROC-AUC:  {roc:.3f}')
    return best_model, roc, acc

def main():
    csv_path = 'backend/ml_pipeline/cleaned_support_sla_sample.csv'
    X_train, X_test, y_train, y_test = load_and_preprocess(csv_path)
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    
    results = {}
    
    # 1. Random Forest (Phase 11.6)
    rf, rf_roc, _ = train_model(
        "Random Forest", 
        RandomForestClassifier(random_state=42), 
        {'n_estimators': [50, 100], 'max_depth': [None, 5]},
        cv, X_train, y_train, X_test, y_test
    )
    results["Random Forest"] = {"model": rf, "roc": rf_roc}
    
    # 2. XGBoost (Phase 11.7)
    xgb, xgb_roc, _ = train_model(
        "XGBoost", 
        XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42), 
        {'n_estimators': [50, 100], 'max_depth': [3, 5], 'learning_rate': [0.01, 0.1]},
        cv, X_train, y_train, X_test, y_test
    )
    results["XGBoost"] = {"model": xgb, "roc": xgb_roc}
    
    # 3. LightGBM (Phase 11.8)
    lgb, lgb_roc, _ = train_model(
        "LightGBM", 
        LGBMClassifier(random_state=42), 
        {'n_estimators': [50, 100], 'max_depth': [3, 5], 'learning_rate': [0.01, 0.1]},
        cv, X_train, y_train, X_test, y_test
    )
    results["LightGBM"] = {"model": lgb, "roc": lgb_roc}
    
    # Determine Winner
    best_name = max(results, key=lambda k: results[k]['roc'])
    best_model = results[best_name]['model']
    best_roc = results[best_name]['roc']
    
    print("\n=========================================")
    print(f"CHAMPION MODEL: {best_name} (ROC-AUC: {best_roc:.3f})")
    print("=========================================")
    
    joblib.dump(best_model, 'backend/ml_pipeline/champion_model.pkl')
    print("Champion model serialized to backend/ml_pipeline/champion_model.pkl")

if __name__ == '__main__':
    main()
