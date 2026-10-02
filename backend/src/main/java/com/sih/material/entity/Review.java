package com.sih.material.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "reviews")
public class Review {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "source_material_id", nullable = false)
    private Long sourceMaterialId;

    @Column(name = "suggested_canonical_code", nullable = false, length = 100)
    private String suggestedCanonicalCode;

    @Column(name = "status", nullable = false, length = 50)
    private String status = "PENDING"; // PENDING, APPROVED, REJECTED, NEEDS_REVIEW

    @Column(name = "semantic_score")
    private Double semanticScore;

    @Column(name = "fuzzy_score")
    private Double fuzzyScore;

    @Column(name = "lexical_score")
    private Double lexicalScore;

    @Column(name = "hybrid_score")
    private Double hybridScore;

    @Column(name = "detected_attributes", columnDefinition = "TEXT")
    private String detectedAttributes;

    @Column(name = "conflicts", columnDefinition = "TEXT")
    private String conflicts;

    @Column(name = "explanation", columnDefinition = "TEXT")
    private String explanation;

    @Column(name = "reviewer_name", length = 255)
    private String reviewerName;

    @Column(name = "comments", columnDefinition = "TEXT")
    private String comments;

    @Column(name = "reviewed_at")
    private LocalDateTime reviewedAt;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    public Review() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getSourceMaterialId() { return sourceMaterialId; }
    public void setSourceMaterialId(Long sourceMaterialId) { this.sourceMaterialId = sourceMaterialId; }

    public String getSuggestedCanonicalCode() { return suggestedCanonicalCode; }
    public void setSuggestedCanonicalCode(String suggestedCanonicalCode) { this.suggestedCanonicalCode = suggestedCanonicalCode; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Double getSemanticScore() { return semanticScore; }
    public void setSemanticScore(Double semanticScore) { this.semanticScore = semanticScore; }

    public Double getFuzzyScore() { return fuzzyScore; }
    public void setFuzzyScore(Double fuzzyScore) { this.fuzzyScore = fuzzyScore; }

    public Double getLexicalScore() { return lexicalScore; }
    public void setLexicalScore(Double lexicalScore) { this.lexicalScore = lexicalScore; }

    public Double getHybridScore() { return hybridScore; }
    public void setHybridScore(Double hybridScore) { this.hybridScore = hybridScore; }

    public String getDetectedAttributes() { return detectedAttributes; }
    public void setDetectedAttributes(String detectedAttributes) { this.detectedAttributes = detectedAttributes; }

    public String getConflicts() { return conflicts; }
    public void setConflicts(String conflicts) { this.conflicts = conflicts; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public String getReviewerName() { return reviewerName; }
    public void setReviewerName(String reviewerName) { this.reviewerName = reviewerName; }

    public String getComments() { return comments; }
    public void setComments(String comments) { this.comments = comments; }

    public LocalDateTime getReviewedAt() { return reviewedAt; }
    public void setReviewedAt(LocalDateTime reviewedAt) { this.reviewedAt = reviewedAt; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
