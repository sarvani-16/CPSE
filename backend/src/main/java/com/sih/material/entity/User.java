package com.sih.material.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Enterprise User Entity for Role-Based Access Control (RBAC).
 * Supports Roles: ADMIN, REVIEWER, OFFICER.
 */
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_user_employee_id", columnList = "employee_id"),
    @Index(name = "idx_user_email", columnList = "email"),
    @Index(name = "idx_user_role", columnList = "role")
})
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "employee_id", unique = true, nullable = false, length = 50)
    private String employeeId;

    @Column(name = "name", nullable = false, length = 255)
    private String name;

    @Column(name = "email", unique = true, nullable = false, length = 255)
    private String email;

    @Column(name = "password_hash", nullable = false, length = 255)
    private String passwordHash;

    @Column(name = "role", nullable = false, length = 50)
    private String role; // ADMIN, REVIEWER, OFFICER

    @Column(name = "cpse_name", length = 100)
    private String cpseName; // e.g. ONGC, BHEL, IOCL, CPSE_CONSORTIUM

    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;

    @Column(name = "status", nullable = false, length = 50)
    private String status = "ACTIVE"; // ACTIVE, PENDING_APPROVAL, INACTIVE

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    @Column(name = "last_login")
    private LocalDateTime lastLogin;

    public User() {}

    public User(String employeeId, String name, String email, String passwordHash, String role, String cpseName) {
        this.employeeId = employeeId;
        this.name = name;
        this.email = email;
        this.passwordHash = passwordHash;
        this.role = role;
        this.cpseName = cpseName;
        this.isActive = true;
        this.status = "ACTIVE";
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getEmployeeId() { return employeeId; }
    public void setEmployeeId(String employeeId) { this.employeeId = employeeId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPasswordHash() { return passwordHash; }
    public void setPasswordHash(String passwordHash) { this.passwordHash = passwordHash; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getCpseName() { return cpseName; }
    public void setCpseName(String cpseName) { this.cpseName = cpseName; }

    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public LocalDateTime getLastLogin() { return lastLogin; }
    public void setLastLogin(LocalDateTime lastLogin) { this.lastLogin = lastLogin; }
}
