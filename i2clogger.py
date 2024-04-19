import time
import smbus
import argparse

from BNO055 import BNO055

argparser = argparse.ArgumentParser(description="I2C Logger")
argparser.add_argument("--calibrationData", help="22 bytes (comma-separated)")
args = argparser.parse_args()
calibrationData = list(map(int, args.calibrationData.split(","))) if args.calibrationData != None else None

bus = smbus.SMBus(1)
imu = BNO055(bus, calibrationData=calibrationData)

while True:
    imu.readEul()
    print(imu.euler['x'], flush=True)
    time.sleep(0.1)