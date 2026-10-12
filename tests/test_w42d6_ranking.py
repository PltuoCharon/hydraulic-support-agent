from app.models.optimization_ranking import RankedCandidate
from app.services.ranking_service import (
    dominates,
    pareto_front,
)



def candidate(
    cid,
    values,
    feasible=True,
):
    return RankedCandidate(
        candidate_id=cid,
        objective_values=values,
        feasible=feasible,
        rank=0,
        dominance_count=0,
    )



def test_single_objective_domination():

    assert dominates(
        (1,),
        (2,)
    )

    assert not dominates(
        (2,),
        (1,)
    )



def test_multi_objective_tradeoff():

    a = candidate(
        "A",
        (1,10)
    )

    b = candidate(
        "B",
        (10,1)
    )

    result = pareto_front(
        [
            a,
            b,
        ]
    )

    assert len(result.candidates)==2



def test_clear_winner():

    a = candidate(
        "A",
        (1,1)
    )

    b = candidate(
        "B",
        (2,2)
    )


    result = pareto_front(
        [
            a,
            b,
        ]
    )

    ids = {
        c.candidate_id
        for c in result.candidates
    }

    assert ids == {"A"}



def test_failed_candidate_not_selected():

    failed = candidate(
        "FAIL",
        (0,),
        False
    )

    success = candidate(
        "GOOD",
        (10,),
        True
    )


    result = pareto_front(
        [
            failed,
            success,
        ]
    )


    ids = {
        c.candidate_id
        for c in result.candidates
    }


    assert ids == {"GOOD"}



def test_dimension_mismatch():

    try:
        dominates(
            (1,),
            (1,2)
        )

    except ValueError:
        return


    assert False
