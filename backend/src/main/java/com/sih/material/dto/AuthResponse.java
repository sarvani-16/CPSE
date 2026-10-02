package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class AuthResponse {

    @JsonProperty("token")
    private String token;

    @JsonProperty("token_type")
    private String tokenType = "Bearer";

    @JsonProperty("user")
    private UserDto user;

    public AuthResponse() {}

    public AuthResponse(String token, UserDto user) {
        this.token = token;
        this.tokenType = "Bearer";
        this.user = user;
    }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public String getTokenType() { return tokenType; }
    public void setTokenType(String tokenType) { this.tokenType = tokenType; }

    public UserDto getUser() { return user; }
    public void setUser(UserDto user) { this.user = user; }
}
