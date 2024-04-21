package ch.swisscheese38.javamower;

public class Main {

    public static void main(String[] args) throws Exception {

        final GpsReader gpsReader = new GpsReader().start();
        final HeadingReader headingReader = new HeadingReader().start();
        final ArduinoController arduinoController = new ArduinoController().start();

        final NavigationController navigationController = 
            new NavigationController(gpsReader, headingReader, arduinoController)
            .setDestination(47.01253, 7.56895)
            .start();
        
        // do some navigation for a little while
        Thread.sleep(5_000);
        
        gpsReader.stop();
        headingReader.stop();
        arduinoController.stop();
        navigationController.stop();
    }
}
