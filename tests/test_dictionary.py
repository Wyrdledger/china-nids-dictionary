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
WEEKLY_FIXTURE = ROOT / "tests" / "fixtures" / "weekly_dictionary_2026-06-01.csv"
PY_HELPER = ROOT / "python" / "nids_dictionary.py"

REQUIRED_COLUMNS = [
    "disease_id",
    "disease_name_zh",
    "disease_name_en",
    "legal_class",
    "management_class",
    "report_time_limit_hours",
    "record_type",
    "is_notifiable_disease",
    "parent_disease_id",
    "cisdcp_disease_name",
    "transmission_type",
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
        self.assertEqual(len(rows), 83)

        notifiable = [row for row in rows if row["is_notifiable_disease"] == "true"]
        self.assertEqual(len(notifiable), 42)

        counts = {"甲类": 0, "乙类": 0, "丙类": 0}
        for row in notifiable:
            counts[row["legal_class"]] += 1
        self.assertEqual(counts, {"甲类": 2, "乙类": 29, "丙类": 11})

        record_counts = {}
        for row in rows:
            record_counts[row["record_type"]] = record_counts.get(row["record_type"], 0) + 1
        self.assertEqual(
            record_counts,
            {"notifiable_disease": 42, "aggregate": 1, "alias": 1, "subtype": 39},
        )

    def test_unique_ids_classes_booleans_dates_and_parent_links(self):
        rows = read_csv(HISTORY_CSV)
        ids = [row["disease_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))

        notifiable_ids = {
            row["disease_id"] for row in rows if row["record_type"] == "notifiable_disease"
        }
        valid_classes = {"甲类", "乙类", "丙类"}
        valid_management = {
            "甲类管理",
            "乙类管理",
            "乙类按甲类措施管理",
            "乙类部分按甲类措施管理",
            "丙类管理",
        }
        valid_record_types = {"notifiable_disease", "subtype", "alias", "aggregate"}
        valid_transmission = {"", "呼吸道传染病", "肠道传染病"}

        for row in rows:
            self.assertRegex(
                row["disease_id"],
                re.compile(r"^NID-(?:[ABC]-[0-9]{3}(?:-S[0-9]{3})?|AGG-[0-9]{3})$"),
            )
            self.assertIn(row["record_type"], valid_record_types)
            self.assertIn(row["is_current"], {"true", "false"})
            self.assertIn(row["is_notifiable_disease"], {"true", "false"})
            self.assertIn(row["transmission_type"], valid_transmission)

            if row["record_type"] == "aggregate":
                self.assertEqual(row["parent_disease_id"], "")
                self.assertEqual(row["legal_class"], "")
                self.assertEqual(row["management_class"], "")
                self.assertEqual(row["report_time_limit_hours"], "")
            else:
                self.assertIn(row["legal_class"], valid_classes)
                self.assertIn(row["management_class"], valid_management)
                self.assertIn(row["report_time_limit_hours"], {"2", "24"})

            if row["record_type"] in {"subtype", "alias"}:
                self.assertIn(row["parent_disease_id"], notifiable_ids)
                self.assertEqual(row["is_notifiable_disease"], "false")

            if row["record_type"] == "notifiable_disease":
                self.assertEqual(row["is_notifiable_disease"], "true")
                self.assertEqual(row["parent_disease_id"], "")

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
        nullable_fields = {
            "disease_name_en",
            "legal_class",
            "management_class",
            "parent_disease_id",
            "transmission_type",
            "effective_end_date",
        }
        for row in csv_rows:
            item = dict(row)
            item["report_time_limit_hours"] = (
                int(item["report_time_limit_hours"])
                if item["report_time_limit_hours"]
                else None
            )
            item["is_notifiable_disease"] = item["is_notifiable_disease"] == "true"
            item["is_current"] = item["is_current"] == "true"
            for field in nullable_fields:
                item[field] = item[field] or None
            normalized_csv_rows.append(item)

        self.assertEqual(json_rows, normalized_csv_rows)

    def test_weekly_dictionary_source_rows_are_migrated(self):
        weekly_rows = read_csv(WEEKLY_FIXTURE)
        current_rows = read_csv(CURRENT_CSV)
        migrated_pairs = {
            (row["cisdcp_disease_name"], row["disease_name_zh"]) for row in current_rows
        }

        self.assertEqual(len(weekly_rows), 83)
        for row in weekly_rows:
            self.assertIn(row["疾病病种"], {item[0] for item in migrated_pairs})

    def test_cisdcp_names_are_unique_and_use_full_width_parentheses(self):
        rows = read_csv(CURRENT_CSV)
        cisdcp_names = [row["cisdcp_disease_name"] for row in rows]
        self.assertEqual(len(cisdcp_names), len(set(cisdcp_names)))

        for row in rows:
            for field in ["disease_name_zh", "cisdcp_disease_name"]:
                self.assertNotIn("(", row[field])
                self.assertNotIn(")", row[field])

    def test_report_names_follow_current_display_policy(self):
        rows = read_csv(CURRENT_CSV)
        by_cisdcp = {row["cisdcp_disease_name"]: row for row in rows}

        expected = {
            "痢疾": "痢疾",
            "斑疹伤寒": "流行性和地方性斑疹伤寒",
            "其他感染性腹泻病": "其他感染性腹泻病",
        }
        for cisdcp_name, disease_name in expected.items():
            self.assertEqual(by_cisdcp[cisdcp_name]["disease_name_zh"], disease_name)
            self.assertEqual(by_cisdcp[cisdcp_name]["record_type"], "notifiable_disease")

    def test_syphilis_subtype_names_use_chinese_ordinals(self):
        rows = read_csv(CURRENT_CSV)
        syphilis_subtypes = [
            row["disease_name_zh"]
            for row in rows
            if row["parent_disease_id"] == "NID-B-024"
        ]
        self.assertIn("一期梅毒", syphilis_subtypes)
        self.assertIn("二期梅毒", syphilis_subtypes)
        self.assertIn("三期梅毒", syphilis_subtypes)
        self.assertNotIn("Ⅰ期梅毒", syphilis_subtypes)
        self.assertNotIn("Ⅱ期梅毒", syphilis_subtypes)
        self.assertNotIn("III期梅毒", syphilis_subtypes)

    def test_python_reader_smoke_test(self):
        spec = importlib.util.spec_from_file_location("nids_dictionary", PY_HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        rows = module.read_nids_csv(str(CURRENT_CSV))
        self.assertEqual(len(rows), 83)
        self.assertEqual(
            sum(1 for row in rows if row["is_notifiable_disease"]),
            42,
        )
        self.assertTrue(rows[0]["is_current"])
        self.assertIsInstance(rows[0]["report_time_limit_hours"], int)

        aggregate = next(row for row in rows if row["record_type"] == "aggregate")
        self.assertIsNone(aggregate["report_time_limit_hours"])
        self.assertIsNone(aggregate["parent_disease_id"])


if __name__ == "__main__":
    unittest.main()
