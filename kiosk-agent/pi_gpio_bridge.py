#!/usr/bin/env python3
"""Pi GPIO bridge: PIR (BCM17) + HOME button (BCM27) -> loopback event endpoint.

Runs on Raspberry Pi OS with GPIO Zero + lgpio (the pin factory GPIO Zero
documents for Pi 5). For development on a laptop set GPIOZERO_PIN_FACTORY=mock.

Environment:
  KIOSK_EVENT_URL   loopback endpoint, default http://127.0.0.1:8765/device/event
  KIOSK_PIR_PIN     default 17 (BCM)      KIOSK_HOME_PIN   default 27 (BCM)
  KIOSK_LED_PIN     default 22 (BCM, optional; empty string disables)
  KIOSK_PIR_COOLDOWN_S  default 10        KIOSK_DEVICE_ID  label only, no secrets

The bridge refuses non-loopback URLs: raw motion/button events never go to the cloud.
"""
from __future__ import annotations

import ipaddress
import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request

log = logging.getLogger("heritage.gpio")


def loopback_only(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or ""
    try:
        ok = ipaddress.ip_address(host).is_loopback
    except ValueError:
        ok = host == "localhost"
    if not ok:
        raise ValueError(f"KIOSK_EVENT_URL must be loopback, got {host!r}")
    return url


class Bridge:
    def __init__(self, url: str, device_id: str = "DEMO-KIOSK-01", cooldown_s: float = 10.0,
                 clock=time.monotonic, sender=None):
        self.url = loopback_only(url)
        self.device_id = device_id
        self.cooldown_s = cooldown_s
        self.clock = clock
        self._last_motion = None
        self.sender = sender or self._post
        self.failures = 0

    def _post(self, payload: dict) -> None:
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=2) as r:
            r.read()

    def emit(self, event: str) -> bool:
        payload = {"event": event, "device_id": self.device_id, "ts": time.time()}
        try:
            self.sender(payload)
            return True
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            self.failures += 1
            log.warning("event %s not delivered: %s", event, exc)
            return False

    def on_motion(self) -> bool:
        now = self.clock()
        if self._last_motion is not None and now - self._last_motion < self.cooldown_s:
            return False                       # suppress wake loop
        self._last_motion = now
        return self.emit("visitor_approached")

    def on_home(self) -> bool:
        return self.emit("home_pressed")


def main() -> None:  # pragma: no cover - needs hardware or mock factory
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from gpiozero import Button, MotionSensor, LED
    from signal import pause
    b = Bridge(os.environ.get("KIOSK_EVENT_URL", "http://127.0.0.1:8765/device/event"),
               os.environ.get("KIOSK_DEVICE_ID", "DEMO-KIOSK-01"),
               float(os.environ.get("KIOSK_PIR_COOLDOWN_S", "10")))
    home = Button(int(os.environ.get("KIOSK_HOME_PIN", "27")), pull_up=True, bounce_time=0.15)
    pir = MotionSensor(int(os.environ.get("KIOSK_PIR_PIN", "17")))
    led_pin = os.environ.get("KIOSK_LED_PIN", "22")
    led = LED(int(led_pin)) if led_pin else None
    home.when_pressed = b.on_home
    pir.when_motion = b.on_motion
    if led:
        led.on()
    log.info("GPIO bridge running -> %s", b.url)
    pause()


if __name__ == "__main__":
    main()
