package com.sih.material.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI 3.0 / Swagger UI Configuration for Spring Boot.
 */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI sihOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("SIH26099: CPSE Material Standardization & Harmonization API")
                        .description("Central Spring Boot Enterprise API Gateway orchestrating CPSE Ingestion, Human-in-the-Loop Reviews, National Material Master Codification, and FastAPI ML Service.")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Smart India Hackathon 2024 Team")
                                .email("procurement-harmonization@cpse.gov.in"))
                        .license(new License().name("Apache 2.0").url("https://spring.io")));
    }
}
