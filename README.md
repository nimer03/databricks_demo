# databricks_demo

In databricks_demo I implemented my first Databricks job to imitate transforming data in a data lakehouse.
I generated semi-structured and structured data with AI to simulate the data of an internet service provider with connection logs, customers, staff (agents), support tickets and live chats between customers and agents. Additionally, I included a table to enable a possible churn prediction in the future.
I structured the transformation after the medallion table structure. That means that the original data is stored in the bronze tables, ETL is then used to create a single source of truth in the silver tables and lastly I created gold tables that include aggregations to analyse use cases.
This demo consists of a Databricks job, the data it transforms and the notebooks that contain the SQL and Python code for the transformations.
