import pytest

from app.models.optimization_objective import (
    ObjectiveDefinition,
    ObjectiveValue,
    ConstraintEvaluation,
)

from app.services.objective_evaluator import (
    ObjectiveEvaluator,
)



def test_objective_definition():

    obj = ObjectiveDefinition(
        objective_id="CX_RANGE",
        name="Cx range",
        direction="MAXIMIZE",
        unit="mm",
        description="test",
    )

    assert obj.unit=="mm"



def test_objective_reject_nan():

    with pytest.raises(ValueError):

        ObjectiveValue(
            objective_id="A",
            value=float("nan"),
            unit="mm",
            source="test",
        )



def test_unknown_constraint():

    c = ConstraintEvaluation(
        constraint_id="MOTION",
        status="UNKNOWN",
        violation_value=None,
        unit="mm",
        source="test",
    )

    assert c.status=="UNKNOWN"



def test_unknown_not_pass():

    c = ConstraintEvaluation(
        constraint_id="MOTION",
        status="UNKNOWN",
        violation_value=None,
        unit="mm",
        source="test",
    )

    assert c.status!="PASS"



def test_score():

    evaluator=ObjectiveEvaluator()

    result=evaluator.calculate_score(
        [],
        [
            ConstraintEvaluation(
                constraint_id="MOTION",
                status="PASS",
                violation_value=None,
                unit="mm",
                source="test",
            )
        ]
    )


    assert result.feasible
