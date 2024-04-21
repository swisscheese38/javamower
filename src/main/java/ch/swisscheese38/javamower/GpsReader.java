package ch.swisscheese38.javamower;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ch.swisscheese38.Gps;


public class GpsReader implements Gps {

    private final Logger logger = LoggerFactory.getLogger(GpsReader.class);

    private ExecutorService executorService;
    private Process process;
    private boolean stopRequested;

    private float latitude;
    private float longitude;
    private int accuracyMm;

    public GpsReader start() {
        stopRequested = false;
        executorService = Executors.newSingleThreadExecutor();
        executorService.execute(new GpsReaderRunnable());
        return this;
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

    @Override
    public double getLatitude() {
        return latitude;
    }

    @Override
    public double getLongitude() {
        return longitude;
    }

    @Override
    public int getAccuracyMm() {
        return accuracyMm;
    }

    private class GpsReaderRunnable implements Runnable {

        @Override
        public void run() {
            try {
                process = new ProcessBuilder("python3", "gateway_gps.py").start();
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
