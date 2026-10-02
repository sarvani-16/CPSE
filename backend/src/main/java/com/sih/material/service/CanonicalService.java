package com.sih.material.service;

import com.sih.material.dto.AutoCreateCanonicalRequest;
import com.sih.material.entity.CanonicalMaterial;
import com.sih.material.entity.MaterialMapping;
import com.sih.material.entity.SourceMaterial;
import com.sih.material.exception.ResourceNotFoundException;
import com.sih.material.repository.CanonicalMaterialRepository;
import com.sih.material.repository.MaterialMappingRepository;
import com.sih.material.repository.SourceMaterialRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class CanonicalService {

    private static final Logger log = LoggerFactory.getLogger(CanonicalService.class);

    private final CanonicalMaterialRepository canonicalRepository;
    private final SourceMaterialRepository sourceMaterialRepository;
    private final MaterialMappingRepository mappingRepository;
    private final AuditService auditService;

    public CanonicalService(CanonicalMaterialRepository canonicalRepository,
                            SourceMaterialRepository sourceMaterialRepository,
                            MaterialMappingRepository mappingRepository,
                            AuditService auditService) {
        this.canonicalRepository = canonicalRepository;
        this.sourceMaterialRepository = sourceMaterialRepository;
        this.mappingRepository = mappingRepository;
        this.auditService = auditService;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getCanonicalMaterials(String search, String category, String status, int page, int pageSize) {
        Pageable pageable = PageRequest.of(Math.max(0, page - 1), Math.max(1, Math.min(100, pageSize)));
        boolean hasSearch = search != null && !search.trim().isEmpty();
        boolean hasCategory = category != null && !category.trim().isEmpty() && !"ALL".equalsIgnoreCase(category.trim());
        boolean hasStatus = status != null && !status.trim().isEmpty() && !"ALL".equalsIgnoreCase(status.trim());

        Page<CanonicalMaterial> matPage;
        if (!hasSearch && !hasCategory && !hasStatus) {
            matPage = canonicalRepository.findAll(pageable);
        } else {
            matPage = canonicalRepository.searchCanonical(
                    hasSearch ? search.trim() : null,
                    hasCategory ? category.trim() : null,
                    hasStatus ? status.trim() : null,
                    pageable
            );
        }

        Map<String, Object> result = new HashMap<>();
        result.put("total", matPage.getTotalElements());
        result.put("page", page);
        result.put("page_size", pageSize);
        result.put("total_pages", matPage.getTotalPages());
        result.put("items", matPage.getContent());
        return result;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getCanonicalMaterialDetail(String code) {
        CanonicalMaterial canonical = canonicalRepository.findByNationalMaterialCode(code)
                .or(() -> canonicalRepository.findByCanonicalCode(code))
                .orElseThrow(() -> new ResourceNotFoundException("Canonical material not found with code: " + code));

        List<MaterialMapping> mappings = mappingRepository.findByCanonicalMaterialCode(canonical.getCanonicalCode());

        Map<String, Object> response = new HashMap<>();
        response.put("canonical_material", canonical);
        response.put("mapped_cpse_count", mappings.size());
        response.put("mappings", mappings);
        return response;
    }

    @Transactional
    public Map<String, Object> autoCreateCanonical(AutoCreateCanonicalRequest req) {
        SourceMaterial source = null;
        if (req.getSourceMaterialId() != null) {
            source = sourceMaterialRepository.findById(req.getSourceMaterialId())
                    .orElseThrow(() -> new ResourceNotFoundException("Source material not found with id: " + req.getSourceMaterialId()));
        }

        String description = source != null ? source.getDescription() : req.getDescription();
        String cpseName = source != null ? source.getCpseName() : req.getCpseName();
        String materialCode = source != null ? source.getMaterialCode() : req.getMaterialCode();

        if (description == null || description.isBlank()) {
            throw new IllegalArgumentException("Description cannot be empty for canonical code creation");
        }

        // Idempotency check: see if a mapping already exists for this source material
        if (source != null) {
            Optional<MaterialMapping> existingMap = mappingRepository.findByCpseNameAndOriginalMaterialCode(cpseName, materialCode);
            if (existingMap.isPresent()) {
                MaterialMapping map = existingMap.get();
                Optional<CanonicalMaterial> existingCanonical = canonicalRepository.findByCanonicalCode(map.getCanonicalMaterialCode());
                if (existingCanonical.isPresent()) {
                    Map<String, Object> resp = new HashMap<>();
                    resp.put("status", "EXISTS");
                    resp.put("message", "Material is already mapped to canonical code: " + map.getCanonicalMaterialCode());
                    resp.put("canonical_material", existingCanonical.get());
                    resp.put("mapping", map);
                    return resp;
                }
            }
        }

        // Generate next NMM Code
        Long maxId = canonicalRepository.getMaxId();
        long nextNum = (maxId != null ? maxId : 8) + 1;
        String nextCode = String.format("NMM-%06d", nextNum);

        CanonicalMaterial newCanon = new CanonicalMaterial();
        newCanon.setNationalMaterialCode(nextCode);
        newCanon.setCanonicalCode(nextCode);
        newCanon.setCodeTypeLabel("Prototype Common Material Code");
        newCanon.setStandardizedDescription(description);
        newCanon.setCanonicalDescription(description);
        newCanon.setCategory(req.getCategory() != null ? req.getCategory() : (source != null ? source.getCategory() : "General"));
        newCanon.setMaterialType(source != null ? source.getMaterialType() : "Standard");
        newCanon.setStandardSpecification(source != null ? source.getSpecification() : req.getSpecification());
        newCanon.setStandardUom(source != null ? source.getUnitOfMeasure() : req.getUnitOfMeasure());
        newCanon.setApprovalStatus("APPROVED");
        newCanon.setCreatedAt(LocalDateTime.now());
        newCanon.setUpdatedAt(LocalDateTime.now());

        CanonicalMaterial savedCanon = canonicalRepository.save(newCanon);

        // Create mapping
        MaterialMapping mapping = new MaterialMapping();
        mapping.setSourceMaterialId(source != null ? source.getId() : 0L);
        mapping.setCpseName(cpseName);
        mapping.setOriginalMaterialCode(materialCode);
        mapping.setOriginalDescription(description);
        mapping.setCanonicalMaterialCode(nextCode);
        mapping.setCanonicalDescription(description);
        mapping.setMatchStatus("APPROVED");
        mapping.setConfidence(1.0);
        mapping.setReviewer(req.getReviewer() != null ? req.getReviewer() : "AI_STANDARDIZATION_ENGINE");
        mapping.setTimestamp(LocalDateTime.now());

        MaterialMapping savedMapping = mappingRepository.save(mapping);

        // Record Audit Event
        auditService.recordLog(
                "CREATE_CANONICAL_CODE",
                "canonical_materials",
                nextCode,
                null,
                description,
                req.getReviewer() != null ? req.getReviewer() : "AI_STANDARDIZATION_ENGINE",
                "Dynamic canonical code creation for unmapped material",
                "{\"source_material_id\": " + (source != null ? source.getId() : 0) + ", \"cpse\": \"" + cpseName + "\"}"
        );

        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "CREATED");
        resp.put("canonical_code", nextCode);
        resp.put("canonical_material", savedCanon);
        resp.put("mapping", savedMapping);
        return resp;
    }
}
