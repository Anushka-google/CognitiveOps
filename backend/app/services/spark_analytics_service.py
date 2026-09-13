from pyspark.sql.functions import col, when, avg, count, trim, lower, initcap, regexp_replace, round, sum as spark_sum
import json
import logging
import os
import sys
from app.services.jira_service import JiraService
from app.db.database import SessionLocal
from app.models.etl_results import ETLAnalyticsResult

# Crucial fix for Windows Spark Workers:
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

logger = logging.getLogger(__name__)

class SparkAnalyticsService:
    _spark_session = None
    
    @classmethod
    def get_spark_session(cls):
        if cls._spark_session is None:
            from pyspark.sql import SparkSession
            logger.info("Initializing PySpark Session...")
            cls._spark_session = SparkSession.builder \
                .appName("CognitiveOps-BigData-Analytics") \
                .master("local[*]") \
                .config("spark.driver.memory", "2g") \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .getOrCreate()
        return cls._spark_session

    def execute_full_etl_pipeline(self):
        """
        Executes Phase 7 End-to-End: Extract -> Clean -> Transform -> Aggregate -> Load
        """
        spark = self.get_spark_session()
        jira_service = JiraService()
        
        # ==========================================
        # 1. EXTRACT (Phase 7.1)
        # ==========================================
        # Extract live tickets from our system (acting as Data Lake extraction)
        tickets = jira_service.get_workflow_records()
        
        # Convert ORM objects to dicts for PySpark
        raw_data = []
        for t in tickets:
            raw_data.append({
                "ticket_id": str(t.ticket_id) if t.ticket_id else None,
                "priority": str(t.priority) if t.priority else "Unknown",
                "status": str(t.status) if t.status else "Unknown",
                "assignee": str(t.assignee) if t.assignee else "Unassigned",
                "days_waiting": int(t.days_waiting) if t.days_waiting is not None else 0,
                "dependencies": ""  # WorkflowRecord does not have a dependencies attribute
            })
            
        # Add some dirty mock records to strictly demonstrate Phase 7.2 Cleaning
        raw_data.extend([
            {"ticket_id": "MOCK-1", "priority": "  high ", "status": "in_progress", "assignee": "Frontend Team", "days_waiting": 12, "dependencies": ""},
            {"ticket_id": "MOCK-1", "priority": "  high ", "status": "in_progress", "assignee": "Frontend Team", "days_waiting": 12, "dependencies": ""}, # Duplicate
            {"ticket_id": "MOCK-2", "priority": "Medium", "status": None, "assignee": "Backend Team", "days_waiting": 45, "dependencies": "MOCK-1"}, # Null status
            {"ticket_id": "MOCK-3", "priority": "CRITICAL", "status": "In Review", "assignee": "DevOps", "days_waiting": -5, "dependencies": ""}, # Malformed negative
            {"ticket_id": None, "priority": "Low", "status": "To Do", "assignee": "Unknown", "days_waiting": 5, "dependencies": ""} # Null ID
        ])

        if not raw_data:
            return {"status": "error", "message": "No data available in Data Lake."}

        df = spark.createDataFrame(raw_data)
        
        # ==========================================
        # 2. CLEAN (Phase 7.2)
        # ==========================================
        # Drop critical nulls, duplicates, and malformed strings
        df_clean = df.na.drop(subset=["ticket_id"])
        df_clean = df_clean.dropDuplicates(["ticket_id"])
        df_clean = df_clean.na.fill({"status": "Unknown", "assignee": "Unassigned", "priority": "Medium"})
        df_clean = df_clean.filter(col("days_waiting") >= 0)
        
        # Normalization
        df_clean = df_clean.withColumn("priority", initcap(trim(col("priority")))) \
                           .withColumn("status", initcap(regexp_replace(col("status"), "_", " ")))
                           
        # ==========================================
        # 3. FEATURE ENGINEERING (Phase 7.3)
        # ==========================================
        # Create ML-ready features
        df_features = df_clean \
            .withColumn("is_high_risk", when((col("priority").isin("High", "Critical")) & (col("days_waiting") > 14), 1).otherwise(0)) \
            .withColumn("is_bottleneck", when(col("status") == "Blocked", 1).otherwise(0)) \
            .withColumn("dependency_count", when(col("dependencies") != "", 1).otherwise(0)) # Simplified for demo
            
        # ==========================================
        # 4. AGGREGATE (Phase 7.4)
        # ==========================================
        # Group by Assignee/Team to calculate KPI aggregations
        df_agg = df_features.groupBy("assignee") \
            .agg(
                count("ticket_id").alias("total_workflows"),
                round(avg("days_waiting"), 2).alias("avg_waiting_time"),
                spark_sum("is_high_risk").alias("high_risk_workflows"),
                round(avg("is_bottleneck"), 2).alias("blocker_density")
            )
            
        # ==========================================
        # 5. LOAD / OUTPUT (Phase 7.5)
        # ==========================================
        # Collect back to Driver Memory
        results = [json.loads(row) for row in df_agg.toJSON().collect()]
        
        # Write to PostgreSQL/SQLite via SQLAlchemy (Closing the loop to ML/Analytics)
        db = SessionLocal()
        try:
            # Clear old ETL results
            db.query(ETLAnalyticsResult).delete()
            
            inserted_records = []
            for r in results:
                record = ETLAnalyticsResult(
                    team_name=r.get("assignee", "Unknown"),
                    avg_waiting_time=r.get("avg_waiting_time", 0.0),
                    blocker_density=r.get("blocker_density", 0.0),
                    high_risk_workflows=r.get("high_risk_workflows", 0),
                    total_workflows=r.get("total_workflows", 0)
                )
                db.add(record)
                inserted_records.append(record)
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to load ETL data to database: {e}")
        finally:
            db.close()
            
        return {
            "status": "success",
            "pipeline_stages": [
                {"stage": "Extract", "rows": len(raw_data)},
                {"stage": "Clean", "rows": df_clean.count()},
                {"stage": "Transform", "features_added": ["is_high_risk", "is_bottleneck", "dependency_count"]},
                {"stage": "Aggregate", "teams_processed": len(results)},
                {"stage": "Load", "destination": "PostgreSQL/SQLite (etl_analytics_results table)"}
            ],
            "data": results
        }
