"""Tests explicitly designed to exercise both outcomes of decisions."""
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def batch(approved=True, fmt="paperback", books=None, credit=False):
    return {
        "intake_approved": approved,
        "format": fmt,
        "books": books if books is not None else [{"missing_pages": 0, "condition": "good", "counterfeit": False}],
        "payout_in_credit": credit,
    }


@pytest.mark.parametrize("batches,bonus", [
    ("not-a-list", 0),
    ([], -1),
])
def test_each_invalid_input_guard(batches, bonus):
    with pytest.raises(ValueError):
        process_book_buybacks(batches, bonus)


def test_approved_and_unapproved_paths():
    result = process_book_buybacks([batch(approved=False), batch()], 0)
    assert result["total_payout"] == 8.0


@pytest.mark.parametrize("fmt,value", [("textbook", 40.0), ("hardcover", 15.0), ("paperback", 8.0)])
def test_each_known_format_branch(fmt, value):
    assert process_book_buybacks([batch(fmt=fmt)], 0)["total_payout"] == value


def test_unknown_format_branch():
    assert process_book_buybacks([batch(fmt="ebook")], 0)["status"] == "ZERO_CREDIT"


def test_missing_pages_true_and_false_paths():
    result = process_book_buybacks([batch(books=[
        {"missing_pages": 1, "condition": "good"},
        {"missing_pages": 0, "condition": "good"},
    ])], 0)
    assert result["total_payout"] == 8.0


def test_counterfeit_textbook_and_non_textbook_paths():
    textbook = process_book_buybacks([batch(fmt="textbook", books=[{"counterfeit": True}])], 0)
    paperback = process_book_buybacks([batch(books=[{"counterfeit": True}, {"condition": "good"}])], 0)
    assert textbook["status"] == "ZERO_CREDIT"
    assert paperback["total_payout"] == 8.0


@pytest.mark.parametrize("condition,multiplier", [("mint", 1.25), ("poor", 0.40), ("good", 1.0), ("unknown", 1.0)])
def test_condition_decision_paths(condition, multiplier):
    result = process_book_buybacks([batch(books=[{"condition": condition}])], 0)
    assert result["total_payout"] == 8.0 * multiplier


def test_store_credit_enabled_and_disabled():
    without_bonus = process_book_buybacks([batch(credit=False)], 5)
    with_bonus = process_book_buybacks([batch(credit=True)], 5)
    assert without_bonus["total_payout"] == 8.0
    assert with_bonus["total_payout"] == 13.0


def test_audit_threshold_false_and_true():
    not_audit = process_book_buybacks([batch(books=[{"missing_pages": 1} for _ in range(4)])], 0)
    audit = process_book_buybacks([batch(books=[{"missing_pages": 1} for _ in range(5)])], 0)
    assert not_audit["status"] == "ZERO_CREDIT"
    assert audit["status"] == "AUDIT_REJECTED"


def test_zero_payout_and_completed_status():
    assert process_book_buybacks([], 0)["status"] == "ZERO_CREDIT"
    assert process_book_buybacks([batch()], 0)["status"] == "COMPLETED"


def test_scanner_empty_vs_nonempty_matrix():
    assert inspect_scanner_calibration([]) == "NO_DATA"
    assert inspect_scanner_calibration([[1, 2, 3]]) == "CALIBRATED"


def test_scanner_high_rate_then_low_resets_streak():
    assert inspect_scanner_calibration([[7, 2, 8]]) == "CALIBRATED"


def test_scanner_two_consecutive_high_rates():
    assert inspect_scanner_calibration([[6, 6]]) == "RECALIBRATE"


def test_scanner_only_one_high_rate_per_device_is_not_consecutive():
    assert inspect_scanner_calibration([[6], [7]]) == "CALIBRATED"
