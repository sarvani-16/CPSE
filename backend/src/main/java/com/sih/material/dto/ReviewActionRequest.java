package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ReviewActionRequest {

    @JsonProperty("reviewer_name")
    private String reviewerName = "Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)";

    @JsonProperty("comment")
    private String comment;

    public ReviewActionRequest() {}

    public String getReviewerName() { return reviewerName; }
    public void setReviewerName(String reviewerName) { this.reviewerName = reviewerName; }

    public String getComment() { return comment; }
    public void setComment(String comment) { this.comment = comment; }
}
