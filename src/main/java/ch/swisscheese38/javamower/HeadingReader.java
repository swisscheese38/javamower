package ch.swisscheese38.javamower;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class HeadingReader implements Heading {

    private static final String CALIBRATION_DATA = "233,255,224,255,225,255,167,1,181,1,133,1,255,255,254,255,255,255,232,3,90,2";

    private final Logger logger = LoggerFactory.getLogger(HeadingReader.class);

    private ExecutorService executorService;
    private Process process;
    private boolean stopRequested;

    private float heading;

    public HeadingReader start() {
        stopRequested = false;
        executorService = Executors.newSingleThreadExecutor();
        executorService.execute(new HeadingReaderRunnable());
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
    public float getHeading() {
        return heading;
    }

    private class HeadingReaderRunnable implements Runnable {

        @Override
        public void run() {
            try {
                process = new ProcessBuilder("python3", "gateway_i2c.py", "--calibrationData", CALIBRATION_DATA).start();
                final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                while (process.isAlive() && !stopRequested) {
                    final String line = bufferedReader.readLine();
                    if (line == null) {
                        logger.warn("Got null data over I2C");
                        continue;
                    }
                    final String[] headingString = line.split("\t");
                    if (headingString.length == 1) {
                        heading = Float.parseFloat(headingString[0]);
                    } else {
                        logger.warn("Got unexpected data over I2C: " + line);
                    }
                }
                process.destroy();
            } catch (Exception e) {
                logger.warn("Couldn't get Heading", e);;
            }
        }
    }
}
