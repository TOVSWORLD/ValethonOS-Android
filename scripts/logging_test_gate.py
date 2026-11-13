"""Physical testing hold until a reviewed known-kernel logging control is qualified.

There is deliberately no flag, receipt boolean or model-result override. Read-only
collection and original restoration do not call this gate. Replacing this hold
requires a reviewed control procedure and validation of its actual fresh raw log.
"""


def require_logging_control():
    raise ValueError(
        'Physical diagnostic testing held: no known-kernel logging control has '
        'produced a verified fresh kernel log through the actual collector')
