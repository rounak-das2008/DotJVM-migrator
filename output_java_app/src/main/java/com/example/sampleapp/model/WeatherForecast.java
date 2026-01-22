package com.example.sampleapp.model;

import java.time.LocalDate;
import lombok.Data;

/**
 * Represents a weather forecast.
 */
@Data
public class WeatherForecast {

    private LocalDate date;

    private int temperatureC;

    private String summary;

    /**
     * Calculates and returns the temperature in Fahrenheit.
     * This is a computed property based on temperatureC.
     *
     * @return The temperature in Fahrenheit.
     */
    public int getTemperatureF() {
        return 32 + (int) (temperatureC / 0.5556);
    }
}