package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;

public class CompareRequest {

    @NotBlank(message = "title_a cannot be blank")
    @JsonProperty("title_a")
    private String titleA;

    @NotBlank(message = "title_b cannot be blank")
    @JsonProperty("title_b")
    private String titleB;

    public CompareRequest() {}

    public CompareRequest(String titleA, String titleB) {
        this.titleA = titleA;
        this.titleB = titleB;
    }

    public String getTitleA() { return titleA; }
    public void setTitleA(String titleA) { this.titleA = titleA; }

    public String getTitleB() { return titleB; }
    public void setTitleB(String titleB) { this.titleB = titleB; }
}
