"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


# --- New Unit Tests ---


def test_filter_returns_multiple_interactions_with_matching_ids() -> None:
    """Tests that the filter correctly returns multiple interactions when item_id matches."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
        _make_log(3, 1, 1),  # Another interaction for item_id 1
        _make_log(4, 3, 3),
    ]
    item_to_filter = 1
    result = _filter_by_item_id(interactions, item_to_filter)

    assert len(result) == 2
    # Check that the returned interactions are indeed the ones with item_id 1
    for log in result:
        assert log.item_id == item_to_filter
    # Optionally, check specific IDs if their order is guaranteed or important
    # assert {log.id for log in result} == {1, 3}


def test_filter_returns_empty_when_no_interactions_match_item_id() -> None:
    """Tests that the filter returns an empty list when no interactions match the provided item_id."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2), _make_log(3, 3, 3)]
    non_existent_item_id = 99
    result = _filter_by_item_id(interactions, non_existent_item_id)

    assert result == []
    assert len(result) == 0

def test_filter_includes_interaction_with_different_learner_id_but_matching_item_id() -> None:
    """
    Tests that an interaction with a different learner_id but a matching item_id
    is correctly included in the filtered results. This targets the boundary
    where learner_id is not a factor in item_id filtering.
    """
    interactions = [
        _make_log(1, 1, 1),  # Match for item_id=1
        _make_log(2, 2, 2),  # No match for item_id=1
        _make_log(3, 2, 1),  # Different learner_id (2), but matching item_id (1)
        _make_log(4, 1, 3),  # No match for item_id=1
    ]
    item_to_filter = 1
    result = _filter_by_item_id(interactions, item_to_filter)

    assert len(result) == 2
    # Assert that the interaction with learner_id=2 and item_id=1 is present
    found_interaction_with_different_learner = False
    for log in result:
        if log.id == 3 and log.learner_id == 2 and log.item_id == 1:
            found_interaction_with_different_learner = True
        assert log.item_id == item_to_filter  # Ensure all returned logs match item_id

    assert found_interaction_with_different_learner, "Interaction with different learner_id but matching item_id was not found."
    assert {log.id for log in result} == {1, 3}