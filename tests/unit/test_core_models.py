import pytest
from pydantic import TypeAdapter, ValidationError

from adaptrag.core.elements import Element, ElementType, Origin
from adaptrag.core.locators import BBox, Locator, PageLocator, TimeLocator


def test_page_locator_defaults_to_no_boxes():
    loc = PageLocator(page=1)
    assert loc.kind == "page"
    assert loc.boxes == []


def test_page_numbers_start_at_one():
    with pytest.raises(ValidationError):
        PageLocator(page=0)


def test_bbox_is_normalized_and_ordered():
    BBox(x0=0.1, y0=0.1, x1=0.9, y1=0.5)
    with pytest.raises(ValidationError):
        BBox(x0=0.1, y0=0.1, x1=1.5, y1=0.5)  # outside 0..1
    with pytest.raises(ValidationError):
        BBox(x0=0.9, y0=0.1, x1=0.1, y1=0.5)  # x1 before x0


def test_time_locator_end_not_before_start():
    TimeLocator(start=1.0, end=2.0, speaker="A")
    with pytest.raises(ValidationError):
        TimeLocator(start=5.0, end=2.0)


def test_locator_union_picks_class_from_kind():
    adapter = TypeAdapter(Locator)
    assert isinstance(adapter.validate_python({"kind": "page", "page": 3}), PageLocator)
    assert isinstance(
        adapter.validate_python({"kind": "time", "start": 0, "end": 1}), TimeLocator
    )
    with pytest.raises(ValidationError):
        adapter.validate_python({"kind": "slide", "number": 1})


def test_element_minimal():
    e = Element(id="e1", type=ElementType.PARAGRAPH, text="Hello")
    assert e.origin is Origin.EXTRACTED
    assert e.parent_id is None
    assert e.locator is None


def test_element_accepts_core_and_namespaced_types():
    Element(id="e1", type="paragraph")
    Element(id="e2", type="forms/checkbox")
    with pytest.raises(ValidationError):
        Element(id="e3", type="made up")


def test_element_requires_nonempty_id():
    with pytest.raises(ValidationError):
        Element(id="", type="paragraph")


def test_quality_between_zero_and_one():
    Element(id="e1", type="paragraph", quality=0.8)
    with pytest.raises(ValidationError):
        Element(id="e1", type="paragraph", quality=1.5)


def test_json_round_trip_keeps_locator_class():
    box = BBox(x0=0, y0=0, x1=0.5, y1=0.1)
    e = Element(
        id="e1", type="paragraph", text="Hi", locator=PageLocator(page=2, boxes=[box])
    )
    again = Element.model_validate_json(e.model_dump_json())
    assert again == e
    assert isinstance(again.locator, PageLocator)
