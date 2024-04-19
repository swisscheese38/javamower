package ch.swisscheese38.javamower;

public class Main {

    public static void main(String[] args) throws Exception {
        GpsReader gpsReader = new GpsReader();
        System.out.println("starting gps reader");
        gpsReader.start();
        for (int i = 0; i < 10; i++) {
            System.out.println(gpsReader.getAccuracyMm());
            Thread.sleep(100);
        }
        gpsReader.stop();
        System.out.println("restarting gps reader");
        gpsReader.start();
        for (int i = 0; i < 10; i++) {
            System.out.println(gpsReader.getAccuracyMm());
            Thread.sleep(100);
        }
        System.out.println("stopping gps reader");
        gpsReader.stop();
    }

}
