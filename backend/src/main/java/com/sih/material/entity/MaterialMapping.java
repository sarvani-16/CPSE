package com.sih.material.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "material_mappings")
public class MaterialMapping {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "source_material_id", nullable = false)
    private Long sourceMaterialId;

    @Column(name = "cpse_name", nullable = false, length = 100)
    private String cpseName;

    @Column(name = "original_material_code", nullable = false, length = 150)
    private String originalMaterialCode;

    @Column(name = "original_description", nullable = false, columnDefinition = "TEXT")
    private String originalDescription;

    @Column(name = "canonical_material_code", nullable = false, length = 100)
    private String canonicalMaterialCode;

    @Column(name = "canonical_description", nullable = false, columnDefinition = "TEXT")
    private String canonicalDescription;

    @Column(name = "match_status", nullable = false, length = 50)
    private String matchStatus; // MATCH, REVIEW, APPROVED, REJECTED, MANUAL

    @Column(name = "confidence", nullable = false)
    private Double confidence;

    @Column(name = "reviewer", nullable = false, length = 255)
    private String reviewer;

    @Column(name = "timestamp")
    private LocalDateTime timestamp = LocalDateTime.now();

    public MaterialMapping() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSourceMaterialId() { return sourceMaterialId; }
    public void setSourceMaterialId(Long sourceMaterialId) { this.sourceMaterialId = sourceMaterialId; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public String getOriginalMaterialCode() { return originalMaterialCode; }
    public void setOriginalMaterialCode(String originalMaterialCode) { this.originalMaterialCode = originalMaterialCode; }

    public String getOriginalDescription() { return originalDescription; }
    public void setOriginalDescription(String originalDescription) { this.originalDescription = originalDescription; }

    public String getCanonicalMaterialCode() { return canonicalMaterialCode; }
    public void setCanonicalMaterialCode(String canonicalMaterialCode) { this.canonicalMaterialCode = canonicalMaterialCode; }

    public String getCanonicalDescription() { return canonicalDescription; }
    public void setCanonicalDescription(String canonicalDescription) { this.canonicalDescription = canonicalDescription; }

    public String getMatchStatus() { return matchStatus; }
    public void setMatchStatus(String matchStatus) { this.matchStatus = matchStatus; }

    public Double getConfidence() { return confidence; }
    public void setConfidence(Double confidence) { this.confidence = confidence; }

    public String getReviewer() { return reviewer; }
    public void setReviewer(String reviewer) { this.reviewer = reviewer; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}
