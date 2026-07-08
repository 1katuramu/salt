#!/usr/bin/env python3

import os
import pandas as pd
import psycopg2
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text

def parse_args():
    parser = argparse.ArgumentParser(description='Import NSSF data from Excel to PostgreSQL')
    parser.add_argument('--excel-file', required=True, help='Path to Excel file')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', default='5432', help='Database port')
    parser.add_argument('--db-name', default='nssf_db', help='Database name')
    parser.add_argument('--db-user', default='nssf_user', help='Database user')
    parser.add_argument('--db-password', default='nssf_password', help='Database password')
    parser.add_argument('--table-name', default='nssf_data', help='Table name for all data')
    return parser.parse_args()

def clean_data(df):
    """Clean and prepare the data for import"""
    print("Cleaning data...")
    
    # Make column names consistent
    df.columns = [col.strip().upper() for col in df.columns]
    
    # Handle missing values - specify each column individually
    if 'NSSF_NUMBER' in df.columns:
        df['NSSF_NUMBER'] = df['NSSF_NUMBER'].fillna('')
    if 'MEMBER_NAME' in df.columns:
        df['MEMBER_NAME'] = df['MEMBER_NAME'].fillna('')
    if 'EMPLOYER_NAME' in df.columns:
        df['EMPLOYER_NAME'] = df['EMPLOYER_NAME'].fillna('')
    if 'EMPL_PRIM_NUMBER' in df.columns:
        df['EMPL_PRIM_NUMBER'] = df['EMPL_PRIM_NUMBER'].fillna('')
    if 'REFERENCE_PERIOD' in df.columns:
        df['REFERENCE_PERIOD'] = df['REFERENCE_PERIOD'].fillna('')
    if 'CONTRIBUTIONS_AMOUNT' in df.columns:
        df['CONTRIBUTIONS_AMOUNT'] = df['CONTRIBUTIONS_AMOUNT'].fillna(0)
    if 'AGE' in df.columns:
        df['AGE'] = df['AGE'].fillna(0)
    if 'NIN' in df.columns:
        df['NIN'] = df['NIN'].fillna('')
    if 'FATHER_NAME' in df.columns:
        df['FATHER_NAME'] = df['FATHER_NAME'].fillna('')
    if 'MOTHER_NAME' in df.columns:
        df['MOTHER_NAME'] = df['MOTHER_NAME'].fillna('')
    
    # Convert date columns to datetime
    for date_col in ['TRANSACTION_DATE', 'DOB']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Convert numeric columns
    if 'CONTRIBUTIONS_AMOUNT' in df.columns:
        df['CONTRIBUTIONS_AMOUNT'] = pd.to_numeric(df['CONTRIBUTIONS_AMOUNT'], errors='coerce').fillna(0)
    
    if 'AGE' in df.columns:
        df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce').fillna(0).astype(int)
    
    # Remove duplicates based on available columns
    duplicate_cols = []
    if 'NSSF_NUMBER' in df.columns:
        duplicate_cols.append('NSSF_NUMBER')
    if 'TRANSACTION_DATE' in df.columns:
        duplicate_cols.append('TRANSACTION_DATE')
    if 'REFERENCE_PERIOD' in df.columns:
        duplicate_cols.append('REFERENCE_PERIOD')
    
    if duplicate_cols:
        df = df.drop_duplicates(subset=duplicate_cols, keep='first')
    
    # Filter out rows with empty NSSF_NUMBER if the column exists
    if 'NSSF_NUMBER' in df.columns:
        df = df[df['NSSF_NUMBER'].astype(str).str.strip() != '']
    
    return df

