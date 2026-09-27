import os
import sqlite3
from pathlib import Path

import pandas as pd


def load_and_prepare_data(csv_path='customer_shopping_behavior.csv'):
    df = pd.read_csv(csv_path)

    df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(
        lambda x: x.fillna(x.median())
    )

    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})

    labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
    df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)

    frequency_mapping = {
        'Fortnightly': 14,
        'Weekly': 7,
        'Monthly': 30,
        'Quarterly': 90,
        'Bi-Weekly': 14,
        'Annually': 365,
        'Every 3 Months': 90,
    }
    df['purchase_frequency_days'] = df['frequency_of_purchases'].map(frequency_mapping)

    if 'promo_code_used' in df.columns:
        df = df.drop(columns=['promo_code_used'])

    return df


def build_sqlite_database(df, db_path='customer_behavior.db', table_name='customer'):
    db_path = str(Path(db_path))
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    return table_name


def run_sql_queries(db_path='customer_behavior.db', sql_file='customer_behavior_sql_queries_sqlite.sql'):
    if not os.path.exists(sql_file):
        raise FileNotFoundError(f'Missing SQL file: {sql_file}')

    with sqlite3.connect(db_path) as conn:
        sql_text = Path(sql_file).read_text()
        statements = [s.strip() for s in sql_text.split(';') if s.strip()]
        results = []
        for statement in statements:
            try:
                rows = conn.execute(statement).fetchall()
                results.append(rows)
            except sqlite3.DatabaseError:
                continue
        return results


if __name__ == '__main__':
    df = load_and_prepare_data()
    build_sqlite_database(df)
    print('Loaded rows:', len(df))
    print('Columns:', df.columns.tolist())
    print('Nulls after cleaning:', int(df.isnull().sum().sum()))
