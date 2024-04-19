package ch.swisscheese38.javamower;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class GpsReader {

    private final Logger logger = LoggerFactory.getLogger(GpsReader.class);

    private ExecutorService executorService;

    private boolean stopRequested;

    private float latitude;
    private float longitude;
    private int accuracyMm;
    public Process process;

    public void start() {
        stopRequested = false;
        executorService = Executors.newSingleThreadExecutor();
        executorService.execute(new GpsReaderRunnable());
    }

    public void stop() {
        stopRequested = true;
        executorService.shutdown();
        try {
            executorService.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            logger.error("Couldn't stop", e);
        }
    }

    public float getLatitude() {
        return latitude;
    }

    public float getLongitude() {
        return longitude;
    }

    public int getAccuracyMm() {
        return accuracyMm;
    }

    private class GpsReaderRunnable implements Runnable {

        @Override
        public void run() {
            try {
                process = new ProcessBuilder("python3", "gpslogger.py").start();
                final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                while (process.isAlive() && !stopRequested) {
                    final String line = bufferedReader.readLine();
                    if (line != null) {
                        final String[] positionString = line.split("\t");
                        if (positionString.length == 3) {
                            latitude = Float.parseFloat(positionString[0]);
                            longitude = Float.parseFloat(positionString[1]);
                            accuracyMm = Integer.parseInt(positionString[2]);
                        }
                    }
                }
                process.destroy();
            } catch (Exception e) {
                logger.warn("Couldn't get GPS Position", e);;
            }
        }
    }
}