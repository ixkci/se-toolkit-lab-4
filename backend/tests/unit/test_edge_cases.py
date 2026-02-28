"""Unit tests for edge cases and boundary values.

These tests cover edge cases and boundary values not already tested in the
existing test suite. They focus on:
- Boundary values for numeric fields
- Edge cases for string fields (unicode, special characters, empty strings)
- Database-level constraint edge cases (schema accepts, DB would reject)
"""

from app.models.item import ItemCreate, ItemUpdate
from app.models.learner import LearnerCreate
from app.models.interaction import InteractionLogCreate


class TestItemCreateEdgeCases:
    """Edge case tests for ItemCreate schema."""

    def test_empty_title_is_accepted(self) -> None:
        """Empty title is accepted by schema (may fail at DB level).

        This tests the boundary case: the schema does not enforce min_length.
        """
        item = ItemCreate(title="")
        assert item.title == ""

    def test_very_long_title_is_accepted(self) -> None:
        """Very long titles (1000+ chars) should be accepted by the schema."""
        long_title = "A" * 1000
        item = ItemCreate(title=long_title)
        assert len(item.title) == 1000

    def test_parent_id_zero_is_accepted(self) -> None:
        """parent_id of 0 should be accepted (will fail FK constraint at DB level).

        This is an important edge case: schema allows 0, but DB FK will reject it
        since item IDs start at 1.
        """
        item = ItemCreate(title="Test Item", parent_id=0)
        assert item.parent_id == 0

    def test_default_type_is_step(self) -> None:
        """Default type should be 'step' when not specified."""
        item = ItemCreate(title="Test Item")
        assert item.type == "step"


class TestItemUpdateEdgeCases:
    """Edge case tests for ItemUpdate schema."""

    def test_empty_title_is_accepted(self) -> None:
        """Empty title is accepted by schema."""
        item = ItemUpdate(title="")
        assert item.title == ""

    def test_empty_description_is_accepted(self) -> None:
        """Empty description should be accepted (default behavior)."""
        item = ItemUpdate(title="Valid Title", description="")
        assert item.description == ""

    def test_default_description_is_empty_string(self) -> None:
        """Default description should be empty string."""
        item = ItemUpdate(title="Title")
        assert item.description == ""


class TestLearnerCreateEdgeCases:
    """Edge case tests for LearnerCreate schema."""

    def test_empty_name_is_accepted(self) -> None:
        """Empty name is accepted by schema (may fail at DB level)."""
        learner = LearnerCreate(name="", email="test@example.com")
        assert learner.name == ""

    def test_empty_email_is_accepted(self) -> None:
        """Empty email is accepted by schema (may fail at DB level)."""
        learner = LearnerCreate(name="Test User", email="")
        assert learner.email == ""

    def test_valid_email_with_subdomain_is_accepted(self) -> None:
        """Email with subdomain should be accepted."""
        learner = LearnerCreate(name="Test User", email="test@mail.example.com")
        assert learner.email == "test@mail.example.com"


class TestInteractionLogCreateEdgeCases:
    """Edge case tests for InteractionLogCreate schema."""

    def test_empty_kind_is_accepted(self) -> None:
        """Empty kind is accepted by schema (may fail at DB level)."""
        interaction = InteractionLogCreate(learner_id=1, item_id=1, kind="")
        assert interaction.kind == ""

    def test_zero_learner_id_is_accepted(self) -> None:
        """learner_id of 0 should be accepted by schema (will fail FK at DB level).

        This is an important boundary case: 0 is not a valid learner ID since
        IDs start at 1, but the schema allows it.
        """
        interaction = InteractionLogCreate(learner_id=0, item_id=1, kind="attempt")
        assert interaction.learner_id == 0

    def test_zero_item_id_is_accepted(self) -> None:
        """item_id of 0 should be accepted by schema (will fail FK at DB level)."""
        interaction = InteractionLogCreate(learner_id=1, item_id=0, kind="attempt")
        assert interaction.item_id == 0

    def test_very_long_kind_is_accepted(self) -> None:
        """Very long kind values should be accepted by schema."""
        long_kind = "a" * 100
        interaction = InteractionLogCreate(learner_id=1, item_id=1, kind=long_kind)
        assert len(interaction.kind) == 100


class TestBoundaryValues:
    """Boundary value tests for model schemas."""

    def test_title_at_max_common_length(self) -> None:
        """Title at typical database VARCHAR limit (255 chars) should work."""
        title = "A" * 255
        item = ItemCreate(title=title)
        assert len(item.title) == 255

    def test_title_exceeding_typical_limit(self) -> None:
        """Title exceeding typical VARCHAR limit should still be accepted by schema."""
        title = "A" * 500
        item = ItemCreate(title=title)
        assert len(item.title) == 500

    def test_kind_at_reasonable_length_boundary(self) -> None:
        """Kind at reasonable length boundary should be accepted."""
        kind = "a" * 50  # Reasonable max for interaction kind
        interaction = InteractionLogCreate(learner_id=1, item_id=1, kind=kind)
        assert len(interaction.kind) == 50

    def test_parent_id_at_integer_boundaries(self) -> None:
        """parent_id at integer boundaries should be accepted."""
        # Test large positive and negative values
        item_large = ItemCreate(title="Test", parent_id=2147483647)  # Max int32
        item_negative = ItemCreate(title="Test", parent_id=-2147483648)  # Min int32
        assert item_large.parent_id == 2147483647
        assert item_negative.parent_id == -2147483648
