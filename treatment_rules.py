"""Calculation rules for a Korean auto-accident oriental treatment guide.

The functions in this module intentionally calculate an *allowable frequency
guide*. They do not infer services actually performed or guarantee payment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class FrequencyRule:
    start_day: int
    end_day: int | None
    frequency: str
    description: str = ""


@dataclass(frozen=True)
class ScheduledRule:
    start_date: date
    end_date: date | None
    frequency: str
    description: str
    is_current: bool


VISIT_CHUNA_RULES = (
    FrequencyRule(1, 21, "매일 가능"),
    FrequencyRule(22, 84, "주 3회 가능"),
    FrequencyRule(85, 183, "주 2회 가능"),
    FrequencyRule(184, None, "주 1회 가능"),
)

PHARMACOPUNCTURE_RULES = (
    FrequencyRule(1, 7, "매일 가능"),
    FrequencyRule(8, 21, "주 3회 가능"),
    FrequencyRule(22, 70, "주 2회 가능"),
    FrequencyRule(71, None, "주 1회 가능"),
)

CUPPING_RULES = (
    FrequencyRule(1, 7, "매일 시행 가능"),
    FrequencyRule(8, 21, "주 4회 가능"),
    FrequencyRule(22, None, "주 2회 가능"),
)


def day_number(base_date: date, target_date: date) -> int:
    """Return inclusive day number: base date is day 1."""
    return (target_date - base_date).days + 1


def day_date(base_date: date, day: int) -> date:
    """Convert an inclusive day number back into a calendar date."""
    return base_date + timedelta(days=day - 1)


def applicable_rule(
    base_date: date, reference_date: date, rules: Iterable[FrequencyRule]
) -> FrequencyRule | None:
    """Find the rule active on reference_date, or None before the base date."""
    elapsed = day_number(base_date, reference_date)
    if elapsed < 1:
        return None
    for rule in rules:
        if elapsed >= rule.start_day and (
            rule.end_day is None or elapsed <= rule.end_day
        ):
            return rule
    return None


def build_schedule(
    base_date: date, reference_date: date, rules: Iterable[FrequencyRule]
) -> list[ScheduledRule]:
    current = applicable_rule(base_date, reference_date, rules)
    return [
        ScheduledRule(
            start_date=day_date(base_date, rule.start_day),
            end_date=day_date(base_date, rule.end_day) if rule.end_day else None,
            frequency=rule.frequency,
            description=rule.description,
            is_current=rule == current,
        )
        for rule in rules
    ]


def current_frequency_text(
    base_date: date, reference_date: date, rules: Iterable[FrequencyRule]
) -> str:
    if reference_date < base_date:
        return "기준일이 시작일 이전입니다"
    rule = applicable_rule(base_date, reference_date, rules)
    return rule.frequency if rule else "확인 필요"


def ict_rule(accident_date: date, reference_date: date) -> dict[str, str | int]:
    """Return the ICT daily billing guide based on the inclusive injury day."""
    elapsed = day_number(accident_date, reference_date)
    if elapsed < 1:
        return {
            "day": elapsed,
            "phase": "수상일 이전",
            "outpatient": "적용 전",
            "inpatient": "적용 전",
        }
    if elapsed <= 17:
        return {
            "day": elapsed,
            "phase": "수상일로부터 17일까지",
            "outpatient": "1일 1회 / 2부위까지",
            "inpatient": "1일 2회 / 2부위까지",
        }
    return {
        "day": elapsed,
        "phase": "수상일로부터 18일 이후",
        "outpatient": "1일 1회 / 1부위",
        "inpatient": "1일 2회 / 1부위",
    }


def calculate_guide(
    accident_date: date, initial_visit_date: date, reference_date: date
) -> dict[str, object]:
    """Build the complete guide model used by the Streamlit report."""
    if initial_visit_date < accident_date:
        raise ValueError("초진일은 사고일보다 빠를 수 없습니다.")
    if reference_date < accident_date:
        raise ValueError("기준일은 사고일과 같거나 이후여야 합니다.")

    return {
        "injury_day": day_number(accident_date, reference_date),
        "visit_day": day_number(initial_visit_date, reference_date),
        "visit_chuna_current": current_frequency_text(
            accident_date, reference_date, VISIT_CHUNA_RULES
        ),
        "pharmacopuncture_current": current_frequency_text(
            accident_date, reference_date, PHARMACOPUNCTURE_RULES
        ),
        "cupping_current": current_frequency_text(
            initial_visit_date, reference_date, CUPPING_RULES
        ),
        "visit_chuna_schedule": build_schedule(
            accident_date, reference_date, VISIT_CHUNA_RULES
        ),
        "pharmacopuncture_schedule": build_schedule(
            accident_date, reference_date, PHARMACOPUNCTURE_RULES
        ),
        "cupping_schedule": build_schedule(
            initial_visit_date, reference_date, CUPPING_RULES
        ),
        "ict": ict_rule(accident_date, reference_date),
    }
