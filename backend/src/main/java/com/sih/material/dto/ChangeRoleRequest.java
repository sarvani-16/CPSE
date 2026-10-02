package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;

public class ChangeRoleRequest {

    @NotBlank(message = "Role is required (ADMIN, REVIEWER, OFFICER)")
    @JsonProperty("role")
    private String role;

    public ChangeRoleRequest() {}

    public ChangeRoleRequest(String role) {
        this.role = role;
    }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
}
