package com.sih.material.controller;

import com.sih.material.integration.AiService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@Tag(name = "Health & Status", description = "System health, ML service connectivity, and enterprise status")
public class HealthController {

    private final AiService aiService;

    public HealthController(AiService aiService) {
        this.aiService = aiService;
    }

    /**
     * Ultra-fast liveness check for Render / load-balancer probes.
     * Guaranteed to return 200 OK in < 2ms without downstream dependencies.
     */
    @GetMapping("/health")
    @Operation(summary = "Liveness probe for cloud platform monitoring")
    public ResponseEntity<Map<String, Object>> getLiveness() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "UP");
        resp.put("service", "SIH26099 Enterprise Spring Boot API Gateway");
        resp.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(resp);
    }

    /**
     * Detailed application health & microservice status endpoint.
     */
    @GetMapping("/api/health")
    @Operation(summary = "System Health and Microservice Connectivity Diagnostic")
    public ResponseEntity<Map<String, Object>> getHealth() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "ok");
        resp.put("service", "SIH26099 Enterprise Spring Boot API Gateway");
        resp.put("version", "3.0.0");
        resp.put("architecture", "React (5173) -> Spring Boot (8080) -> PostgreSQL (5432) & FastAPI ML (8001)");
        resp.put("features", List.of(
                "PostgreSQL Enterprise Persistence",
                "Spring Data JPA Data Governance",
                "Dedicated Python ML Microservice (Port 8001)",
                "Human-in-the-Loop Review Center with Batch Actions",
                "National Canonical Material Master (NMM Series)",
                "Immutable Audit Trail with RFC 4180 CSV Export",
                "Active Confidential Credential Sanitization"
        ));
        resp.put("ml_service_status", aiService.checkMlServiceHealth());
        return ResponseEntity.ok(resp);
    }
}
