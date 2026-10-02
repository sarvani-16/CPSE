package com.sih.material.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "source_materials", indexes = {
    @Index(name = "idx_source_material_user_id", columnList = "user_id"),
    @Index(name = "idx_source_material_cpse", columnList = "cpse_name"),
    @Index(name = "idx_source_material_code", columnList = "material_code")
})
public class SourceMaterial {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @com.fasterxml.jackson.annotation.JsonIgnore
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", insertable = false, updatable = false)
    private User user;

    @Column(name = "cpse_name", nullable = false, length = 100)
    private String cpseName;

    @Column(name = "material_code", nullable = false, length = 150)
    private String materialCode;

    @Column(name = "description", nullable = false, columnDefinition = "TEXT")
    private String description;

    @Column(name = "specification", columnDefinition = "TEXT")
    private String specification;

    @Column(name = "material_type", length = 100)
    private String materialType;

    @Column(name = "material_grade", length = 100)
    private String materialGrade;

    @Column(name = "dimensions", length = 150)
    private String dimensions;

    @Column(name = "unit_of_measure", length = 50)
    private String unitOfMeasure;

    @Column(name = "manufacturer", length = 255)
    private String manufacturer;

    @Column(name = "part_number", length = 150)
    private String partNumber;

    @Column(name = "category", length = 150)
    private String category;

    @Column(name = "source_file", length = 255)
    private String sourceFile;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    public SourceMaterial() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public String getMaterialCode() { return materialCode; }
    public void setMaterialCode(String materialCode) { this.materialCode = materialCode; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

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

    public String getSourceFile() { return sourceFile; }
    public void setSourceFile(String sourceFile) { this.sourceFile = sourceFile; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
