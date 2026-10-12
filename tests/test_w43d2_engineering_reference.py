from datetime import datetime

import pytest

from pydantic import ValidationError

from app.models.engineering_reference import (
    EngineeringParameter,
    EngineeringReference,
)

from app.services.engineering_reference import (
    EngineeringReferenceRegistry,
)



def reference(**overrides):

    data = {
        "reference_id": "REF-0001",
        "name": "四连杆数学实验基线",
        "source_type": "SYNTHETIC_MATH",
        "verification_level": "UNKNOWN",
        "description": "W41 synthetic evaluation baseline",
        "created_time": datetime(2026, 10, 12, 9, 0, 0),
    }

    data.update(overrides)

    return EngineeringReference(**data)



def parameter(**overrides):

    data = {
        "name": "AB",
        "value": 320.0,
        "unit": "mm",
        "source_reference": "REF-0001",
        "verified": False,
    }

    data.update(overrides)

    return EngineeringParameter(**data)



def test_create_reference():

    ref = reference()

    assert ref.reference_id == "REF-0001"

    assert ref.source_type == "SYNTHETIC_MATH"

    assert ref.verification_level == "UNKNOWN"



def test_create_parameter():

    p = parameter()

    assert p.name == "AB"

    assert p.unit == "mm"

    assert p.source_reference == "REF-0001"

    assert p.verified is False



def test_source_type_restriction():

    with pytest.raises(ValidationError):

        reference(source_type="FIELD_MEASUREMENT")



def test_verification_level_restriction():

    with pytest.raises(ValidationError):

        reference(verification_level="EXPERT_APPROVED")



def test_reference_id_pattern():

    with pytest.raises(ValidationError):

        reference(reference_id="")



def test_parameter_requires_finite_value():

    with pytest.raises(ValidationError):

        parameter(value=float("inf"))



def test_parameter_requires_unit():

    with pytest.raises(ValidationError):

        parameter(unit="")



def test_register_and_get():

    registry = EngineeringReferenceRegistry()

    ref = reference()

    registry.register(ref)

    assert registry.get("REF-0001") is ref

    assert registry.get("MISSING") is None



def test_duplicate_register_rejected():

    registry = EngineeringReferenceRegistry()

    registry.register(reference())

    with pytest.raises(ValueError):

        registry.register(reference())



def test_list_returns_all():

    registry = EngineeringReferenceRegistry()

    registry.register(reference(reference_id="REF-0001"))

    registry.register(
        reference(
            reference_id="REF-0002",
            source_type="ENGINEERING_REFERENCE",
            verification_level="ENGINEERING_VERIFIED",
        )
    )

    listed = registry.list()

    assert len(listed) == 2

    assert listed[0].reference_id == "REF-0001"

    assert listed[1].reference_id == "REF-0002"



def test_no_auto_promotion_on_register():

    registry = EngineeringReferenceRegistry()

    registry.register(
        reference(verification_level="UNKNOWN")
    )

    got = registry.get("REF-0001")

    assert got.verification_level == "UNKNOWN"



def test_no_promotion_method_exists():

    registry = EngineeringReferenceRegistry()

    assert not hasattr(registry, "promote")

    assert not hasattr(registry, "upgrade")

    assert not hasattr(registry, "update")



def test_json_roundtrip():

    ref = reference()

    restored = EngineeringReference.model_validate_json(
        ref.model_dump_json()
    )

    assert restored == ref

    p = parameter()

    restored_p = EngineeringParameter.model_validate_json(
        p.model_dump_json()
    )

    assert restored_p == p



def test_json_roundtrip_preserves_enums():

    ref = reference(
        source_type="EXTERNAL_DATA",
        verification_level="DATA_SUPPORTED",
    )

    restored = EngineeringReference.model_validate_json(
        ref.model_dump_json()
    )

    assert restored.source_type == "EXTERNAL_DATA"

    assert restored.verification_level == "DATA_SUPPORTED"



def test_immutable():

    ref = reference()

    with pytest.raises(ValidationError):

        ref.verification_level = "ENGINEERING_VERIFIED"

    p = parameter()

    with pytest.raises(ValidationError):

        p.value = 1.0
