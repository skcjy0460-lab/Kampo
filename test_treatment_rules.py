import unittest
from datetime import date

from treatment_rules import (
    CUPPING_RULES,
    PHARMACOPUNCTURE_RULES,
    VISIT_CHUNA_RULES,
    build_schedule,
    calculate_guide,
    current_frequency_text,
    day_number,
    ict_rule,
)


class TreatmentRulesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.accident = date(2026, 5, 1)

    def test_day_number_is_inclusive(self) -> None:
        self.assertEqual(day_number(self.accident, date(2026, 5, 1)), 1)
        self.assertEqual(day_number(self.accident, date(2026, 5, 17)), 17)

    def test_visit_chuna_boundary_days(self) -> None:
        self.assertEqual(
            current_frequency_text(self.accident, date(2026, 5, 21), VISIT_CHUNA_RULES),
            "매일 가능",
        )
        self.assertEqual(
            current_frequency_text(self.accident, date(2026, 5, 22), VISIT_CHUNA_RULES),
            "주 3회 가능",
        )

    def test_pharmacopuncture_boundary_days(self) -> None:
        self.assertEqual(
            current_frequency_text(
                self.accident, date(2026, 5, 7), PHARMACOPUNCTURE_RULES
            ),
            "매일 가능",
        )
        self.assertEqual(
            current_frequency_text(
                self.accident, date(2026, 5, 8), PHARMACOPUNCTURE_RULES
            ),
            "주 3회 가능",
        )

    def test_ict_changes_on_day_18(self) -> None:
        self.assertEqual(
            ict_rule(self.accident, date(2026, 5, 17))["outpatient"],
            "1일 1회 / 2부위까지",
        )
        self.assertEqual(
            ict_rule(self.accident, date(2026, 5, 18))["inpatient"],
            "1일 2회 / 1부위",
        )

    def test_cupping_uses_initial_visit_date(self) -> None:
        initial_visit = date(2026, 5, 10)
        self.assertEqual(
            current_frequency_text(initial_visit, date(2026, 5, 16), CUPPING_RULES),
            "매일 시행 가능",
        )
        self.assertEqual(
            current_frequency_text(initial_visit, date(2026, 5, 17), CUPPING_RULES),
            "주 4회 가능",
        )

    def test_schedule_end_dates_match_source_periods(self) -> None:
        schedule = build_schedule(self.accident, date(2026, 5, 22), VISIT_CHUNA_RULES)
        self.assertEqual(schedule[0].end_date, date(2026, 5, 21))
        self.assertEqual(schedule[1].start_date, date(2026, 5, 22))
        self.assertTrue(schedule[1].is_current)

    def test_invalid_initial_visit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            calculate_guide(self.accident, date(2026, 4, 30), date(2026, 5, 10))


if __name__ == "__main__":
    unittest.main()
