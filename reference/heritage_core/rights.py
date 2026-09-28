"""Rights gate.

Display, download, derivative/translation and AI processing are *separate*
decisions (design doc §3). Material that is ``unknown`` or
``permission_pending`` never reaches public listing, search, the AI context
or the offline bundle.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RightsState(str, Enum):
    UNKNOWN = "unknown"
    PERMISSION_PENDING = "permission_pending"
    PUBLIC_DISPLAY_APPROVED = "public_display_approved"
    RESTRICTED_TO_STAFF = "restricted_to_staff"
    LINK_ONLY = "link_only"
    WITHDRAWN = "withdrawn"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED_1 = "approved_1"      # first (content) reviewer approved
    PUBLISHED = "published"        # second reviewer published
    WITHDRAWN = "withdrawn"


class Action(str, Enum):
    LIST = "list"                  # appear in public listing / browse
    VIEW_ACCESS_COPY = "view"      # open access derivative on kiosk/web
    SEARCH_INDEX = "search"        # enter public lexical/vector index
    AI_CONTEXT = "ai"              # be sent to a model as evidence
    OFFLINE_CACHE = "offline"      # be copied to the Pi offline bundle
    DOWNLOAD = "download"          # visitor download / QR handoff


@dataclass(frozen=True)
class RightsPolicy:
    state: RightsState
    public_display: bool = False
    download_allowed: bool = False
    derivative_allowed: bool = False
    ai_processing_allowed: bool = False
    offline_cache_allowed: bool = False

    @classmethod
    def from_state(cls, state: str | RightsState, **overrides) -> "RightsPolicy":
        s = RightsState(state)
        defaults = dict(public_display=s is RightsState.PUBLIC_DISPLAY_APPROVED)
        defaults.update(overrides)
        return cls(state=s, **defaults)


CLOSED_STATES = {RightsState.UNKNOWN, RightsState.PERMISSION_PENDING, RightsState.WITHDRAWN}


def permitted(policy: RightsPolicy, status: ReviewStatus | str, action: Action, *, staff: bool = False) -> bool:
    """Return True only if *action* is allowed. Fail closed on anything unexpected."""
    status = ReviewStatus(status)
    action = Action(action)
    if policy.state in CLOSED_STATES or status is ReviewStatus.WITHDRAWN:
        return False
    if staff:
        # staff may see restricted material in the admin UI, never via public routes
        return action in (Action.LIST, Action.VIEW_ACCESS_COPY, Action.SEARCH_INDEX) or (
            action is Action.AI_CONTEXT and policy.ai_processing_allowed)
    if status is not ReviewStatus.PUBLISHED:
        return False
    if policy.state is RightsState.RESTRICTED_TO_STAFF:
        return False
    if policy.state is RightsState.LINK_ONLY:
        # catalogue card + outbound source reference only; no mirrored content
        return action is Action.LIST
    # PUBLIC_DISPLAY_APPROVED
    if action in (Action.LIST, Action.VIEW_ACCESS_COPY, Action.SEARCH_INDEX):
        return policy.public_display
    if action is Action.AI_CONTEXT:
        return policy.public_display and policy.ai_processing_allowed
    if action is Action.OFFLINE_CACHE:
        return policy.public_display and policy.offline_cache_allowed
    if action is Action.DOWNLOAD:
        return policy.public_display and policy.download_allowed
    return False


def permission_matrix() -> dict[str, dict[str, bool]]:
    """Matrix used by docs/diagram generation: default policy per state, published item."""
    out: dict[str, dict[str, bool]] = {}
    for s in RightsState:
        pol = RightsPolicy.from_state(s, ai_processing_allowed=True, offline_cache_allowed=True,
                                      download_allowed=False)
        out[s.value] = {a.value: permitted(pol, ReviewStatus.PUBLISHED, a) for a in Action}
    return out
