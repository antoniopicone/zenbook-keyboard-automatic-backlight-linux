# Automatic Keyboard Backlight - for Asus Zenbook laptop

This process runs a Python script that monitors the ALS sensor for ambient brightness and, based on it, automatically turns the integrated keyboard backlight of the Asus Zenbook laptop on/off.

## Installation

```bash
sudo cp kbd-backlight-auto.py /usr/local/bin/ 
mkdir -p ~/.config/systemd/user/
cp kbd-backlight-auto.service ~/.config/systemd/user/kbd-backlight-auto.service

# Start service
systemctl --user daemon-reload
systemctl --user enable kbd-backlight-auto.service --now
```

