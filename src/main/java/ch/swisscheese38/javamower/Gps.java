package ch.swisscheese38.javamower;

public interface Gps {

    double getLatitude();

    double getLongitude();

    int getAccuracyMm();

    FixType getFixType();

    public enum FixType {
        NO_FIX,
        DEAD_RECKONING,
        FIX_2D,
        FIX_3D,
        RTK_FIX,
        RTK_FLOAT
    }

}
