raw   = float(open('/sys/bus/iio/devices/iio:device0/in_illuminance_raw').read())
scale = float(open('/sys/bus/iio/devices/iio:device0/in_illuminance_scale').read())
off   = float(open('/sys/bus/iio/devices/iio:device0/in_illuminance_offset').read())
print(f'raw={raw}, lux={(raw+off)*scale:.1f}')
