# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types  import *
import sys
sys.path.append("/Workspace/Users/sivana9908_gmail.com#ext#@sivana9908gmail.onmicrosoft.com/Uber-Eats-End-to-End-_Azure-Data-Engineering-Project")
from src.common.spark_utils import standardize_columns
from delta.tables import DeltaTable

# COMMAND ----------

#Reading data from adls 
df_zones= (
    spark.read
    .format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load("abfss://bronze@ubereaststorage.dfs.core.windows.net/csv/zones/")
)
display(df_zones)


# COMMAND ----------






# COMMAND ----------

table_name = "ubereats_databricks1.silver.zones"

if not spark.catalog.tableExists(table_name):

    df_zones.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(table_name)

else:

    target = DeltaTable.forName(spark, table_name)

    (
        target.alias("t")
        .merge(
            df_zones.alias("s"),
            "t.zone_id = s.zone_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )