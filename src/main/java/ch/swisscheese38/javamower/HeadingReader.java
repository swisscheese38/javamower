package ch.swisscheese38.javamower;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class HeadingReader {

    private final Logger logger = LoggerFactory.getLogger(HeadingReader.class);

    private ExecutorService executorService;
    private Process process;
    private boolean stopRequested;

    private float heading;

    public void start() {
        stopRequested = false;
        executorService = Executors.newSingleThreadExecutor();
        executorService.execute(new HeadingReaderRunnable());
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

    public float getHeading() {
        return heading;
    }

    private class HeadingReaderRunnable implements Runnable {

        @Override
        public void run() {
            try {
                process = new ProcessBuilder(
                    "python3", "i2clogger.py",
                    "--calibrationData", "233,255,224,255,225,255,167,1,181,1,133,1,255,255,254,255,255,255,232,3,90,2"
                    ).start();
                final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                while (process.isAlive() && !stopRequested) {
                    final String line = bufferedReader.readLine();
                    if (line != null) {
                        final String[] headingString = line.split("\t");
                        if (headingString.length == 1) {
                            heading = Float.parseFloat(headingString[0]);
                        }
                    }
                }
                process.destroy();
            } catch (Exception e) {
                logger.warn("Couldn't get Heading", e);;
            }
        }
    }
}
