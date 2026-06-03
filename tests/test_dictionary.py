import csv
import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_CSV = ROOT / "data" / "nids_current.csv"
HISTORY_CSV = ROOT / "data" / "nids_history.csv"
CURRENT_JSON = ROOT / "data" / "nids_current.json"
WEEKLY_FIXTURE = ROOT / "tests" / "fixtures" / "weekly_dictionary_2026-06-01.csv"
PY_HELPER = ROOT / "python" / "nids_dictionary.py"

REQUIRED_COLUMNS = [
    "disease_id",
    "record_type",
    "is_notifiable_disease",
    "parent_disease_id",
    "disease_name_zh",
    "cisdcp_disease_name",
    "disease_name_en",
    "legal_class",
    "management_class",
    "report_time_limit_hours",
    "transmission_type",
    "pathogen_type",
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
            {"notifiable_disease": 42, "aggregate": 1, "subtype": 40},
        )
        self.assertTrue(
            all(row["record_type"] == "notifiable_disease" for row in rows[:42])
        )
        self.assertTrue(all(row["record_type"] == "subtype" for row in rows[42:-1]))
        self.assertEqual(rows[-1]["record_type"], "aggregate")
        self.assertEqual(rows[-1]["disease_name_zh"], "合计")

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
            "丙类管理",
        }
        valid_record_types = {"notifiable_disease", "subtype", "alias", "aggregate"}
        valid_transmission = {
            "",
            "呼吸道传染病",
            "肠道传染病",
            "动物源性及虫媒传染病",
            "经血与性传播传染病",
            "其他",
        }
        valid_pathogen = {"", "细菌性疾病", "病毒性疾病", "寄生虫病性疾病"}

        for row in rows:
            self.assertRegex(
                row["disease_id"],
                re.compile(r"^NID-(?:[ABC]-[0-9]{3}(?:-S[0-9]{3})?|AGG-[0-9]{3})$"),
            )
            self.assertIn(row["record_type"], valid_record_types)
            self.assertIn(row["is_notifiable_disease"], {"true", "false"})
            self.assertIn(row["transmission_type"], valid_transmission)
            self.assertIn(row["pathogen_type"], valid_pathogen)

            if row["record_type"] == "aggregate":
                self.assertEqual(row["parent_disease_id"], "")
                self.assertEqual(row["legal_class"], "")
                self.assertEqual(row["management_class"], "")
                self.assertEqual(row["report_time_limit_hours"], "")
            else:
                self.assertIn(row["legal_class"], valid_classes)
                self.assertIn(row["management_class"], valid_management)
                self.assertIn(row["report_time_limit_hours"], {"2", "24"})

            if row["record_type"] == "subtype":
                self.assertIn(row["parent_disease_id"], notifiable_ids)
                self.assertEqual(row["is_notifiable_disease"], "false")

            if row["record_type"] == "notifiable_disease":
                self.assertEqual(row["is_notifiable_disease"], "true")
                self.assertEqual(row["parent_disease_id"], "")

    def test_current_csv_matches_active_history_rows(self):
        current = sorted(read_csv(CURRENT_CSV), key=lambda row: row["disease_id"])
        history = sorted(read_csv(HISTORY_CSV), key=lambda row: row["disease_id"])
        self.assertEqual(current, history)

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
            "pathogen_type",
        }
        for row in csv_rows:
            item = dict(row)
            item["report_time_limit_hours"] = (
                int(item["report_time_limit_hours"])
                if item["report_time_limit_hours"]
                else None
            )
            item["is_notifiable_disease"] = item["is_notifiable_disease"] == "true"
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
            "痢疾": "细菌性和阿米巴痢疾",
            "斑疹伤寒": "流行性和地方性斑疹伤寒",
            "其他感染性腹泻病": "其他感染性腹泻病",
        }
        for cisdcp_name, disease_name in expected.items():
            self.assertEqual(by_cisdcp[cisdcp_name]["disease_name_zh"], disease_name)
            self.assertEqual(by_cisdcp[cisdcp_name]["record_type"], "notifiable_disease")

    def test_english_names_follow_professional_usage(self):
        rows = read_csv(CURRENT_CSV)
        by_name = {row["disease_name_zh"]: row for row in rows}

        self.assertTrue(all(row["disease_name_en"] for row in rows))

        expected = {
            "新型冠状病毒感染": "COVID-19",
            "人感染新亚型流感": "Human infection with novel influenza virus",
            "流行性出血热": "Hemorrhagic fever with renal syndrome",
            "登革热": "Dengue",
            "猴痘": "Mpox",
            "细菌性和阿米巴痢疾": "Bacillary and amoebic dysentery",
            "黑热病": "Visceral leishmaniasis (kala-azar)",
            "手足口病": "Hand, foot and mouth disease",
            "其他感染性腹泻病": "Other infectious diarrhea",
            "HIV": "HIV infection",
            "H5N1": "Human infection with avian influenza A(H5N1) virus",
            "H7N9": "Human infection with avian influenza A(H7N9) virus",
            "欧亚类禽H1N1": (
                "Human infection with Eurasian avian-like influenza A(H1N1) virus"
            ),
            "阿米巴性痢疾": "Amoebic dysentery",
            "利福平耐药": "Rifampicin-resistant pulmonary tuberculosis",
            "一期梅毒": "Primary syphilis",
            "间日疟": "Plasmodium vivax malaria",
            "恶性疟": "Plasmodium falciparum malaria",
            "疟疾（未分型）": "Untyped malaria",
            "合计": "Total",
        }
        for disease_name, disease_name_en in expected.items():
            self.assertEqual(by_name[disease_name]["disease_name_en"], disease_name_en)

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

    def test_class_b_managed_as_class_a_policy_and_time_limit(self):
        rows = read_csv(CURRENT_CSV)
        class_a_managed = [
            row
            for row in rows
            if row["legal_class"] == "乙类"
            and row["management_class"] == "甲类管理"
        ]
        self.assertEqual(
            {row["disease_id"] for row in class_a_managed},
            {"NID-B-002", "NID-B-013-S001"},
        )
        self.assertTrue(
            all(row["report_time_limit_hours"] == "2" for row in class_a_managed)
        )
        anthrax_parent = next(row for row in rows if row["disease_id"] == "NID-B-013")
        self.assertEqual(anthrax_parent["management_class"], "乙类管理")
        self.assertEqual(anthrax_parent["report_time_limit_hours"], "24")

    def test_transmission_type_policy(self):
        rows = read_csv(CURRENT_CSV)
        by_name = {row["disease_name_zh"]: row for row in rows}

        expected = {
            "传染性非典型肺炎": "呼吸道传染病",
            "麻疹": "呼吸道传染病",
            "肺结核": "呼吸道传染病",
            "流行性脑脊髓膜炎": "呼吸道传染病",
            "百日咳": "呼吸道传染病",
            "白喉": "呼吸道传染病",
            "猩红热": "呼吸道传染病",
            "流行性感冒": "呼吸道传染病",
            "流行性腮腺炎": "呼吸道传染病",
            "风疹": "呼吸道传染病",
            "麻风病": "呼吸道传染病",
            "霍乱": "肠道传染病",
            "甲肝": "肠道传染病",
            "戊肝": "肠道传染病",
            "肝炎（未分型）": "肠道传染病",
            "脊髓灰质炎": "肠道传染病",
            "细菌性和阿米巴痢疾": "肠道传染病",
            "伤寒和副伤寒": "肠道传染病",
            "急性出血性结膜炎": "肠道传染病",
            "其他感染性腹泻病": "肠道传染病",
            "手足口病": "肠道传染病",
            "鼠疫": "动物源性及虫媒传染病",
            "H5N1": "动物源性及虫媒传染病",
            "流行性出血热": "动物源性及虫媒传染病",
            "狂犬病": "动物源性及虫媒传染病",
            "流行性乙型脑炎": "动物源性及虫媒传染病",
            "登革热": "动物源性及虫媒传染病",
            "炭疽": "动物源性及虫媒传染病",
            "布鲁氏菌病": "动物源性及虫媒传染病",
            "钩端螺旋体病": "动物源性及虫媒传染病",
            "血吸虫病": "动物源性及虫媒传染病",
            "疟疾": "动物源性及虫媒传染病",
            "H7N9": "动物源性及虫媒传染病",
            "流行性和地方性斑疹伤寒": "动物源性及虫媒传染病",
            "黑热病": "动物源性及虫媒传染病",
            "包虫病": "动物源性及虫媒传染病",
            "丝虫病": "动物源性及虫媒传染病",
            "艾滋病": "经血与性传播传染病",
            "乙肝": "经血与性传播传染病",
            "丙肝": "经血与性传播传染病",
            "淋病": "经血与性传播传染病",
            "梅毒": "经血与性传播传染病",
            "新生儿破伤风": "其他",
            "基孔肯雅热": "动物源性及虫媒传染病",
            "发热伴血小板减少综合征": "动物源性及虫媒传染病",
        }
        for disease_name, transmission_type in expected.items():
            self.assertEqual(by_name[disease_name]["transmission_type"], transmission_type)

        observed_types = {row["transmission_type"] for row in rows if row["transmission_type"]}
        self.assertIn("呼吸道传染病", observed_types)
        self.assertIn("肠道传染病", observed_types)
        self.assertIn("动物源性及虫媒传染病", observed_types)
        self.assertIn("经血与性传播传染病", observed_types)
        self.assertIn("其他", observed_types)

    def test_pathogen_type_policy(self):
        rows = read_csv(CURRENT_CSV)
        by_name = {row["disease_name_zh"]: row for row in rows}

        expected = {
            "鼠疫": "细菌性疾病",
            "霍乱": "细菌性疾病",
            "炭疽": "细菌性疾病",
            "细菌性痢疾": "细菌性疾病",
            "肺结核": "细菌性疾病",
            "伤寒和副伤寒": "细菌性疾病",
            "流行性脑脊髓膜炎": "细菌性疾病",
            "百日咳": "细菌性疾病",
            "白喉": "细菌性疾病",
            "新生儿破伤风": "细菌性疾病",
            "猩红热": "细菌性疾病",
            "布鲁氏菌病": "细菌性疾病",
            "淋病": "细菌性疾病",
            "梅毒": "细菌性疾病",
            "麻风病": "细菌性疾病",
            "流行性和地方性斑疹伤寒": "细菌性疾病",
            "钩端螺旋体病": "细菌性疾病",
            "传染性非典型肺炎": "病毒性疾病",
            "新型冠状病毒感染": "病毒性疾病",
            "艾滋病": "病毒性疾病",
            "病毒性肝炎": "病毒性疾病",
            "脊髓灰质炎": "病毒性疾病",
            "人感染新亚型流感": "病毒性疾病",
            "麻疹": "病毒性疾病",
            "流行性出血热": "病毒性疾病",
            "狂犬病": "病毒性疾病",
            "流行性乙型脑炎": "病毒性疾病",
            "登革热": "病毒性疾病",
            "H7N9": "病毒性疾病",
            "流行性感冒": "病毒性疾病",
            "流行性腮腺炎": "病毒性疾病",
            "风疹": "病毒性疾病",
            "急性出血性结膜炎": "病毒性疾病",
            "手足口病": "病毒性疾病",
            "猴痘": "病毒性疾病",
            "基孔肯雅热": "病毒性疾病",
            "发热伴血小板减少综合征": "病毒性疾病",
            "阿米巴性痢疾": "寄生虫病性疾病",
            "血吸虫病": "寄生虫病性疾病",
            "疟疾": "寄生虫病性疾病",
            "丝虫病": "寄生虫病性疾病",
            "包虫病": "寄生虫病性疾病",
            "黑热病": "寄生虫病性疾病",
        }
        for disease_name, pathogen_type in expected.items():
            self.assertEqual(by_name[disease_name]["pathogen_type"], pathogen_type)

        for disease_name in ["H5N1", "乙肝", "细菌性和阿米巴痢疾", "合计"]:
            self.assertEqual(by_name[disease_name]["pathogen_type"], "")

    def test_hiv_is_subtype_and_aggregate_is_last_alignment_row(self):
        rows = read_csv(CURRENT_CSV)
        hiv = next(row for row in rows if row["disease_id"] == "NID-B-003-S001")
        self.assertEqual(hiv["record_type"], "subtype")
        self.assertEqual(hiv["parent_disease_id"], "NID-B-003")

        self.assertEqual(rows[-1]["disease_id"], "NID-AGG-001")
        self.assertEqual(rows[-1]["record_type"], "aggregate")
        self.assertEqual(rows[-1]["is_notifiable_disease"], "false")
        self.assertEqual(rows[-1]["cisdcp_disease_name"], "合计")

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
        self.assertIsInstance(rows[0]["report_time_limit_hours"], int)

        aggregate = next(row for row in rows if row["record_type"] == "aggregate")
        self.assertIsNone(aggregate["report_time_limit_hours"])
        self.assertIsNone(aggregate["parent_disease_id"])


if __name__ == "__main__":
    unittest.main()
