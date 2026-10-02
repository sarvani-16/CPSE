package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AutoCreateCanonicalRequest {

    @JsonProperty("source_material_id")
    private Long sourceMaterialId;

    @JsonProperty("description")
    private String description;

    @JsonProperty("cpse_name")
    private String cpseName = "CPSE";

    @JsonProperty("material_code")
    private String materialCode = "UNSPECIFIED";

    @JsonProperty("specification")
    private String specification;

    @JsonProperty("material_grade")
    private String materialGrade;

    @JsonProperty("dimensions")
    private String dimensions;

    @JsonProperty("unit_of_measure")
    private String unitOfMeasure = "EA";

    @JsonProperty("category")
    private String category;

    @JsonProperty("reviewer")
    private String reviewer = "AI_STANDARDIZATION_ENGINE";

    public AutoCreateCanonicalRequest() {}

    public Long getSourceMaterialId() { return sourceMaterialId; }
    public void setSourceMaterialId(Long sourceMaterialId) { this.sourceMaterialId = sourceMaterialId; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public String getMaterialCode() { return materialCode; }
    public void setMaterialCode(String materialCode) { this.materialCode = materialCode; }

    public String getSpecification() { return specification; }
    public void setSpecification(String specification) { this.specification = specification; }

    public String getMaterialGrade() { return materialGrade; }
    public void setMaterialGrade(String materialGrade) { this.materialGrade = materialGrade; }

    public String getDimensions() { return dimensions; }
    public void setDimensions(String dimensions) { this.dimensions = dimensions; }

    public String getUnitOfMeasure() { return unitOfMeasure; }
    public void setUnitOfMeasure(String unitOfMeasure) { this.unitOfMeasure = unitOfMeasure; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getReviewer() { return reviewer; }
    public void setReviewer(String reviewer) { this.reviewer = reviewer; }
}
