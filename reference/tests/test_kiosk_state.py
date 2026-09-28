from heritage_core.kiosk_state import Kiosk, Event, State


def booted(**kw):
    k = Kiosk(**kw)
    k.handle(Event.BOOT_DONE)
    for _ in range(k.pir_warmup_s):
        k.handle(Event.TICK)
    return k


def test_pir_ignored_during_warmup():
    k = Kiosk(); k.handle(Event.BOOT_DONE)
    assert k.handle(Event.PIR_MOTION) is State.ATTRACT


def test_pir_wakes_once_not_loop():
    k = booted()
    assert k.handle(Event.PIR_MOTION) is State.ACTIVE
    k.handle(Event.HOME)
    assert k.handle(Event.PIR_MOTION) is State.ATTRACT   # inside cooldown
    for _ in range(k.pir_cooldown_s):
        k.handle(Event.TICK)
    assert k.handle(Event.PIR_MOTION) is State.ACTIVE


def test_idle_warning_then_reset_clears_session_keeps_cache():
    k = booted(idle_s=5, countdown_s=3)
    k.cache_items = frozenset({"WS-001"})
    k.handle(Event.TOUCH); k.session.reading_list.append("WS-001"); k.session.media_playing = True
    for _ in range(5):
        k.handle(Event.TICK)
    assert k.state is State.IDLE_WARNING
    for _ in range(3):
        k.handle(Event.TICK)
    assert k.state is State.ATTRACT and not k.session.reading_list and not k.session.media_playing
    assert k.cache_items == frozenset({"WS-001"}) and k.log[-1] == "reset:idle"


def test_extend_returns_to_active():
    k = booted(idle_s=2, countdown_s=5)
    k.handle(Event.TOUCH); k.handle(Event.TICK); k.handle(Event.TICK)
    assert k.handle(Event.EXTEND) is State.ACTIVE


def test_home_same_reset_as_timeout():
    k = booted(); k.handle(Event.TOUCH); k.session.question_state = "draft question"
    assert k.handle(Event.HOME) is State.ATTRACT and k.session.question_state is None
    assert k.log[-1] == "reset:home"


def test_network_loss_disables_assistant_only():
    k = booted(); k.handle(Event.TOUCH); k.handle(Event.NET_DOWN)
    assert k.state is State.ACTIVE and not k.assistant_available
