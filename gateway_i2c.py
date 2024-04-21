import time
import smbus
import argparse
import statistics

from BNO055 import BNO055

argparser = argparse.ArgumentParser(description="I2C Logger")
argparser.add_argument("--calibrationData", help="22 bytes (comma-separated)")
args = argparser.parse_args()
calibrationData = list(map(int, args.calibrationData.split(","))) if args.calibrationData != None else None

bus = smbus.SMBus(1)
imu = BNO055(bus, calibrationData=calibrationData)

try:    
    while True:
        vals = list()
        for i in range(10):
            vals.append(imu.readHeadingDegrees())
            time.sleep(0.01)
        
        median = statistics.median(vals)
        print(median, flush=True)
except KeyboardInterrupt:
    pass