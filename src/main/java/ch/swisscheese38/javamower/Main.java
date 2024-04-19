package ch.swisscheese38.javamower;

public class Main {

    public static void main(String[] args) throws Exception {
        final GpsReader gpsReader = new GpsReader();
        final HeadingReader headingReader = new HeadingReader();
        final ArduinoController arduinoController = new ArduinoController();
        
        System.out.println("starting readers/controllers");
        gpsReader.start();
        headingReader.start();
        arduinoController.start();
        for (int i = 0; i < 10; i++) {
            System.out.println("GPS Accuracy: " + gpsReader.getAccuracyMm());
            System.out.println("IMU Heading: " + headingReader.getHeading());
            System.out.println("Left wheel velocity: " + arduinoController.getLeftVelocity());
            Thread.sleep(100);
        }
        
        System.out.println("stopping readers/controllers");
        gpsReader.stop();
        headingReader.stop();
        arduinoController.stop();
    }
}
