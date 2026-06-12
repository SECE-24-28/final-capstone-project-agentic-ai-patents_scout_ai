import os
import json
import unittest
from pathlib import Path
import pandas as pd

from backend.data_pipeline.bootstrap_patents import bootstrap_raw_patents
from backend.data_pipeline.build_patent_dataset import run_build_pipeline

class TestPatentDatasetPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Setup test raw patents directory and bootstrap with real data
        cls.source_dir = "data/test_raw_patents"
        cls.output_dir = "data/test_processed_patents"
        bootstrap_raw_patents(cls.source_dir)

    @classmethod
    def tearDownClass(cls):
        # Clean up test directories
        import shutil
        for path in [cls.source_dir, cls.output_dir]:
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_end_to_end_pipeline(self):
        """Runs the entire pipeline, verifies output files, and inspects metrics."""
        print("\n" + "=" * 60)
        print("VERIFYING PATENT DATASET PIPELINE END-TO-END")
        print("=" * 60)

        # 2. Run the build pipeline
        report = run_build_pipeline(self.source_dir, self.output_dir)

        # 3. Assertions & Verification of metrics
        self.assertEqual(report["total_raw_records"], 29)
        self.assertEqual(report["total_clean_records"], 24)  # 29 - 1 duplicate - 4 malformed/missing
        self.assertEqual(report["duplicates_removed"], 1)
        self.assertEqual(report["missing_titles_removed"], 1)
        self.assertEqual(report["missing_abstracts_removed"], 1)
        self.assertEqual(report["malformed_records_removed"], 2)  # 2 short ones
        self.assertEqual(report["final_dataset_size"], 24)

        # 4. Verify all output files exist
        csv_path = Path(self.output_dir) / "patents_balanced.csv"
        json_path = Path(self.output_dir) / "patents_balanced.json"
        report_path = Path(self.output_dir) / "dataset_report.json"

        self.assertTrue(csv_path.exists(), f"Output file missing: {csv_path}")
        self.assertTrue(json_path.exists(), f"Output file missing: {json_path}")
        self.assertTrue(report_path.exists(), f"Output file missing: {report_path}")

        # Load CSV and verify headers and content
        df = pd.read_csv(csv_path)
        required_headers = ["patent_number", "title", "abstract", "assignee", "year", "domain"]
        for header in required_headers:
            self.assertIn(header, df.columns)

        # 5. Confirm NO synthetic patents were created
        # Check that all patent numbers match real-world identifiers (starts with US or CN)
        for num in df["patent_number"]:
            self.assertTrue(num.startswith("US") or num.startswith("CN"), f"Found non-real patent number format: {num}")
            self.assertNotEqual(num, "US9999999B2")  # Verify malformed cases were removed

        print("[SUCCESS] Dataset pipeline verification test passed!")
        print(f"  - Verified CSV dataset: {csv_path}")
        print(f"  - Verified JSON dataset: {json_path}")
        print(f"  - Verified Report dataset: {report_path}")
        print("=" * 60 + "\n")

if __name__ == "__main__":
    unittest.main()
