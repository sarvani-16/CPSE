package com.sih.material;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sih.material.dto.ChangeRoleRequest;
import com.sih.material.dto.ChangeStatusRequest;
import com.sih.material.dto.LoginRequest;
import com.sih.material.entity.AuditLog;
import com.sih.material.entity.User;
import com.sih.material.repository.AuditLogRepository;
import com.sih.material.repository.UserRepository;
import com.sih.material.security.JwtUtil;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("h2")
public class SecurityAndRoleTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AuditLogRepository auditLogRepository;

    @Autowired
    private ObjectMapper objectMapper;

    private String adminToken;
    private String reviewerToken;
    private String officerToken;

    @BeforeEach
    void setUp() {
        // Generate valid JWTs for standard roles
        adminToken = jwtUtil.generateToken(1L, "ADM001", "Admin User", "admin@cpse-harmonization.gov.in", "ADMIN", "CPSE_CONSORTIUM", true);
        reviewerToken = jwtUtil.generateToken(2L, "REV001", "Reviewer User", "audit.officer@cpse.gov.in", "REVIEWER", "GOVERNMENT_AUDIT", true);
        officerToken = jwtUtil.generateToken(3L, "USR001", "Officer User", "procurement@ongc.co.in", "OFFICER", "ONGC", true);
    }

    @Test
    @DisplayName("1. Unauthenticated request to protected endpoint must return 401 Unauthorized")
    void unauthenticatedRequest_returns401() throws Exception {
        mockMvc.perform(get("/api/dashboard/admin"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("2. Malformed or invalid JWT token must return 401 Unauthorized")
    void invalidJwt_returns401() throws Exception {
        mockMvc.perform(get("/api/dashboard/admin")
                        .header("Authorization", "Bearer invalid.jwt.token.here"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("3. Expired JWT token must return 401 Unauthorized")
    void expiredJwt_returns401() throws Exception {
        // Create an expired token with the same secret key
        String secret = "SIH26099EnterpriseSecretKeyForHarmonizationSystem2026SecureHMACSHA256";
        Key key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        String expiredToken = Jwts.builder()
                .setSubject("ADM001")
                .setIssuedAt(new Date(System.currentTimeMillis() - 7200000))
                .setExpiration(new Date(System.currentTimeMillis() - 3600000))
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();

        mockMvc.perform(get("/api/dashboard/admin")
                        .header("Authorization", "Bearer " + expiredToken))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("4. ADMIN user accessing Admin Dashboard must return 200 OK")
    void adminAccessAdminEndpoint_returns200() throws Exception {
        mockMvc.perform(get("/api/dashboard/admin")
                        .header("Authorization", "Bearer " + adminToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.summary.total_materials").exists())
                .andExpect(jsonPath("$.system_health.backend").value("OPERATIONAL"));
    }

    @Test
    @DisplayName("5. REVIEWER user accessing Admin Dashboard must return 403 Forbidden")
    void reviewerAccessAdminEndpoint_returns403() throws Exception {
        mockMvc.perform(get("/api/dashboard/admin")
                        .header("Authorization", "Bearer " + reviewerToken))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error").value("Access Restricted"));
    }

    @Test
    @DisplayName("6. OFFICER user accessing Admin Dashboard must return 403 Forbidden")
    void officerAccessAdminEndpoint_returns403() throws Exception {
        mockMvc.perform(get("/api/dashboard/admin")
                        .header("Authorization", "Bearer " + officerToken))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error").value("Access Restricted"));
    }

    @Test
    @DisplayName("7. REVIEWER user accessing Reviewer Dashboard must return 200 OK")
    void reviewerAccessReviewerDashboard_returns200() throws Exception {
        mockMvc.perform(get("/api/dashboard/reviewer")
                        .header("Authorization", "Bearer " + reviewerToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.summary.pending_reviews").exists())
                .andExpect(jsonPath("$.review_queue").isArray());
    }

    @Test
    @DisplayName("8. OFFICER user accessing Reviewer Dashboard must return 403 Forbidden")
    void officerAccessReviewerDashboard_returns403() throws Exception {
        mockMvc.perform(get("/api/dashboard/reviewer")
                        .header("Authorization", "Bearer " + officerToken))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error").value("Access Restricted"));
    }

    @Test
    @DisplayName("9. OFFICER user accessing Officer Dashboard must return 200 OK")
    void officerAccessOfficerDashboard_returns200() throws Exception {
        mockMvc.perform(get("/api/dashboard/officer")
                        .header("Authorization", "Bearer " + officerToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.summary.my_materials").exists())
                .andExpect(jsonPath("$.summary.cpse_name").value("ONGC"));
    }

    @Test
    @DisplayName("10. OFFICER user attempting review batch approval must return 403 Forbidden")
    void officerPerformReviewAction_returns403() throws Exception {
        String body = "{\"review_ids\": [1], \"comments\": \"Attempted approval by officer\"}";
        mockMvc.perform(post("/api/reviews/batch-approve")
                        .header("Authorization", "Bearer " + officerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("11. Database test: Verify default seed accounts exist with persisted roles")
    void databaseVerification_defaultUsersSeeded() {
        User admin = userRepository.findByEmployeeIdIgnoreCase("ADM001").orElse(null);
        assertThat(admin).isNotNull();
        assertThat(admin.getRole()).isEqualTo("ADMIN");
        assertThat(admin.getEmail()).isEqualTo("admin@cpse-harmonization.gov.in");

        User reviewer = userRepository.findByEmployeeIdIgnoreCase("REV001").orElse(null);
        assertThat(reviewer).isNotNull();
        assertThat(reviewer.getRole()).isEqualTo("REVIEWER");

        User officer = userRepository.findByEmployeeIdIgnoreCase("USR001").orElse(null);
        assertThat(officer).isNotNull();
        assertThat(officer.getRole()).isEqualTo("OFFICER");
    }

    @Test
    @DisplayName("12. Login API: Successful login generates valid JWT, returns role, and updates last_login")
    void loginEndpoint_returnsValidJwtAndRole() throws Exception {
        LoginRequest loginRequest = new LoginRequest("ADM001", "admin123");

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isString())
                .andExpect(jsonPath("$.user.employee_id").value("ADM001"))
                .andExpect(jsonPath("$.user.role").value("ADMIN"))
                .andExpect(jsonPath("$.user.name").isNotEmpty());

        // Verify lastLogin is updated in database
        User admin = userRepository.findByEmployeeIdIgnoreCase("ADM001").orElseThrow();
        assertThat(admin.getLastLogin()).isNotNull();
    }

    @Test
    @DisplayName("13. User Management: Admin toggling status activates/deactivates user and creates audit log")
    void userActivationDeactivation_audited() throws Exception {
        User officer = userRepository.findByEmployeeIdIgnoreCase("USR002").orElseThrow();
        Long officerId = officer.getId();

        ChangeStatusRequest deactivateRequest = new ChangeStatusRequest(false);

        mockMvc.perform(put("/api/users/" + officerId + "/status")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(deactivateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.is_active").value(false));

        User updated = userRepository.findById(officerId).orElseThrow();
        assertThat(updated.getIsActive()).isFalse();

        // Verify audit log exists
        List<AuditLog> logs = auditLogRepository.findAll();
        boolean hasDeactivateLog = logs.stream()
                .anyMatch(l -> "USER_DEACTIVATED".equals(l.getAction()) && officer.getEmployeeId().equals(l.getEntityId()));
        assertThat(hasDeactivateLog).isTrue();

        // Reactivate for test purity
        ChangeStatusRequest activateRequest = new ChangeStatusRequest(true);
        mockMvc.perform(put("/api/users/" + officerId + "/status")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(activateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.is_active").value(true));
    }

    @Test
    @DisplayName("14. User Management: Admin changing user role updates database and creates audit log")
    void roleChange_audited() throws Exception {
        User officer = userRepository.findByEmployeeIdIgnoreCase("USR002").orElseThrow();
        Long officerId = officer.getId();

        ChangeRoleRequest roleRequest = new ChangeRoleRequest("REVIEWER");

        mockMvc.perform(put("/api/users/" + officerId + "/role")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(roleRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.role").value("REVIEWER"));

        User updated = userRepository.findById(officerId).orElseThrow();
        assertThat(updated.getRole()).isEqualTo("REVIEWER");

        // Verify audit log exists
        List<AuditLog> logs = auditLogRepository.findAll();
        boolean hasRoleAudit = logs.stream()
                .anyMatch(l -> "ROLE_CHANGED".equals(l.getAction()) && officer.getEmployeeId().equals(l.getEntityId()));
        assertThat(hasRoleAudit).isTrue();

        // Reset back to OFFICER
        ChangeRoleRequest resetRequest = new ChangeRoleRequest("OFFICER");
        mockMvc.perform(put("/api/users/" + officerId + "/role")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(resetRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.role").value("OFFICER"));
    }
}
