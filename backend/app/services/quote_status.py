QUOTE_STATUS_DRAFT = "draft"
QUOTE_STATUS_SENT = "sent"
QUOTE_STATUS_ACCEPTED = "accepted"
QUOTE_STATUS_REJECTED = "rejected"
QUOTE_STATUS_EXPIRED = "expired"

QUOTE_STATUSES = {
    QUOTE_STATUS_DRAFT,
    QUOTE_STATUS_SENT,
    QUOTE_STATUS_ACCEPTED,
    QUOTE_STATUS_REJECTED,
    QUOTE_STATUS_EXPIRED,
}

QUOTE_STATUS_TRANSITIONS = {
    QUOTE_STATUS_DRAFT: {
        QUOTE_STATUS_SENT,
        QUOTE_STATUS_EXPIRED,
    },
    QUOTE_STATUS_SENT: {
        QUOTE_STATUS_ACCEPTED,
        QUOTE_STATUS_REJECTED,
        QUOTE_STATUS_EXPIRED,
    },
    QUOTE_STATUS_ACCEPTED: set(),
    QUOTE_STATUS_REJECTED: set(),
    QUOTE_STATUS_EXPIRED: set(),
}


class InvalidQuoteStatusError(ValueError):
    pass


class InvalidQuoteStatusTransitionError(ValueError):
    pass


def normalize_quote_status(status: str) -> str:
    return status.strip().lower()


def validate_quote_status(status: str) -> str:
    normalized_status = normalize_quote_status(status)

    if normalized_status not in QUOTE_STATUSES:
        raise InvalidQuoteStatusError("Invalid quote status")

    return normalized_status


def validate_quote_status_transition(
    current_status: str,
    next_status: str,
) -> str:
    normalized_current_status = validate_quote_status(current_status)
    normalized_next_status = validate_quote_status(next_status)

    if normalized_current_status == normalized_next_status:
        return normalized_next_status

    allowed_next_statuses = QUOTE_STATUS_TRANSITIONS[normalized_current_status]

    if normalized_next_status not in allowed_next_statuses:
        raise InvalidQuoteStatusTransitionError(
            f"Quote status cannot change from {normalized_current_status} to {normalized_next_status}"
        )

    return normalized_next_status
