package com.example.sampleapp.controller;

import lombok.AllArgsConstructor;
import lombok.Data;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.IntStream;

@RestController
@RequestMapping("/WeatherForecast")
public class WeatherForecastController {

    private static final String[] SUMMARIES = new String[] {
            "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
    };

    @GetMapping
    public List<WeatherForecast> get() {
        return IntStream.rangeClosed(1, 5).mapToObj(index -> new WeatherForecast(
                LocalDate.now().plusDays(index),
                ThreadLocalRandom.current().nextInt(-20, 55),
                SUMMARIES[ThreadLocalRandom.current().nextInt(SUMMARIES.length)])).toList();
    }

    @Data
    @AllArgsConstructor
    public static class WeatherForecast {
        private LocalDate date;
        private int temperatureC;
        private String summary;

        public int getTemperatureF() {
            return 32 + (int) (temperatureC / 0.5556);
        }
    }
}