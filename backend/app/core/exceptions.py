class ThesisFormatError(Exception):
    """Base application exception."""


class InvalidDocumentError(ThesisFormatError):
    """Raised when an uploaded document cannot be processed."""


class UnsupportedDegreeError(ThesisFormatError):
    """Raised when no rule set exists for the requested degree."""
