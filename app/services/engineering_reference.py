"""
W43-D2 engineering reference registry.

Evidence isolation storage.
Never promotes verification_level.
"""

from app.models.engineering_reference import EngineeringReference


class EngineeringReferenceRegistry:

    def __init__(self):

        self._references = {}


    def register(
        self,
        reference: EngineeringReference,
    ):

        if reference.reference_id in self._references:
            raise ValueError(
                "reference already exists"
            )

        self._references[
            reference.reference_id
        ] = reference


    def get(
        self,
        reference_id: str,
    ):

        return self._references.get(
            reference_id
        )


    def list(self):

        return tuple(
            self._references.values()
        )
