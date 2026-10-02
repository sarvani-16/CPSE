package com.sih.material.integration;

import com.sih.material.dto.CompareRequest;
import com.sih.material.dto.CompareResponse;
import com.sih.material.exception.AiServiceUnavailableException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Dedicated Integration Service for Python FastAPI ML Microservice.
 * Isolates all HTTP communication to ML_SERVICE_URL (default: http://localhost:8001).
 * Translates connection failures into controlled enterprise error responses.
 */
@Service
public class AiService {

    private static final Logger log = LoggerFactory.getLogger(AiService.class);

    private final RestTemplate restTemplate;

    @Value("${ml-service.url:http://localhost:8001}")
    private String mlServiceUrl;

    public AiService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Executes AI hybrid material comparison (MiniLM + TF-IDF + RapidFuzz + Guardrails)
     * by invoking FastAPI endpoint POST /api/match.
     */
    public CompareResponse compareMaterials(String titleA, String titleB) {
        String endpoint = mlServiceUrl + "/api/match";
        log.debug("Invoking ML Service endpoint: {}", endpoint);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        CompareRequest requestPayload = new CompareRequest(titleA, titleB);
        HttpEntity<CompareRequest> entity = new HttpEntity<>(requestPayload, headers);

        try {
            ResponseEntity<CompareResponse> response = restTemplate.postForEntity(
                    endpoint,
                    entity,
                    CompareResponse.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new AiServiceUnavailableException("AI Service returned non-success status: " + response.getStatusCode());
            }

        } catch (ResourceAccessException e) {
            log.error("AI matching service unreachable at {}: {}", mlServiceUrl, e.getMessage());
            throw new AiServiceUnavailableException("AI matching service is currently unavailable. Please ensure the Python ML microservice is running on " + mlServiceUrl);
        } catch (RestClientException e) {
            log.error("Error communicating with AI matching service: {}", e.getMessage());
            throw new AiServiceUnavailableException("AI matching service communication failure: " + e.getMessage());
        }
    }

    /**
     * Retrieves health status from the Python ML microservice.
     */
    public Map<String, Object> checkMlServiceHealth() {
        String endpoint = mlServiceUrl + "/api/health";
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(endpoint, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            }
        } catch (Exception e) {
            log.warn("ML Service health check failed: {}", e.getMessage());
        }
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("status", "UNAVAILABLE");
        fallback.put("url", mlServiceUrl);
        fallback.put("message", "Python ML service is not reachable on port 8001");
        return fallback;
    }
}
