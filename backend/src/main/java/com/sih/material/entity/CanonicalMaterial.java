package com.sih.material.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "canonical_materials")
public class CanonicalMaterial {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "national_material_code", nullable = false, unique = true, length = 100)
    private String nationalMaterialCode;

    @Column(name = "code_type_label", nullable = false, length = 100)
    private String codeTypeLabel = "Prototype Common Material Code";

    @Column(name = "canonical_code", unique = true, length = 100)
    private String canonicalCode;

    @Column(name = "standardized_description", nullable = false, columnDefinition = "TEXT")
    private String standardizedDescription;

    @Column(name = "canonical_description", columnDefinition = "TEXT")
    private String canonicalDescription;

    @Column(name = "category", length = 150)
    private String category;

    @Column(name = "material_type", length = 100)
    private String materialType;

    @Column(name = "standard_specification", columnDefinition = "TEXT")
    private String standardSpecification;

    @Column(name = "standard_uom", length = 50)
    private String standardUom;

    @Column(name = "technical_attributes", columnDefinition = "TEXT")
    private String technicalAttributes;

    @Column(name = "approval_status", nullable = false, length = 50)
    private String approvalStatus = "APPROVED";

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    public CanonicalMaterial() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNationalMaterialCode() { return nationalMaterialCode; }
    public void setNationalMaterialCode(String nationalMaterialCode) { this.nationalMaterialCode = nationalMaterialCode; }

    public String getCodeTypeLabel() { return codeTypeLabel; }
    public void setCodeTypeLabel(String codeTypeLabel) { this.codeTypeLabel = codeTypeLabel; }

    public String getCanonicalCode() { return canonicalCode; }
    public void setCanonicalCode(String canonicalCode) { this.canonicalCode = canonicalCode; }

    public String getStandardizedDescription() { return standardizedDescription; }
    public void setStandardizedDescription(String standardizedDescription) { this.standardizedDescription = standardizedDescription; }

    public String getCanonicalDescription() { return canonicalDescription; }
    public void setCanonicalDescription(String canonicalDescription) { this.canonicalDescription = canonicalDescription; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getMaterialType() { return materialType; }
    public void setMaterialType(String materialType) { this.materialType = materialType; }

    public String getStandardSpecification() { return standardSpecification; }
    public void setStandardSpecification(String standardSpecification) { this.standardSpecification = standardSpecification; }

    public String getStandardUom() { return standardUom; }
    public void setStandardUom(String standardUom) { this.standardUom = standardUom; }

    public String getTechnicalAttributes() { return technicalAttributes; }
    public void setTechnicalAttributes(String technicalAttributes) { this.technicalAttributes = technicalAttributes; }

    public String getApprovalStatus() { return approvalStatus; }
    public void setApprovalStatus(String approvalStatus) { this.approvalStatus = approvalStatus; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
