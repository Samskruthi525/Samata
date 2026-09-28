"""Visitor state machine for the Pi kiosk (design doc §5, prototype HTML).

States: BOOT -> ATTRACT -> ACTIVE <-> IDLE_WARNING -> RESETTING -> ATTRACT.
The physical HOME button (BCM27) and idle timeout run the SAME reset routine;
neither destroys the offline cache. Network loss is an orthogonal flag.
Defaults mirror the HTML prototype: idle 120 s, countdown 20 s (CONFIGURABLE).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class State(str, Enum):
    BOOT = "BOOT"
    ATTRACT = "ATTRACT"
    ACTIVE = "ACTIVE"
    IDLE_WARNING = "IDLE_WARNING"
    RESETTING = "RESETTING"


class Event(str, Enum):
    BOOT_DONE = "boot_done"
    PIR_MOTION = "visitor_approached"   # BCM17 rising edge
    TOUCH = "touch"
    HOME = "home_pressed"               # BCM27, debounced
    TICK = "tick"                       # 1 s timer
    EXTEND = "extend"
    NET_DOWN = "net_down"
    NET_UP = "net_up"


@dataclass
class Session:
    reading_list: list[str] = field(default_factory=list)
    question_state: str | None = None
    media_playing: bool = False
    screens: list[str] = field(default_factory=list)


@dataclass
class Kiosk:
    idle_s: int = 120
    countdown_s: int = 20
    pir_warmup_s: int = 30              # TBD per module datasheet
    pir_cooldown_s: int = 10            # ignore repeated triggers (no wake loop)
    state: State = State.BOOT
    online: bool = True
    uptime_s: int = 0
    idle_for: int = 0
    countdown: int = 0
    last_wake_at: int | None = None
    session: Session = field(default_factory=Session)
    cache_items: frozenset[str] = frozenset()
    log: list[str] = field(default_factory=list)

    # -- helpers
    def _reset(self, why: str) -> None:
        self.state = State.RESETTING
        self.session = Session()            # clears list, question buffer, media
        self.idle_for = self.countdown = 0
        self.log.append(f"reset:{why}")
        self.state = State.ATTRACT          # cache_items intentionally untouched

    def handle(self, ev: Event | str) -> State:
        ev = Event(ev)
        if ev is Event.NET_DOWN:
            self.online = False
        elif ev is Event.NET_UP:
            self.online = True
        elif ev is Event.BOOT_DONE and self.state is State.BOOT:
            self.state = State.ATTRACT
        elif ev is Event.TICK:
            self.uptime_s += 1
            if self.state is State.ACTIVE:
                self.idle_for += 1
                if self.idle_for >= self.idle_s:
                    self.state, self.countdown = State.IDLE_WARNING, self.countdown_s
            elif self.state is State.IDLE_WARNING:
                self.countdown -= 1
                if self.countdown <= 0:
                    self._reset("idle")
        elif ev is Event.PIR_MOTION:
            if self.state is State.ATTRACT and self.uptime_s >= self.pir_warmup_s:
                if self.last_wake_at is None or self.uptime_s - self.last_wake_at >= self.pir_cooldown_s:
                    self.state, self.idle_for, self.last_wake_at = State.ACTIVE, 0, self.uptime_s
                    self.log.append("wake:pir")
            elif self.state is State.ACTIVE:
                self.idle_for = 0               # presence counts as activity
        elif ev is Event.TOUCH:
            if self.state in (State.ATTRACT, State.ACTIVE):
                self.state, self.idle_for = State.ACTIVE, 0
        elif ev is Event.EXTEND and self.state is State.IDLE_WARNING:
            self.state, self.idle_for = State.ACTIVE, 0
        elif ev is Event.HOME and self.state in (State.ACTIVE, State.IDLE_WARNING, State.ATTRACT):
            self._reset("home")
        return self.state

    @property
    def assistant_available(self) -> bool:
        return self.online
