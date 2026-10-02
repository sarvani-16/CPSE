package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class DashboardOverviewResponse {

    @JsonProperty("summary")
    private Map<String, Object> summary;

    @JsonProperty("charts")
    private Map<String, Object> charts;

    @JsonProperty("pipeline_status")
    private List<Map<String, Object>> pipelineStatus;

    public DashboardOverviewResponse() {}

    public DashboardOverviewResponse(Map<String, Object> summary, Map<String, Object> charts, List<Map<String, Object>> pipelineStatus) {
        this.summary = summary;
        this.charts = charts;
        this.pipelineStatus = pipelineStatus;
    }

    public Map<String, Object> getSummary() { return summary; }
    public void setSummary(Map<String, Object> summary) { this.summary = summary; }

    public Map<String, Object> getCharts() { return charts; }
    public void setCharts(Map<String, Object> charts) { this.charts = charts; }

    public List<Map<String, Object>> getPipelineStatus() { return pipelineStatus; }
    public void setPipelineStatus(List<Map<String, Object>> pipelineStatus) { this.pipelineStatus = pipelineStatus; }
}
