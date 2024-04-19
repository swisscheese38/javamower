package ch.swisscheese38.javamower;

import java.nio.charset.StandardCharsets;
import java.util.stream.Stream;

import com.fazecast.jSerialComm.SerialPort;
import com.fazecast.jSerialComm.SerialPortDataListener;
import com.fazecast.jSerialComm.SerialPortEvent;

public class ArduinoController {

    private static final int VENDOR_ID = 0x1A86;
    private static final int PRODUCT_ID = 0x7523;
    
    private SerialPort serialPort;
    
    private float leftVelocity;
    private float rightVelocity;

    public float getRightVelocity() {
        return rightVelocity;
    }

    public float getLeftVelocity() {
        return leftVelocity;
    }

    public void start() {
        serialPort = Stream.of(SerialPort.getCommPorts())
            .filter(sp -> VENDOR_ID == sp.getVendorID())
            .filter(sp -> PRODUCT_ID == sp.getProductID())
            .findFirst()
            .orElseThrow();
        serialPort.openPort();
        serialPort.addDataListener(new ArduinoDataListener());
    }

    public void stop() {
        serialPort.removeDataListener();
        serialPort.closePort();
    }

    private class ArduinoDataListener implements SerialPortDataListener {

        @Override
        public int getListeningEvents() {
            return SerialPort.LISTENING_EVENT_DATA_RECEIVED;
        }

        @Override
        public void serialEvent(final SerialPortEvent event) {
            final String string = new String(event.getReceivedData(), StandardCharsets.UTF_8);
            final String[] splittedString = string.split(" ");
            if (splittedString.length == 2) {
                leftVelocity = Float.parseFloat(splittedString[0]);
                rightVelocity = Float.parseFloat(splittedString[1]);
            }
        }
    }
}
