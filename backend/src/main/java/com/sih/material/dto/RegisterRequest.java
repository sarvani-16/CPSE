package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public class RegisterRequest {

    @NotBlank(message = "Full Name is required")
    @JsonProperty("name")
    @JsonAlias({"name", "fullName", "full_name"})
    private String name;

    @NotBlank(message = "Employee ID is required")
    @JsonProperty("employee_id")
    @JsonAlias({"employeeId", "employee_id", "empId", "emp_id"})
    private String employeeId;

    @NotBlank(message = "Official Email is required")
    @Email(message = "Invalid email format")
    @JsonProperty("email")
    private String email;

    @NotBlank(message = "CPSE Organization is required")
    @JsonProperty("cpse_name")
    @JsonAlias({"cpseName", "cpse_name", "cpse", "organization"})
    private String cpseName;

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    private String password;

    public RegisterRequest() {}

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmployeeId() { return employeeId; }
    public void setEmployeeId(String employeeId) { this.employeeId = employeeId; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
