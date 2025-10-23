#!/bin/bash
xset s off
xset s noblank
xset -dpms

sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences

chromium --noerrdialogs --disable-infobars --kiosk --force-device-scale-factor=0.6 \
  --overscroll-history-navigation=0 \
  --disable-pinch \
  'https://izzymart.app'