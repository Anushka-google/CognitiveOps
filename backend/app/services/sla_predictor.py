from pathlib import Path

import joblib
import numpy as np
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "sla_model.keras"
SCALER_PATH = BASE_DIR / "models" / "sla_scaler.pkl"


FEATURE_COLUMNS = [
    "customer_tenure_months",
    "previous_tickets_90d",
    "avg_sentiment_score",
    "message_length",
    "contains_urgent_keyword",
    "contains_refund_keyword",
    "agent_queue_length_at_submit",
    "agent_experience_months",
    "backlog_age_hours",
    "response_time_hours",
    "waiting_ratio",
    "blocker_density",
    "reassignment_rate",
    "dependency_count",
    "workflow_complexity",
]


class SLAPredictor:

    def __init__(self):
        self.model = tf.keras.models.load_model(
            MODEL_PATH
        )

        self.scaler = joblib.load(
            SCALER_PATH
        )

    def predict(self, features: dict):

        values = [
            float(features.get(column, 0))
            for column in FEATURE_COLUMNS
        ]

        values = np.array(
            [values],
            dtype=float
        )

        scaled_values = self.scaler.transform(
            values
        )

        probability = float(
            self.model.predict(
                scaled_values,
                verbose=0
            )[0][0]
        )

        if probability >= 0.70:
            risk_level = "High"
        elif probability >= 0.40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "sla_breach_probability": probability,
            "risk_level": risk_level,
        }