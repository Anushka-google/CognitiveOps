from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import col, when, avg, count
import json
import logging
import os
import sys

# Crucial fix for Windows Spark Workers:
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

logger = logging.getLogger(__name__)

class SparkAnalyticsService:
    _spark_session = None
    
    @classmethod
    def get_spark_session(cls):
        """
        Initialize the SparkSession (Singleton pattern to avoid memory overhead).
        """
        if cls._spark_session is None:
            logger.info("Initializing PySpark Session...")
            cls._spark_session = SparkSession.builder \
                .appName("CognitiveOps-BigData-Analytics") \
                .master("local[*]") \
                .config("spark.driver.memory", "2g") \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .getOrCreate()
        return cls._spark_session

    def run_workflow_aggregation(self):
        """
        Demonstrates advanced PySpark DataFrames capabilities for historical analysis.
        """
        # 1. Initialize SparkSession
        spark = self.get_spark_session()

        # 2. Define Explicit Schemas (Schema Enforcement)
        ticket_schema = StructType([
            StructField("ticket_id", StringType(), True),
            StructField("priority", StringType(), True),
            StructField("status", StringType(), True),
            StructField("assignee_id", StringType(), True),
            StructField("days_waiting", IntegerType(), True)
        ])

        team_schema = StructType([
            StructField("assignee_id", StringType(), True),
            StructField("team_name", StringType(), True),
            StructField("region", StringType(), True)
        ])

        # Mock large-scale distributed data (simulating a Data Lake read)
        ticket_data = [
            ("KAN-101", "High", "In Progress", "U1", 12),
            ("KAN-102", "Medium", "Blocked", "U2", 45),
            ("KAN-103", "Critical", "In Review", "U1", 3),
            ("KAN-104", "High", "Blocked", "U3", 28),
            ("KAN-105", "Low", "Done", "U2", 1),
            ("KAN-106", "Medium", "In Progress", "U1", 8),
            ("KAN-107", "Critical", "Blocked", "U3", 35)
        ]
        
        team_data = [
            ("U1", "Frontend Core", "New York"),
            ("U2", "Backend API", "London"),
            ("U3", "Platform Ops", "San Francisco")
        ]

        # 3. Create DataFrames
        df_tickets = spark.createDataFrame(ticket_data, schema=ticket_schema)
        df_teams = spark.createDataFrame(team_data, schema=team_schema)

        # 4. select() & filter()
        # Extract active workflows and filter out completed items
        df_active = df_tickets.select("ticket_id", "priority", "status", "assignee_id", "days_waiting") \
                              .filter(col("status") != "Done")

        # 5. withColumn()
        # Derive a new column identifying SLA breaches dynamically
        df_enriched = df_active.withColumn(
            "sla_breached",
            when((col("priority") == "Critical") & (col("days_waiting") > 5), "Yes")
            .when((col("priority") == "High") & (col("days_waiting") > 14), "Yes")
            .otherwise("No")
        )

        # 6. join()
        # Join ticket data with organizational team data
        df_joined = df_enriched.join(df_teams, on="assignee_id", how="left")

        # 7. groupBy() & aggregations
        # Compute team-level operational metrics
        df_aggregated = df_joined.groupBy("team_name", "region") \
            .agg(
                count("ticket_id").alias("active_workflows"),
                avg("days_waiting").alias("avg_days_waiting"),
            )

        # Action: Collect results back to driver memory and parse to JSON
        # In a real environment, this might write out to Parquet or an S3 bucket
        json_rows = df_aggregated.toJSON().collect()
        
        return [json.loads(row) for row in json_rows]
