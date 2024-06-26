import time
import ctypes

def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)

def twos_complement(input_value, num_bits):
    mask = 2**(num_bits - 1)
    return -(input_value & mask) + (input_value & ~mask)

class BNO055:

    """
    BNO055
    IMU 9DOF Sensor Fusion
    """

    def __init__(self, bus, address = 0x28, calibrationData = None):
        self.bus = bus
        self.address = address

        #  Select BNO055 config mode (requires 19ms, see table 3-6)
        self.writeByte(self.BNO055_OPR_MODE, self.OPRMode.CONFIGMODE )
        time.sleep(0.025)

        #  Select BNO055 sensor units
        # Linear acceleration units 0x00000000 METERS_PER_SECOND
        # Anguar velocity units     0x00000010 RAD_PER_SECOND
        # Euler orientation units   0x00000100 RAD
        # Temperature units         0x00000000 CELSIUS
        # Orientation mode          0x00000000 WINDOWS_ORIENTATION
        self.writeByte(self.BNO055_UNIT_SEL, 0x00000110 )

        #  Write calibrationData if known
        if calibrationData != None and len(calibrationData) == 22:
            self.writeBytes(self.BNO055_ACC_OFFSET_X_LSB, calibrationData)
        
        #  Select BNO055 system operation mode (requires 7ms, see table 3-6)
        self.writeByte(self.BNO055_OPR_MODE, self.OPRMode.NDOF )
        time.sleep(0.025)

    def readData(self, subAddress):
        rawData = self.readBytes(subAddress, 6)
        intX = (rawData[1] << 8) | rawData[0]
        intY = (rawData[3] << 8) | rawData[2]
        intZ = (rawData[5] << 8) | rawData[4]
        x = twos_complement(intX, 16)
        y = twos_complement(intY, 16)
        z = twos_complement(intZ, 16)
        return (x, y, z)

    def readSingleData(self, subAddress):
        rawData = self.readBytes(subAddress, 2)
        intV = (rawData[1] << 8) | rawData[0]
        v = twos_complement(intV, 16)
        return v

    def readHeadingDegrees(self):
        return self.readSingleData(self.BNO055_EUL_HEADING_LSB)/16.0

    def readEul(self, degrees = 0):
        x, y, z = self.readData(self.BNO055_EUL_HEADING_LSB)
        if degrees == 0:
            unit = 16.0
        else:   # radians
            unit = 900.0
        self.euler = {'x': x/unit, 'y': y/unit, 'z': z/unit}
        
    def readQuat(self):
        rawData = self.readBytes(self.BNO055_QUA_DATA_W_LSB, 8)
        intQW = (rawData[1] << 8) | rawData[0]
        intQX = (rawData[3] << 8) | rawData[2]
        intQY = (rawData[5] << 8) | rawData[4]
        intQZ = (rawData[7] << 8) | rawData[6]
        qw = twos_complement(intQW, 16)/16384.   # 2E14
        qx = twos_complement(intQX, 16)/16384.
        qy = twos_complement(intQY, 16)/16384.
        qz = twos_complement(intQZ, 16)/16384.
        # No conversion needed
        self.quat = {'qw': qw, 'qx': qx, 'qy': qy, 'qz': qz}

    def readGyro(self):
        x, y, z = self.readData(self.BNO055_GYR_DATA_X_LSB)
        # Convert values to an appropriate range (section 3.6.4)
        unit = 900.0 #ANGULAR_RAD_SCALE 1 rad/s = 900 LSB
        self.gyro = {'x': x/unit, 'y': y/unit, 'z': z/unit}

    def readLinAccel(self):
        x, y, z = self.readData(self.BNO055_LIA_DATA_X_LSB)
        # Convert values to an appropriate range (section 3.6.4)
        unit = 100.0 # LINEAR_SCALE 1 m/s2 = 100 LSB
        self.linAccel = {'x': x/unit, 'y': y/unit, 'z': z/unit}

    def readCalib(self):
        stat = self.readBytes(self.BNO055_CALIB_STAT, 1)
        sys  = ( stat[0] & 0b11000000 ) >> 6    # Take first 2 bits and move them to the end
        gyro = ( stat[0] & 0b00110000 ) >> 4
        acc  = ( stat[0] & 0b00001100 ) >> 2
        mag  = ( stat[0] & 0b00000011 ) >> 0
        # Calibration status, from 0 (not calibrated) t0 3 (fully calibrated)
        self.status = {'sys': sys, 'gyro': gyro, 'acc': acc, 'mag':mag}

    def readCalibOffsets(self):
        accX, accY, accZ = self.readData(self.BNO055_ACC_OFFSET_X_LSB)
        magX, magY, magZ = self.readData(self.BNO055_MAG_OFFSET_X_LSB)
        gyrX, gyrY, gyrZ = self.readData(self.BNO055_GYR_OFFSET_X_LSB)
        accR = self.readSingleData(self.BNO055_ACC_RADIUS_LSB)
        magR = self.readSingleData(self.BNO055_MAG_RADIUS_LSB)
        return {'accX': accX, 'accY': accY, 'accZ': accZ,
                'magX': magX, 'magY': magY, 'magZ': magZ,
                'gyrX': gyrX, 'gyrY': gyrY, 'gyrZ': gyrZ,
                'accR': accR, 'magR': magR}

    def readCalibrationBytes(self):
        return self.readBytes(self.BNO055_ACC_OFFSET_X_LSB, 22)

    def selfTest(self):
        result = self.readBytes(self.BNO055_ST_RESULT, 1)
        mcu  = ( result[0] & 0b00001000 ) >> 3
        gyro = ( result[0] & 0b00000100 ) >> 2
        mag  = ( result[0] & 0b00000010 ) >> 1
        acc  = ( result[0] & 0b00000001 ) >> 0
        # Sensor is working if bit is set to 1
        self.result = {'mcu': mcu, 'gyro': gyro, 'acc': acc, 'mag':mag}

    def writeByte(self, subAddress, value):
        self.bus.write_byte_data(self.address, subAddress, value)

    def readBytes(self, subAddress, count):
        return self.bus.read_i2c_block_data(self.address, subAddress, count)

    def writeBytes(self, subAddress, data):
        self.bus.write_i2c_block_data(self.address, subAddress, data)

    #  BNO055 Register Map
    #  Datasheet: https:# www.bosch-sensortec.com/en/homepage/products_3/sensor_hubs/iot_solutions/bno055_1/bno055_4
    #  BNO055 Page 0
    BNO055_CHIP_ID          = 0x00    #  should be 0xA0
    BNO055_ACC_ID           = 0x01    #  should be 0xFB
    BNO055_MAG_ID           = 0x02    #  should be 0x32
    BNO055_GYRO_ID          = 0x03    #  should be 0x0F
    BNO055_SW_REV_ID_LSB    = 0x04
    BNO055_SW_REV_ID_MSB    = 0x05
    BNO055_BL_REV_ID        = 0x06
    BNO055_PAGE_ID          = 0x07
    BNO055_ACC_DATA_X_LSB   = 0x08
    BNO055_ACC_DATA_X_MSB   = 0x09
    BNO055_ACC_DATA_Y_LSB   = 0x0A
    BNO055_ACC_DATA_Y_MSB   = 0x0B
    BNO055_ACC_DATA_Z_LSB   = 0x0C
    BNO055_ACC_DATA_Z_MSB   = 0x0D
    BNO055_MAG_DATA_X_LSB   = 0x0E
    BNO055_MAG_DATA_X_MSB   = 0x0F
    BNO055_MAG_DATA_Y_LSB   = 0x10
    BNO055_MAG_DATA_Y_MSB   = 0x11
    BNO055_MAG_DATA_Z_LSB   = 0x12
    BNO055_MAG_DATA_Z_MSB   = 0x13
    BNO055_GYR_DATA_X_LSB   = 0x14
    BNO055_GYR_DATA_X_MSB   = 0x15
    BNO055_GYR_DATA_Y_LSB   = 0x16
    BNO055_GYR_DATA_Y_MSB   = 0x17
    BNO055_GYR_DATA_Z_LSB   = 0x18
    BNO055_GYR_DATA_Z_MSB   = 0x19
    BNO055_EUL_HEADING_LSB  = 0x1A
    BNO055_EUL_HEADING_MSB  = 0x1B
    BNO055_EUL_ROLL_LSB     = 0x1C
    BNO055_EUL_ROLL_MSB     = 0x1D
    BNO055_EUL_PITCH_LSB    = 0x1E
    BNO055_EUL_PITCH_MSB    = 0x1F
    BNO055_QUA_DATA_W_LSB   = 0x20
    BNO055_QUA_DATA_W_MSB   = 0x21
    BNO055_QUA_DATA_X_LSB   = 0x22
    BNO055_QUA_DATA_X_MSB   = 0x23
    BNO055_QUA_DATA_Y_LSB   = 0x24
    BNO055_QUA_DATA_Y_MSB   = 0x25
    BNO055_QUA_DATA_Z_LSB   = 0x26
    BNO055_QUA_DATA_Z_MSB   = 0x27
    BNO055_LIA_DATA_X_LSB   = 0x28
    BNO055_LIA_DATA_X_MSB   = 0x29
    BNO055_LIA_DATA_Y_LSB   = 0x2A
    BNO055_LIA_DATA_Y_MSB   = 0x2B
    BNO055_LIA_DATA_Z_LSB   = 0x2C
    BNO055_LIA_DATA_Z_MSB   = 0x2D
    BNO055_GRV_DATA_X_LSB   = 0x2E
    BNO055_GRV_DATA_X_MSB   = 0x2F
    BNO055_GRV_DATA_Y_LSB   = 0x30
    BNO055_GRV_DATA_Y_MSB   = 0x31
    BNO055_GRV_DATA_Z_LSB   = 0x32
    BNO055_GRV_DATA_Z_MSB   = 0x33
    BNO055_TEMP             = 0x34
    BNO055_CALIB_STAT       = 0x35
    BNO055_ST_RESULT        = 0x36
    BNO055_INT_STATUS       = 0x37
    BNO055_SYS_CLK_STATUS   = 0x38
    BNO055_SYS_STATUS       = 0x39
    BNO055_SYS_ERR          = 0x3A
    BNO055_UNIT_SEL         = 0x3B
    BNO055_OPR_MODE         = 0x3D
    BNO055_PWR_MODE         = 0x3E
    BNO055_SYS_TRIGGER      = 0x3F
    BNO055_TEMP_SOURCE      = 0x40
    BNO055_AXIS_MAP_CONFIG  = 0x41
    BNO055_AXIS_MAP_SIGN    = 0x42
    BNO055_ACC_OFFSET_X_LSB = 0x55
    BNO055_ACC_OFFSET_X_MSB = 0x56
    BNO055_ACC_OFFSET_Y_LSB = 0x57
    BNO055_ACC_OFFSET_Y_MSB = 0x58
    BNO055_ACC_OFFSET_Z_LSB = 0x59
    BNO055_ACC_OFFSET_Z_MSB = 0x5A
    BNO055_MAG_OFFSET_X_LSB = 0x5B
    BNO055_MAG_OFFSET_X_MSB = 0x5C
    BNO055_MAG_OFFSET_Y_LSB = 0x5D
    BNO055_MAG_OFFSET_Y_MSB = 0x5E
    BNO055_MAG_OFFSET_Z_LSB = 0x5F
    BNO055_MAG_OFFSET_Z_MSB = 0x60
    BNO055_GYR_OFFSET_X_LSB = 0x61
    BNO055_GYR_OFFSET_X_MSB = 0x62
    BNO055_GYR_OFFSET_Y_LSB = 0x63
    BNO055_GYR_OFFSET_Y_MSB = 0x64
    BNO055_GYR_OFFSET_Z_LSB = 0x65
    BNO055_GYR_OFFSET_Z_MSB = 0x66
    BNO055_ACC_RADIUS_LSB   = 0x67
    BNO055_ACC_RADIUS_MSB   = 0x68
    BNO055_MAG_RADIUS_LSB   = 0x69
    BNO055_MAG_RADIUS_MSB   = 0x6A
    #  BNO055 Page 1
    BNO055_PAGE_ID          = 0x07
    BNO055_ACC_CONFIG       = 0x08
    BNO055_MAG_CONFIG       = 0x09
    BNO055_GYRO_CONFIG_0    = 0x0A
    BNO055_GYRO_CONFIG_1    = 0x0B
    BNO055_ACC_SLEEP_CONFIG = 0x0C
    BNO055_GYR_SLEEP_CONFIG = 0x0D
    BNO055_INT_MSK          = 0x0F
    BNO055_INT_EN           = 0x10
    BNO055_ACC_AM_THRES     = 0x11
    BNO055_ACC_INT_SETTINGS = 0x12
    BNO055_ACC_HG_DURATION  = 0x13
    BNO055_ACC_HG_THRESH    = 0x14
    BNO055_ACC_NM_THRESH    = 0x15
    BNO055_ACC_NM_SET       = 0x16
    BNO055_GYR_INT_SETTINGS = 0x17
    BNO055_GYR_HR_X_SET     = 0x18
    BNO055_GYR_DUR_X        = 0x19
    BNO055_GYR_HR_Y_SET     = 0x1A
    BNO055_GYR_DUR_Y        = 0x1B
    BNO055_GYR_HR_Z_SET     = 0x1C
    BNO055_GYR_DUR_Z        = 0x1D
    BNO055_GYR_AM_THRESH    = 0x1E
    BNO055_GYR_AM_SET       = 0x1F

    #  Set initial input parameters
    #  ACC Full Scale
    Ascale = enum('AFS_2G', 'AFS_4G', 'AFS_8G', 'AFS_18G')
    #  ACC Bandwidth
    Abw = enum('ABW_7_81Hz', 'ABW_15_63Hz', 'ABW_31_25Hz', 'ABW_62_5Hz', 'ABW_125Hz', 'ABW_250Hz', 'ABW_500Hz', 'ABW_1000Hz')
    #  ACC Pwr Mode
    APwrMode = enum('NormalA', 'SuspendA', 'LowPower1A', 'StandbyA', 'LowPower2A', 'DeepSuspendA')
    #  Gyro full scale
    Gscale = enum('GFS_2000DPS', 'GFS_1000DPS', 'GFS_500DPS', 'GFS_250DPS', 'GFS_125DPS')
    #  GYR Pwr Mode
    GPwrMode = enum('NormalG', 'FastPowerUpG', 'DeepSuspendedG', 'SuspendG', 'AdvancedPowerSaveG')
    #  Gyro bandwidth
    Gbw = enum('GBW_523Hz', 'GBW_230Hz', 'GBW_116Hz', 'GBW_47Hz', 'GBW_23Hz', 'GBW_12Hz', 'GBW_64Hz', 'GBW_32Hz')
    #  BNO-55 operation modes
    OPRMode = enum('CONFIGMODE', 'ACCONLY', 'MAGONLY', 'GYROONLY', 'ACCMAG', 'ACCGYRO', 'MAGGYRO', 'AMG', 'IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF')
    # OPRMode ={'CONFIGMODE': 0x00, 'ACCONLY': 0x01, 'MAGONLY': 0x02, 'GYROONLY': 0x03, 'ACCMAG': 0x04, 'ACCGYRO': 0x05, 'MAGGYRO': 0x06, 'AMG': 0x07, 'IMU': 0x08, 'COMPASS': 0x09, 'M4G': 0x0A, 'NDOF_FMC_OFF': 0x0B, 'NDOF': 0x0C}
    #  Power mode
    PWRMode = enum('Normalpwr', 'Lowpower', 'Suspendpwr')
    #  Magnetometer output data rate
    Modr = enum('MODR_2Hz', 'MODR_6Hz', 'MODR_8Hz', 'MODR_10Hz', 'MODR_15Hz', 'MODR_20Hz', 'MODR_25Hz', 'MODR_30Hz')
    #  MAG Op Mode
    MOpMode = enum('LowPower', 'Regular', 'EnhancedRegular', 'HighAccuracy')
    #  MAG power mod
    MPwrMode = enum('Normal', 'Sleep', 'Suspend', 'ForceMode')
    Posr = enum('P_OSR_00', 'P_OSR_01', 'P_OSR_02', 'P_OSR_04', 'P_OSR_08', 'P_OSR_16')
    Tosr = enum('T_OSR_00', 'T_OSR_01', 'T_OSR_02', 'T_OSR_04', 'T_OSR_08', 'T_OSR_16')
    #  bandwidth at full to 0.021 x sample rate
    IIRFilter = enum('full', 'BW0_223ODR', 'BW0_092ODR', 'BW0_042ODR', 'BW0_021ODR')
    Mode = enum('BMP280Sleep', 'forced', 'forced2', 'normal')
    SBy = enum('t_00_5ms', 't_62_5ms', 't_125ms', 't_250ms', 't_500ms', 't_1000ms', 't_2000ms', 't_4000ms',)