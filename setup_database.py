"""
Database Initialization Script
Supports both SQLite (local out-of-the-box testing) and MySQL (production database).
Loads data from Data_CSV/ into tables matching the tutorial schema.
"""

import os
import re
import pandas as pd
from sqlalchemy import create_engine

DATA_DIR = os.path.join(os.path.dirname(__file__), "Data_CSV")

CSV_TABLE_MAPPING = {
    "2017_Budgets.csv": "2017_budgets",
    "Customers.csv": "customers",
    "Products.csv": "products",
    "Regions.csv": "regions",
    "sales_order.csv": "sales_order",
    "State_Regions.csv": "state_regions",
}


def load_data_to_db(connection_uri: str, is_sqlite: bool = False):
    print(f"Connecting to database: {'SQLite (local file)' if is_sqlite else connection_uri}")
    engine = create_engine(connection_uri)

    for csv_file, table_name in CSV_TABLE_MAPPING.items():
        csv_path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_file} not found in {DATA_DIR}")
            continue

        print(f"Loading {csv_file} -> table '{table_name}'...")
        df = pd.read_csv(csv_path)

        # Standardize numeric columns if necessary
        if "2017 Budgets" in df.columns:
            # Clean monetary string formats if any
            df["2017 Budgets"] = (
                df["2017 Budgets"]
                .astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
            )
            df["2017 Budgets"] = pd.to_numeric(df["2017 Budgets"], errors="coerce")

        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"  Loaded {len(df)} rows into '{table_name}'.")

    print("\nDatabase initialization completed successfully!")


def setup_sqlite():
    db_path = os.path.join(os.path.dirname(__file__), "regional_sales_data.db")
    sqlite_uri = f"sqlite:///{db_path}"
    load_data_to_db(sqlite_uri, is_sqlite=True)
    return sqlite_uri


def setup_mysql(host="localhost", port=3306, user="root", password="password", db_name="regional_sales_data"):
    from sqlalchemy import text

    # Connect to MySQL server to create database if not exists
    server_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}"
    server_engine = create_engine(server_uri)
    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
        conn.commit()

    db_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    load_data_to_db(db_uri, is_sqlite=False)
    return db_uri


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize regional_sales_data database")
    parser.add_argument("--db", choices=["sqlite", "mysql"], default="sqlite", help="Target database type")
    parser.add_argument("--host", default=os.getenv("MYSQL_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MYSQL_PORT", 3306)))
    parser.add_argument("--user", default=os.getenv("MYSQL_USER", "root"))
    parser.add_argument("--password", default=os.getenv("MYSQL_PASSWORD", "root"))
    parser.add_argument("--dbname", default=os.getenv("MYSQL_DATABASE", "regional_sales_data"))

    args = parser.parse_args()

    if args.db == "sqlite":
        setup_sqlite()
    else:
        setup_mysql(args.host, args.port, args.user, args.password, args.dbname)
