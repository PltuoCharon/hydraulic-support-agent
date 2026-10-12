"""
W42-D5 Objective evaluator.

Consumes W41/W42 evaluation records.
Does not modify solver.
"""

from app.models.optimization_objective import (
    ObjectiveValue,
    ConstraintEvaluation,
    OptimizationScore,
)


class ObjectiveEvaluator:


    OBJECTIVE_ID = "CX_RANGE_MM"


    CONSTRAINT_ID = "MOTION_VALID"



    def evaluate_objectives(
        self,
        record,
    ):

        if record.evaluation_status != "SUCCESS":
            return []


        if not hasattr(
            record,
            "evaluation_result"
        ):
            return []


        result = record.evaluation_result


        if not result.candidates:
            return []


        xs = [
            c.front_link_shield.x_mm.value
            for c in result.candidates
        ]


        return [
            ObjectiveValue(
                objective_id=self.OBJECTIVE_ID,
                value=max(xs)-min(xs),
                unit="mm",
                source="W41_EVALUATOR",
            )
        ]



    def evaluate_constraints(
        self,
        record,
    ):

        if record.evaluation_status == "SUCCESS":

            status="PASS"

        else:

            status="UNKNOWN"


        return [
            ConstraintEvaluation(
                constraint_id=self.CONSTRAINT_ID,
                status=status,
                violation_value=None,
                unit="mm",
                source="W41_EVALUATOR",
            )
        ]



    def calculate_score(
        self,
        objectives,
        constraints,
    ):


        feasible = all(
            c.status=="PASS"
            for c in constraints
        )


        return OptimizationScore(
            feasible=feasible,
            objective_values=tuple(
                objectives
            ),
            constraint_status=tuple(
                constraints
            ),
            score_source=
            "W42_D5_OBJECTIVE_FRAMEWORK",
        )
