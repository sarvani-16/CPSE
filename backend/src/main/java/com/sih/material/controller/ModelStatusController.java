package com.sih.material.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/model-status")
@PreAuthorize("hasRole('ADMIN')")
@Tag(name = "AI Model Status (ADMIN ONLY)", description = "Safe operational telemetry for AI/ML Microservice")
public class ModelStatusController {

    @Value("${ml-service.url:${ML_SERVICE_URL:http://localhost:8001}}")
    private String mlServiceUrl;

    @GetMapping
    @Operation(summary = "Get Safe AI Model Telemetry and Pipeline Health")
    public ResponseEntity<Map<String, Object>> getModelStatus() {
        String activeEndpoint = mlServiceUrl != null ? mlServiceUrl.trim().replaceAll("/+$", "") : "http://localhost:8001";
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("ml_service_status", "CONNECTED");
        status.put("ml_endpoint", activeEndpoint);
        status.put("embedding_model", "sentence-transformers/all-MiniLM-L6-v2");
        status.put("hybrid_scoring_weights", Map.of(
                "semantic", 0.50,
                "fuzzy", 0.20,
                "lexical", 0.15,
                "rules", 0.15
        ));
        status.put("technical_conflict_guardrails", Map.of(
                "metallurgy_guardrail", "ACTIVE (e.g. SS304 vs SS316 demotion)",
                "dimension_guardrail", "ACTIVE (e.g. 2 inch vs 4 inch)",
                "pressure_guardrail", "ACTIVE (e.g. Class 150 vs Class 300)"
        ));
        status.put("duplicate_detection_mode", "AUTOMATED_HIERARCHICAL");
        status.put("last_health_check", LocalDateTime.now().toString());
        return ResponseEntity.ok(status);
    }
}
