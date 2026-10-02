package com.sih.material.controller;

import com.sih.material.dto.CompareRequest;
import com.sih.material.dto.CompareResponse;
import com.sih.material.integration.AiService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/matching")
@Tag(name = "AI Matching Engine", description = "Material comparison routed through Spring Boot to FastAPI ML Service")
public class MatchingController {

    private final AiService aiService;

    public MatchingController(AiService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/compare")
    @Operation(summary = "Compare Two Material Descriptions via AI ML Service")
    public ResponseEntity<CompareResponse> compareMaterials(@Valid @RequestBody CompareRequest request) {
        CompareResponse response = aiService.compareMaterials(request.getTitleA(), request.getTitleB());
        return ResponseEntity.ok(response);
    }
}
