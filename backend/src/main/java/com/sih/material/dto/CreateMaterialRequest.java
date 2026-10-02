package com.sih.material.dto;

import jakarta.validation.constraints.NotBlank;

public class CreateMaterialRequest {

    @NotBlank(message = "Material code is required")
    private String materialCode;

    @NotBlank(message = "Description is required")
    private String description;

    private String cpseName;
    private String specification;
    private String materialType;
    private String materialGrade;
    private String dimensions;
    private String unitOfMeasure;
    private String manufacturer;
    private String partNumber;
    private String category;

    public CreateMaterialRequest() {}

    public CreateMaterialRequest(String materialCode, String description, String cpseName) {
        this.materialCode = materialCode;
        this.description = description;
        this.cpseName = cpseName;
    }

    public String getMaterialCode() { return materialCode; }
    public void setMaterialCode(String materialCode) { this.materialCode = materialCode; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public String getSpecification() { return specification; }
    public void setSpecification(String specification) { this.specification = specification; }

    public String getMaterialType() { return materialType; }
    public void setMaterialType(String materialType) { this.materialType = materialType; }

    public String getMaterialGrade() { return materialGrade; }
    public void setMaterialGrade(String materialGrade) { this.materialGrade = materialGrade; }

    public String getDimensions() { return dimensions; }
    public void setDimensions(String dimensions) { this.dimensions = dimensions; }

    public String getUnitOfMeasure() { return unitOfMeasure; }
    public void setUnitOfMeasure(String unitOfMeasure) { this.unitOfMeasure = unitOfMeasure; }

    public String getManufacturer() { return manufacturer; }
    public void setManufacturer(String manufacturer) { this.manufacturer = manufacturer; }

    public String getPartNumber() { return partNumber; }
    public void setPartNumber(String partNumber) { this.partNumber = partNumber; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
}
