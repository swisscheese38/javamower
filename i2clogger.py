import time
import smbus

from BNO055 import BNO055

bus = smbus.SMBus(1)
imu = BNO055(bus)

while True:
    imu.readEul()
    print(imu.euler['x'], flush=True)
    time.sleep(0.1)