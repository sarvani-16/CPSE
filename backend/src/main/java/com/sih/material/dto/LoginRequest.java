package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;

public class LoginRequest {

    @NotBlank(message = "Employee ID or Official Email is required")
    @JsonProperty("username")
    private String username; // Accepts Employee ID (e.g. ADM001) or Email

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    private String password;

    public LoginRequest() {}

    public LoginRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
