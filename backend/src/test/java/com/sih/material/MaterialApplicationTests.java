package com.sih.material;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("h2")
class MaterialApplicationTests {

    @Test
    void contextLoads() {
        // Verifies Spring Boot application context loads cleanly with all JPA repositories and controllers
    }
}
