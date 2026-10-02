package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class BatchApproveResponse {

    @JsonProperty("total_requested")
    private int totalRequested;

    @JsonProperty("approved_count")
    private int approvedCount;

    @JsonProperty("skipped_count")
    private int skippedCount;

    @JsonProperty("rejected_count")
    private int rejectedCount;

    @JsonProperty("approved_ids")
    private List<Long> approvedIds;

    @JsonProperty("skipped_ids")
    private List<Long> skippedIds;

    @JsonProperty("reasons")
    private List<String> reasons;

    public BatchApproveResponse() {}

    public int getTotalRequested() { return totalRequested; }
    public void setTotalRequested(int totalRequested) { this.totalRequested = totalRequested; }

    public int getApprovedCount() { return approvedCount; }
    public void setApprovedCount(int approvedCount) { this.approvedCount = approvedCount; }

    public int getSkippedCount() { return skippedCount; }
    public void setSkippedCount(int skippedCount) { this.skippedCount = skippedCount; }

    public int getRejectedCount() { return rejectedCount; }
    public void setRejectedCount(int rejectedCount) { this.rejectedCount = rejectedCount; }

    public List<Long> getApprovedIds() { return approvedIds; }
    public void setApprovedIds(List<Long> approvedIds) { this.approvedIds = approvedIds; }

    public List<Long> getSkippedIds() { return skippedIds; }
    public void setSkippedIds(List<Long> skippedIds) { this.skippedIds = skippedIds; }

    public List<String> getReasons() { return reasons; }
    public void setReasons(List<String> reasons) { this.reasons = reasons; }
}
