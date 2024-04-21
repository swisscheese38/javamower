package ch.swisscheese38.javamower;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.geotools.referencing.GeodeticCalculator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ch.swisscheese38.Gps;

public class NavigationController {
    
    private final Logger logger = LoggerFactory.getLogger(NavigationController.class);

    private final GeodeticCalculator geodeticCalculator = new GeodeticCalculator();

    private final Gps gps;
    private final Heading heading;
    private final Motor motor;

    private double latitude;
    private double longitude;

    private ScheduledExecutorService executorService;

    public NavigationController(Gps gps, Heading heading, Motor motor) {
        this.gps = gps;
        this.heading = heading;
        this.motor = motor;
    }

    public NavigationController start() {
        executorService = Executors.newScheduledThreadPool(1);
        executorService.scheduleAtFixedRate(new NavigationControllerRunnable(), 0L, 100L, TimeUnit.MILLISECONDS);
        return this;
    }

    public void stop() {
        executorService.shutdown();
        try {
            executorService.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            logger.error("Couldn't stop", e);
        }
    }
    
    public NavigationController setDestination(double latitude, double longitude) {
        this.latitude = latitude;
        this.longitude = longitude;
        return this;
    }

    private class NavigationControllerRunnable implements Runnable {

        @Override
        public void run() {
            try {    
                geodeticCalculator.setStartingGeographicPoint(gps.getLongitude(), gps.getLatitude());
                geodeticCalculator.setDestinationGeographicPoint(longitude, latitude);
                System.out.println("Turn from %s to %s and drive for %s meters".formatted(
                    heading.getHeading(),
                    geodeticCalculator.getAzimuth(),
                    geodeticCalculator.getOrthodromicDistance()
                ));
            } catch (Exception e) {
                logger.warn("Couldn't navigate", e);;
            }
        }

    }
}
