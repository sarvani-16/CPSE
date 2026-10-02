package com.sih.material;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * SIH26099: Enterprise Spring Boot Backend
 * AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
 */
@SpringBootApplication
@EnableAsync
public class MaterialApplication {

    public static void main(String[] args) {
        SpringApplication.run(MaterialApplication.class, args);
    }
}
