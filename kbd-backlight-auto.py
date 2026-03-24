#!/usr/bin/env python3
# kbd-backlight-auto.py

import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)

# --- CONFIG ---
ALS_RAW_PATH    = "/sys/bus/iio/devices/iio:device0/in_illuminance_raw"
ALS_SCALE_PATH  = "/sys/bus/iio/devices/iio:device0/in_illuminance_scale"
ALS_OFFSET_PATH = "/sys/bus/iio/devices/iio:device0/in_illuminance_offset"
KBD_PATH        = "/sys/class/leds/asus::kbd_backlight/brightness"
SAMPLE_INTERVAL = 5    # seconds
HYSTERESIS      = 30   # lux — dead band around each threshold

# Thresholds in lux -> keyboard level
# Hysteresis creates a band [threshold-HYSTERESIS, threshold+HYSTERESIS]
# in which the level does NOT change until clearly exiting the band
THRESHOLDS = [
    (50,   3),
    (200,  2),
    (600,  1),
    (float('inf'), 0),
]

def read_float(path):
    with open(path) as f:
        return float(f.read().strip())

def get_lux():
    raw    = read_float(ALS_RAW_PATH)
    scale  = read_float(ALS_SCALE_PATH)
    offset = read_float(ALS_OFFSET_PATH)
    return (raw + offset) * scale

def get_kbd_level_no_hysteresis(lux):
    """'Pure' level without hysteresis — used as reference."""
    for threshold, level in THRESHOLDS:
        if lux < threshold:
            return level
    return 0

def get_kbd_level_with_hysteresis(lux, current_level):
    """
    Changes level only if the new 'pure' level is stable,
    i.e. if lux is clearly outside the hysteresis band
    around the threshold that separates current_level from the adjacent level.
    """
    new_level = get_kbd_level_no_hysteresis(lux)

    if new_level == current_level:
        return current_level  # no change needed

    # Find the threshold that separates current_level and new_level
    # (the first threshold we cross going up or down)
    boundary = None
    for threshold, level in THRESHOLDS:
        if level == min(current_level, new_level):
            boundary = threshold
            break

    if boundary is None or boundary == float('inf'):
        return new_level  # no finite threshold between the two levels, change immediately

    # Apply hysteresis: change only if we are outside the dead band
    if new_level < current_level:
        # lux is decreasing (darker → more backlight)
        # change only if lux < threshold - hysteresis
        if lux < boundary - HYSTERESIS:
            return new_level
    else:
        # lux is increasing (brighter → less backlight)
        # change only if lux > threshold + hysteresis
        if lux > boundary + HYSTERESIS:
            return new_level

    return current_level  # we are in the dead band, don't change

def set_kbd_brightness(level):
    with open(KBD_PATH, "w") as f:
        f.write(str(level))

if __name__ == "__main__":
    current_level = -1

    # Initialization: read the current keyboard level
    try:
        current_level = int(read_float(KBD_PATH))
        logging.info(f"Current keyboard level at startup: {current_level}")
    except Exception:
        current_level = get_kbd_level_no_hysteresis(get_lux())

    while True:
        try:
            lux = get_lux()
            new_level = get_kbd_level_with_hysteresis(lux, current_level)

            if new_level != current_level:
                logging.info(f"Lux: {lux:.1f} → level: {current_level} → {new_level}")
                set_kbd_brightness(new_level)
                current_level = new_level
            else:
                logging.debug(f"Lux: {lux:.1f} → level unchanged: {current_level}")

        except Exception as e:
            logging.error(f"Error: {e}")

        time.sleep(SAMPLE_INTERVAL)
