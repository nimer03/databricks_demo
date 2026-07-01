import os
import pandas
import glob
import openpyxl
from pyspark.sql.functions import current_timestamp

path = "/Volumes/sac/customer_service/cloud_storage"

csv_files = sorted(glob.glob(os.path.join(path, "chat", "*.xlsx")), key=os.path.getmtime)

for f in csv_files:
  
    df_chat = pandas.read_excel(f)

    print('Shape: ', df_chat.shape)
    print('Columns: ', df_chat.columns)
    print('Data Types: ', df_chat.dtypes)

    df_chat = df_chat.astype(str)
    spark_df_chat = spark.createDataFrame(df_chat)

    spark_df_chat = spark_df_chat.withColumn("ingestion_time", current_timestamp())

    spark_df_chat.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable("sac.support.chat_bronze")