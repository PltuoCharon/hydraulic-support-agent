"""
W42-D6 Pareto ranking service.

No GA/PSO.
No search.
Only ranking.
"""


from collections.abc import Iterable

from app.models.optimization_ranking import (
    RankedCandidate,
    ParetoFront,
)



def dominates(
    left: tuple[float, ...],
    right: tuple[float, ...],
) -> bool:
    """
    MINIMIZE all objectives.

    left dominates right when:
    - every objective <=
    - at least one objective <
    """

    if len(left) != len(right):
        raise ValueError(
            "objective dimension mismatch"
        )

    return (
        all(
            a <= b
            for a, b in zip(left, right)
        )
        and
        any(
            a < b
            for a, b in zip(left, right)
        )
    )



def pareto_front(
    candidates: Iterable[RankedCandidate],
) -> ParetoFront:

    items = tuple(candidates)

    result = []

    for candidate in items:

        dominated = False

        for other in items:

            if other.candidate_id == candidate.candidate_id:
                continue

            if (
                other.feasible
                and
                not candidate.feasible
            ):
                dominated = True
                break

            if (
                other.feasible
                ==
                candidate.feasible
                and
                dominates(
                    other.objective_values,
                    candidate.objective_values,
                )
            ):
                dominated = True
                break


        if not dominated:
            result.append(
                RankedCandidate(
                    candidate_id=candidate.candidate_id,
                    objective_values=candidate.objective_values,
                    feasible=candidate.feasible,
                    rank=0,
                    dominance_count=0,
                )
            )


    return ParetoFront(
        candidates=tuple(result),
        total_candidates=len(items),
        feasible_candidates=sum(
            c.feasible for c in items
        ),
    )
