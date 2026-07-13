from typing import cast

from sqlalchemy import Index, String, Table, UniqueConstraint

from classpath.models.curriculum import CurriculumConcept
from classpath.models.profile import StudentProfile


def test_profile_metadata_matches_foundation_migration_contract() -> None:
    table = cast(Table, StudentProfile.__table__)
    unique_constraints = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    indexes = {
        str(index.name): index
        for index in table.indexes
        if isinstance(index, Index) and index.name is not None
    }

    assert "uq_student_profiles_user_id" in unique_constraints
    assert indexes["ix_student_profiles_user_id"].unique is False
    assert isinstance(table.c.subject.type, String)
    assert table.c.subject.type.length == 16


def test_curriculum_metadata_declares_scope_index() -> None:
    table = cast(Table, CurriculumConcept.__table__)
    indexes = {str(index.name): index for index in table.indexes if index.name is not None}
    scope_index = indexes["ix_curriculum_concepts_scope"]

    assert [column.name for column in scope_index.columns] == [
        "class_level",
        "subject",
        "taxonomy_version",
        "review_status",
    ]
    assert scope_index.unique is False
