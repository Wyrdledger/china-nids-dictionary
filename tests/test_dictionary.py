import csv
import importlib.util
import json
import re
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_CSV = ROOT / "data" / "nids_current.csv"
HISTORY_CSV = ROOT / "data" / "nids_history.csv"
CURRENT_JSON = ROOT / "data" / "nids_current.json"
PY_HELPER = ROOT / "python" / "nids_dictionary.py"

REQUIRED_COLUMNS = [
    "disease_id",
    "disease_name_zh",
    "disease_name_en",
    "legal_class",
    "management_class",
    "report_time_limit_hours",
    "is_current",
    "effective_start_date",
    "effective_end_date",
    "source_id",
    "source_note",
]


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class DictionaryValidationTest(unittest.TestCase):
    def test_required_columns_and_expected_current_counts(self):
        rows = read_csv(CURRENT_CSV)
        self.assertEqual(list(rows[0].keys()), REQUIRED_COLUMNS)
        self.assertEqual(len(rows), 42)

        counts = {"甲类": 0, "乙类": 0, "丙类": 0}
        for row in rows:
            counts[row["legal_class"]] += 1
        self.assertEqual(counts, {"甲类": 2, "乙类": 29, "丙类": 11})

    def test_unique_ids_classes_booleans_and_dates(self):
        rows = read_csv(HISTORY_CSV)
        ids = [row["disease_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))

        valid_classes = {"甲类", "乙类", "丙类"}
        valid_management = {
            "甲类管理",
            "乙类管理",
            "乙类按甲类措施管理",
            "乙类部分按甲类措施管理",
            "丙类管理",
        }

        for row in rows:
            self.assertRegex(row["disease_id"], re.compile(r"^NID-[ABC]-[0-9]{3}$"))
            self.assertIn(row["legal_class"], valid_classes)
            self.assertIn(row["management_class"], valid_management)
            self.assertIn(row["is_current"], {"true", "false"})
            self.assertIn(row["report_time_limit_hours"], {"2", "24"})

            start = date.fromisoformat(row["effective_start_date"])
            if row["effective_end_date"]:
                self.assertLessEqual(start, date.fromisoformat(row["effective_end_date"]))

    def test_current_csv_matches_active_history_rows(self):
        current = sorted(read_csv(CURRENT_CSV), key=lambda row: row["disease_id"])
        active_history = sorted(
            [row for row in read_csv(HISTORY_CSV) if row["is_current"] == "true"],
            key=lambda row: row["disease_id"],
        )
        self.assertEqual(current, active_history)

    def test_json_matches_current_csv(self):
        csv_rows = read_csv(CURRENT_CSV)
        with CURRENT_JSON.open("r", encoding="utf-8-sig") as handle:
            json_rows = json.load(handle)

        normalized_csv_rows = []
        for row in csv_rows:
            item = dict(row)
            item["report_time_limit_hours"] = int(item["report_time_limit_hours"])
            item["is_current"] = item["is_current"] == "true"
            item["effective_end_date"] = item["effective_end_date"] or None
            normalized_csv_rows.append(item)

        self.assertEqual(json_rows, normalized_csv_rows)

    def test_python_reader_smoke_test(self):
        spec = importlib.util.spec_from_file_location("nids_dictionary", PY_HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        rows = module.read_nids_csv(str(CURRENT_CSV))
        self.assertEqual(len(rows), 42)
        self.assertTrue(rows[0]["is_current"])
        self.assertIsInstance(rows[0]["report_time_limit_hours"], int)


if __name__ == "__main__":
    unittest.main()
