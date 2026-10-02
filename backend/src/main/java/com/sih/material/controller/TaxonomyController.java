package com.sih.material.controller;

import com.sih.material.entity.Taxonomy;
import com.sih.material.service.TaxonomyService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/taxonomy")
@Tag(name = "Commodity Taxonomy Management", description = "Standardized multi-level hierarchy for industrial CPSE commodities")
public class TaxonomyController {

    private final TaxonomyService taxonomyService;

    public TaxonomyController(TaxonomyService taxonomyService) {
        this.taxonomyService = taxonomyService;
    }

    @GetMapping
    @Operation(summary = "Get Full Commodity Taxonomy Tree")
    public ResponseEntity<List<Map<String, Object>>> getTaxonomyTree() {
        return ResponseEntity.ok(taxonomyService.getTaxonomyTree());
    }

    @GetMapping("/list")
    @Operation(summary = "Get Flat List of Taxonomy Categories")
    public ResponseEntity<List<Taxonomy>> getAllList() {
        return ResponseEntity.ok(taxonomyService.getAllTaxonomies());
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Create Taxonomy Node (ADMIN ONLY)")
    public ResponseEntity<Taxonomy> createTaxonomy(@RequestBody Taxonomy item) {
        return ResponseEntity.ok(taxonomyService.createTaxonomy(item));
    }
}
