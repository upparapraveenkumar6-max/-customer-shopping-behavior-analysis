import os
import sqlite3
import unittest

from project_runner import build_sqlite_database, load_and_prepare_data, run_sql_queries


class ProjectFlowTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_customer_behavior.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_load_and_prepare_data(self):
        df = load_and_prepare_data('customer_shopping_behavior.csv')
        self.assertEqual(df.shape[0], 3900)
        self.assertFalse(df.isnull().any().any())
        self.assertIn('age_group', df.columns)
        self.assertIn('purchase_frequency_days', df.columns)

    def test_build_sqlite_database(self):
        df = load_and_prepare_data('customer_shopping_behavior.csv')
        table_name = build_sqlite_database(df, self.db_path, 'customer')
        self.assertEqual(table_name, 'customer')
        with sqlite3.connect(self.db_path) as conn:
            row_count = conn.execute('SELECT COUNT(*) FROM customer').fetchone()[0]
        self.assertEqual(row_count, 3900)

    def test_sql_queries_execute(self):
        df = load_and_prepare_data('customer_shopping_behavior.csv')
        build_sqlite_database(df, self.db_path, 'customer')
        results = run_sql_queries(self.db_path, 'customer_behavior_sql_queries_sqlite.sql')
        self.assertGreater(len(results), 0)
        self.assertEqual(len(results[0]), 2)


if __name__ == '__main__':
    unittest.main()