def create_table(engine, table_name, df):
    """Create the required database table if it doesn't exist"""
    print(f"Creating database table '{table_name}' if it doesn't exist...")
    
    # Build CREATE TABLE statement dynamically based on DataFrame columns
    column_definitions = []
    
    for col in df.columns:
        col_lower = col.lower().replace(' ', '_')  # Handle spaces in column names
        
        # Determine column type based on column name patterns
        if col_lower in ['nssf_number', 'empl_prim_number', 'nin']:
            col_type = "VARCHAR(50)"
        elif col_lower in ['member_name', 'employer_name', 'father_name', 'mother_name']:
            col_type = "VARCHAR(255)"
        elif col_lower in ['reference_period']:
            col_type = "VARCHAR(100)"
        elif col_lower in ['dob', 'transaction_date']:
            col_type = "DATE"
        elif col_lower == 'age':
            col_type = "INTEGER"
        elif col_lower == 'contributions_amount':
            col_type = "DECIMAL(15,2)"
        else:
            col_type = "TEXT"  # Default for any other columns
        
        # Ensure column name is valid for PostgreSQL
        safe_col_name = col_lower.replace(' ', '_').replace('-', '_').replace('.', '_')
        column_definitions.append(f'"{safe_col_name}" {col_type}')
    
    # Add metadata columns
    column_definitions.extend([
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    ])
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        id SERIAL PRIMARY KEY,
        {', '.join(column_definitions)}
    );
    """
    
    print("Generated SQL:")
    print(create_table_sql)
    
    # Create unique constraint if we have key columns
    unique_constraint_sql = ""
    key_columns = []
    for col in df.columns:
        col_safe = col.lower().replace(' ', '_').replace('-', '_').replace('.', '_')
        if col_safe in ['nssf_number', 'transaction_date', 'reference_period']:
            key_columns.append(f'"{col_safe}"')
    
    if key_columns:
        constraint_name = f"{table_name}_unique_idx"
        unique_constraint_sql = f"""
        CREATE UNIQUE INDEX IF NOT EXISTS "{constraint_name}" 
        ON "{table_name}" ({', '.join(key_columns)});
        """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        if unique_constraint_sql:
            try:
                conn.execute(text(unique_constraint_sql))
                print("Unique constraint created successfully")
            except Exception as e:
                print(f"Note: Could not create unique constraint: {e}")
        conn.commit()
    
    print(f"Database table '{table_name}' ready!")

def import_to_postgres(df, db_params, table_name):
    """Import the data to PostgreSQL"""
    print("Importing data to PostgreSQL...")
    
    try:
        # Create SQLAlchemy engine
        connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create table if it doesn't exist
        create_table(engine, table_name, df)
        
        # Import data
        if not df.empty:
            print(f"Importing {len(df)} records...")
            # Convert column names to lowercase and handle special characters for PostgreSQL compatibility
            df_clean = df.copy()
            df_clean.columns = [col.lower().replace(' ', '_').replace('-', '_').replace('.', '_') for col in df_clean.columns]
            
            # Handle potential duplicates by using upsert logic
            try:
                df_clean.to_sql(table_name, engine, if_exists='append', index=False, 
                               method='multi', chunksize=1000)
                print("Data imported successfully!")
            except Exception as e:
                if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                    print("Some duplicate records found, continuing with unique records...")
                    # Try inserting one by one to skip duplicates
                    success_count = 0
                    skip_count = 0
                    for _, row in df_clean.iterrows():
                        try:
                            row.to_frame().T.to_sql(table_name, engine, if_exists='append', index=False)
                            success_count += 1
                        except:
                            skip_count += 1
                            continue  # Skip duplicates
                    print(f"Data imported: {success_count} records added, {skip_count} duplicates skipped!")
                else:
                    raise e
        else:
            print("No data to import.")
        
        # Show final statistics
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_count = result.fetchone()[0]
            print(f"Total records in table '{table_name}': {total_count}")
        
        print("Import completed successfully!")
        
    except Exception as e:
        print(f"Database import error: {str(e)}")
        raise

def main():
    args = parse_args()
    
    # Check if Excel file exists
    if not os.path.exists(args.excel_file):
        print(f"Error: Excel file '{args.excel_file}' not found.")
        return
    
    # Database connection parameters
    db_params = {
        'host': args.db_host,
        'port': args.db_port,
        'dbname': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }
    
    try:
        # Read Excel file
        print(f"Reading Excel file: {args.excel_file}")
        df = pd.read_excel(args.excel_file)
        print(f"Read {len(df)} rows from Excel file.")
        print(f"Columns found: {list(df.columns)}")
        
        # Clean data
        df = clean_data(df)
        print(f"After cleaning: {len(df)} rows remaining.")
        
        # Import to PostgreSQL
        import_to_postgres(df, db_params, args.table_name)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()