import pytest
from heritage_core.rights import RightsPolicy, RightsState, ReviewStatus, Action, permitted, permission_matrix

ALL = list(Action)


@pytest.mark.parametrize("state", ["unknown", "permission_pending", "withdrawn"])
def test_closed_states_block_everything(state):
    pol = RightsPolicy.from_state(state, public_display=True, ai_processing_allowed=True,
                                  offline_cache_allowed=True, download_allowed=True)
    assert not any(permitted(pol, "published", a) for a in ALL)
    assert not any(permitted(pol, "published", a, staff=True) for a in ALL)


def test_unpublished_never_public():
    pol = RightsPolicy.from_state("public_display_approved", ai_processing_allowed=True)
    for st in ("draft", "in_review", "approved_1"):
        assert not permitted(pol, st, Action.LIST)


def test_link_only_lists_but_does_not_mirror():
    pol = RightsPolicy.from_state("link_only", ai_processing_allowed=True, offline_cache_allowed=True)
    assert permitted(pol, "published", Action.LIST)
    for a in (Action.VIEW_ACCESS_COPY, Action.SEARCH_INDEX, Action.AI_CONTEXT, Action.OFFLINE_CACHE, Action.DOWNLOAD):
        assert not permitted(pol, "published", a)


def test_permissions_are_independent():
    pol = RightsPolicy.from_state("public_display_approved")  # AI/offline/download default False
    assert permitted(pol, "published", Action.VIEW_ACCESS_COPY)
    assert not permitted(pol, "published", Action.AI_CONTEXT)
    assert not permitted(pol, "published", Action.OFFLINE_CACHE)
    assert not permitted(pol, "published", Action.DOWNLOAD)


def test_restricted_staff_only():
    pol = RightsPolicy.from_state("restricted_to_staff")
    assert not permitted(pol, "published", Action.LIST)
    assert permitted(pol, "published", Action.LIST, staff=True)


def test_withdrawn_status_overrides_rights():
    pol = RightsPolicy.from_state("public_display_approved", ai_processing_allowed=True)
    assert not permitted(pol, ReviewStatus.WITHDRAWN, Action.LIST)


def test_matrix_shape():
    m = permission_matrix()
    assert set(m) == {s.value for s in RightsState}
    assert m["public_display_approved"]["view"] and not m["public_display_approved"]["download"]
