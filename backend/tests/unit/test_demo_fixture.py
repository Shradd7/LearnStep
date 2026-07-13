from classpath.scripts.seed_demo_curriculum import load_demo_records


def test_demo_curriculum_is_small_and_explicitly_synthetic() -> None:
    records = load_demo_records()
    assert 1 <= len(records) <= 8
    assert {record["review_status"] for record in records} == {"synthetic_demo"}
    assert {record["source_type"] for record in records} == {"synthetic_demo"}
    assert {record["class_level"] for record in records}.issubset({5, 6, 7, 8})
    assert {record["subject"] for record in records}.issubset({"mathematics", "science"})
