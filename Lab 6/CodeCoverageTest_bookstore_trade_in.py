"""Tests focused on statement/line coverage for bookstore_trade_in.py."""
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def batch(**overrides):
    data = {
        "intake_approved": True,
        "format": "paperback",
        "payout_in_credit": False,
        "books": [{"missing_pages": 0, "condition": "good", "counterfeit": False}],
    }
    data.update(overrides)
    return data


def test_existing_good_paperback():
    assert process_book_buybacks([batch()], 5.0) == {
        "total_payout": 8.0, "status": "COMPLETED"
    }


def test_invalid_batches_type():
    with pytest.raises(ValueError):
        process_book_buybacks("not a list", 5.0)


def test_negative_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks([], -1.0)


def test_unapproved_batch_is_skipped():
    assert process_book_buybacks([batch(intake_approved=False)], 5.0)["status"] == "ZERO_CREDIT"


def test_default_format_and_books():
    # Missing format defaults to paperback and missing books defaults to an empty list.
    assert process_book_buybacks([{"intake_approved": True}], 5.0)["status"] == "ZERO_CREDIT"


@pytest.mark.parametrize(
    ("format_type", "condition", "expected"),
    [
        ("textbook", "good", 40.0),
        ("hardcover", "good", 15.0),
        ("paperback", "good", 8.0),
        ("textbook", "mint", 50.0),
        ("hardcover", "mint", 18.75),
        ("paperback", "mint", 10.0),
        ("textbook", "poor", 16.0),
        ("hardcover", "poor", 6.0),
        ("paperback", "poor", 3.2),
        ("paperback", "used", 8.0),
    ],
)
def test_format_and_condition_values(format_type, condition, expected):
    result = process_book_buybacks(
        [batch(format=format_type, books=[{"condition": condition}])], 0.0
    )
    assert result["total_payout"] == expected
    assert result["status"] == "COMPLETED"


def test_unknown_format_is_rejected():
    result = process_book_buybacks([batch(format="ebook")], 0.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_missing_pages_are_rejected():
    result = process_book_buybacks(
        [batch(books=[{"missing_pages": 2, "condition": "good"}])], 0.0
    )
    assert result["status"] == "ZERO_CREDIT"


def test_counterfeit_paperback_does_not_add_credit():
    result = process_book_buybacks(
        [batch(books=[{"counterfeit": True}, {"condition": "good"}])], 0.0
    )
    assert result["total_payout"] == 8.0
    assert result["status"] == "COMPLETED"


def test_counterfeit_textbook_zeros_batch_credit_and_breaks():
    result = process_book_buybacks(
        [batch(format="textbook", books=[
            {"condition": "good"},
            {"counterfeit": True},
            {"condition": "mint"},
        ])], 0.0
    )
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_store_credit_bonus():
    result = process_book_buybacks([batch(payout_in_credit=True)], 5.0)
    assert result["total_payout"] == 13.0


def test_audit_rejected_after_more_than_four_rejections():
    books = [{"missing_pages": 1} for _ in range(5)]
    result = process_book_buybacks([batch(books=books)], 0.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_empty_batches_zero_credit():
    assert process_book_buybacks([], 0.0) == {
        "total_payout": 0.0, "status": "ZERO_CREDIT"
    }


def test_scanner_empty_matrix():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_calibrated_for_low_and_isolated_high_rates():
    assert inspect_scanner_calibration([[1, 6, 3, 7, 2], [5, 0]]) == "CALIBRATED"


def test_scanner_recalibrates_on_two_consecutive_high_rates():
    assert inspect_scanner_calibration([[1, 6, 5.1]]) == "RECALIBRATE"


def test_scanner_streak_resets_and_starts_fresh_for_each_device():
    assert inspect_scanner_calibration([[7, 2, 8], [6, 6]]) == "RECALIBRATE"
