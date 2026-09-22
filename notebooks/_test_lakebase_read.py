# Databricks notebook source
# Quick test: read underwriter table from Lakebase

df = (
    spark.read
    .format("postgresql")
    .option("host", "ep-icy-pond-d8d33jwn.database.us-east-2.cloud.databricks.com")
    .option("port", "5432")
    .option("database", "databricks_postgres")
    .option("dbtable", "email_to_quote.underwriter")
    .option("user", "6c61f198-3fcd-4021-8be2-cca728d89ac1")
    .option("password", "Mail2Quote2026!")
    .load()
)

print(f"Total rows in Lakebase underwriter: {df.count()}")
for row in df.collect():
    print(f"  id={row['id']} email_id={row['email_id']} decision={row['decision']}")
