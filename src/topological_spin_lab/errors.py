class TopologicalSpinLabError(Exception):
    """Base package exception."""


class SpecValidationError(TopologicalSpinLabError):
    """Raised when an experiment specification is invalid."""
