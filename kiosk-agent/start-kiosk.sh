#!/usr/bin/env bash
# Launch the kiosk UI full screen and relaunch it if it exits. Started from the desktop autostart entry.
# The UI is served locally by local_event_service.py (KIOSK_UI_DIR) — never a cloud URL.
set -u
URL="${KIOSK_UI_URL:-http://127.0.0.1:8765/}"
BROWSER=$(command -v chromium-browser || command -v chromium)
if [ -z "$BROWSER" ]; then echo "chromium not found" >&2; exit 1; fi
until curl -fs -o /dev/null "$URL"; do sleep 1; done     # wait for the local UI server
while true; do
  "$BROWSER" --kiosk --noerrdialogs --disable-infobars --no-first-run \
             --disable-session-crashed-bubble --overscroll-history-navigation=0 \
             --check-for-update-interval=31536000 "$URL"
  sleep 2
done
