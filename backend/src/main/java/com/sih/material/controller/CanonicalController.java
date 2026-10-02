package com.sih.material.controller;

import com.sih.material.dto.AutoCreateCanonicalRequest;
import com.sih.material.service.CanonicalService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/canonical-materials")
@Tag(name = "National Canonical Materials", description = "Harmonized Common Material Master (NMM Series) codification")
public class CanonicalController {

    private final CanonicalService canonicalService;

    public CanonicalController(CanonicalService canonicalService) {
        this.canonicalService = canonicalService;
    }

    @GetMapping
    @Operation(summary = "Get Harmonized Canonical Materials")
    public ResponseEntity<Map<String, Object>> getCanonicalMaterials(
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "approval_status", required = false) String status,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "page_size", defaultValue = "20") int pageSize
    ) {
        return ResponseEntity.ok(canonicalService.getCanonicalMaterials(search, category, status, page, pageSize));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get Canonical Material Detail with Mappings")
    public ResponseEntity<Map<String, Object>> getCanonicalDetail(@PathVariable("id") String id) {
        return ResponseEntity.ok(canonicalService.getCanonicalMaterialDetail(id));
    }

    @PostMapping("/auto-create")
    @Operation(summary = "Dynamically Create Common Material Code for Unseen Item")
    public ResponseEntity<Map<String, Object>> autoCreateCanonical(
            @RequestBody AutoCreateCanonicalRequest request
    ) {
        return ResponseEntity.ok(canonicalService.autoCreateCanonical(request));
    }
}
