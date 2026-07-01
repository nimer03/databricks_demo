import os
import pandas
import glob
import openpyxl
from pyspark.sql.functions import current_timestamp

path = "/Volumes/sac/customer_service/cloud_storage"

csv_files = sorted(glob.glob(os.path.join(path, "ticket", "*.xlsx")), key=os.path.getmtime)

for f in csv_files:
  
    df_ticket = pandas.read_excel(f)

    print('Shape: ', df_ticket.shape)
    print('Columns: ', df_ticket.columns)
    print('Data Types: ', df_ticket.dtypes)

    df_ticket = df_ticket.astype(str)
    spark_df_ticket = spark.createDataFrame(df_ticket)

    spark_df_ticket = spark_df_ticket.withColumn("ingestion_time", current_timestamp())

    spark_df_ticket.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable("sac.support.ticket_bronze")