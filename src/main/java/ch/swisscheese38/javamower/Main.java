package ch.swisscheese38.javamower;

public class Main {

    public static void main(String[] args) throws Exception {
        final GpsReader gpsReader = new GpsReader();
        final HeadingReader headingReader = new HeadingReader();
        System.out.println("starting readers");
        gpsReader.start();
        headingReader.start();
        for (int i = 0; i < 10; i++) {
            System.out.println(gpsReader.getAccuracyMm());
            System.out.println(headingReader.getHeading());
            Thread.sleep(100);
        }
        System.out.println("stopping readers");
        gpsReader.stop();
        headingReader.stop();
    }
}
