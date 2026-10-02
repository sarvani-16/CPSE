package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.sih.material.entity.User;
import java.time.LocalDateTime;

public class UserDto {

    private Long id;

    @JsonProperty("employee_id")
    private String employeeId;

    private String name;
    private String email;
    private String role;

    @JsonProperty("cpse_name")
    private String cpseName;

    private String status;

    @JsonProperty("is_active")
    private Boolean isActive;

    @JsonProperty("last_login")
    private LocalDateTime lastLogin;

    public UserDto() {}

    public static UserDto fromEntity(User user) {
        UserDto dto = new UserDto();
        dto.setId(user.getId());
        dto.setEmployeeId(user.getEmployeeId());
        dto.setName(user.getName());
        dto.setEmail(user.getEmail());
        dto.setRole(user.getRole());
        dto.setCpseName(user.getCpseName());
        dto.setStatus(user.getStatus());
        dto.setIsActive(user.getIsActive());
        dto.setLastLogin(user.getLastLogin());
        return dto;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getEmployeeId() { return employeeId; }
    public void setEmployeeId(String employeeId) { this.employeeId = employeeId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }

    public LocalDateTime getLastLogin() { return lastLogin; }
    public void setLastLogin(LocalDateTime lastLogin) { this.lastLogin = lastLogin; }
}
