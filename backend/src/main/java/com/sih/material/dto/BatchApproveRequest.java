package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public class BatchApproveRequest {

    @NotEmpty(message = "review_ids list must not be empty")
    @JsonProperty("review_ids")
    private List<Long> reviewIds;

    @JsonProperty("reviewer_name")
    private String reviewerName = "Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)";

    @JsonProperty("comment")
    private String comment;

    @JsonProperty("min_confidence")
    private Double minConfidence = 0.80;

    public BatchApproveRequest() {}

    public List<Long> getReviewIds() { return reviewIds; }
    public void setReviewIds(List<Long> reviewIds) { this.reviewIds = reviewIds; }

    public String getReviewerName() { return reviewerName; }
    public void setReviewerName(String reviewerName) { this.reviewerName = reviewerName; }

    public String getComment() { return comment; }
    public void setComment(String comment) { this.comment = comment; }

    public Double getMinConfidence() { return minConfidence; }
    public void setMinConfidence(Double minConfidence) { this.minConfidence = minConfidence; }
}
