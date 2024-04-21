from serial import Serial
from pyubx2 import UBXReader

serialstream = Serial('/dev/ttyAMA0', 115200, timeout=3)
ubxreader = UBXReader(datastream=serialstream, protfilter=2)

try:
    for (raw_data, msg) in ubxreader:
        if 'NAV-PVT' == msg.identity:
            print(f'{msg.lat}\t{msg.lon}\t{msg.hAcc}', flush=True)
except KeyboardInterrupt:
    pass