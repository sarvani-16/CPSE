package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotNull;

public class ChangeStatusRequest {

    @NotNull(message = "Active state is required")
    @JsonProperty("active")
    private Boolean active;

    @JsonProperty("status")
    private String status;

    public ChangeStatusRequest() {}

    public ChangeStatusRequest(Boolean active) {
        this.active = active;
        this.status = Boolean.TRUE.equals(active) ? "ACTIVE" : "INACTIVE";
    }

    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
