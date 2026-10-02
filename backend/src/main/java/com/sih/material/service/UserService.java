package com.sih.material.service;

import com.sih.material.dto.AuthResponse;
import com.sih.material.dto.LoginRequest;
import com.sih.material.dto.RegisterRequest;
import com.sih.material.dto.UserDto;
import com.sih.material.entity.User;
import com.sih.material.exception.ResourceNotFoundException;
import com.sih.material.repository.UserRepository;
import com.sih.material.security.JwtUtil;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
public class UserService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final AuditService auditService;

    public UserService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil,
                       AuditService auditService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
        this.auditService = auditService;
    }

    /**
     * Seeds initial development & demonstration accounts if not already present.
     * Guaranteed Roles:
     * - ADM001: ADMIN
     * - REV001: REVIEWER
     * - USR001: OFFICER
     */
    @PostConstruct
    @Transactional
    public void seedDefaultAccounts() {
        seedAccountIfMissing("ADM001", "Dr. Rajesh Sharma (Director General)", "admin@cpse-harmonization.gov.in", "admin123", "ADMIN", "CPSE_CONSORTIUM");
        seedAccountIfMissing("REV001", "P. Venkatraman (Chief Technical Auditor)", "audit.officer@cpse.gov.in", "reviewer123", "REVIEWER", "GOVERNMENT_AUDIT");
        seedAccountIfMissing("USR001", "S. Ananya (Material Procurement Officer)", "procurement@ongc.co.in", "officer123", "OFFICER", "ONGC");
        seedAccountIfMissing("USR002", "Vikram Malhotra (Senior Engineer - Stores)", "procurement@bhel.in", "officer123", "OFFICER", "BHEL");
    }

    private void seedAccountIfMissing(String empId, String name, String email, String rawPassword, String role, String cpse) {
        if (!userRepository.existsByEmployeeIdIgnoreCase(empId)) {
            User user = new User(
                    empId,
                    name,
                    email,
                    passwordEncoder.encode(rawPassword),
                    role,
                    cpse
            );
            userRepository.save(user);
            log.info("[+] Seeded enterprise user account: {} ({}) with role {}", empId, email, role);
        }
    }

    @Transactional
    public AuthResponse login(LoginRequest req) {
        User user = userRepository.findByEmployeeIdOrEmail(req.getUsername().trim())
                .orElseThrow(() -> new BadCredentialsException("Invalid Employee ID / Email or Password"));

        if (!Boolean.TRUE.equals(user.getIsActive())) {
            throw new BadCredentialsException("Account is deactivated. Please contact your system administrator.");
        }

        if (!passwordEncoder.matches(req.getPassword(), user.getPasswordHash())) {
            throw new BadCredentialsException("Invalid Employee ID / Email or Password");
        }

        user.setLastLogin(LocalDateTime.now());
        userRepository.save(user);

        String token = jwtUtil.generateToken(
                user.getId(),
                user.getEmployeeId(),
                user.getName(),
                user.getEmail(),
                user.getRole(),
                user.getCpseName(),
                Boolean.TRUE.equals(user.getIsActive())
        );

        auditService.recordLog(
                "LOGIN",
                "users",
                user.getEmployeeId(),
                null,
                "Successful authentication",
                user.getEmployeeId(),
                "User logged in from enterprise web gateway",
                null
        );

        return new AuthResponse(token, UserDto.fromEntity(user));
    }

    @Transactional
    public UserDto register(RegisterRequest req) {
        if (userRepository.existsByEmployeeIdIgnoreCase(req.getEmployeeId().trim())) {
            throw new IllegalArgumentException("Employee ID already registered.");
        }
        if (userRepository.existsByEmailIgnoreCase(req.getEmail().trim())) {
            throw new IllegalArgumentException("Email address already registered.");
        }

        User user = new User();
        user.setEmployeeId(req.getEmployeeId().trim().toUpperCase());
        user.setName(req.getName().trim());
        user.setEmail(req.getEmail().trim().toLowerCase());
        user.setPasswordHash(passwordEncoder.encode(req.getPassword()));
        user.setRole("OFFICER"); // Default role strictly OFFICER (zero public privilege escalation)
        user.setCpseName(req.getCpseName().trim());
        user.setIsActive(true);
        user.setStatus("ACTIVE");
        user.setCreatedAt(LocalDateTime.now());
        user.setUpdatedAt(LocalDateTime.now());

        User saved = userRepository.save(user);

        auditService.recordLog(
                "USER_CREATED",
                "users",
                saved.getEmployeeId(),
                null,
                "New account registered as OFFICER",
                saved.getEmployeeId(),
                "Self-registration via enterprise portal",
                null
        );

        return UserDto.fromEntity(saved);
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getAllUsers(String role, String search, int page, int pageSize) {
        Pageable pageable = PageRequest.of(Math.max(0, page - 1), Math.max(1, Math.min(100, pageSize)));
        boolean hasRole = role != null && !role.trim().isEmpty() && !"ALL".equalsIgnoreCase(role.trim());
        boolean hasSearch = search != null && !search.trim().isEmpty();

        Page<User> userPage;
        if (!hasRole && !hasSearch) {
            userPage = userRepository.findAll(pageable);
        } else {
            userPage = userRepository.searchUsers(
                    hasRole ? role.trim() : null,
                    hasSearch ? search.trim() : null,
                    pageable
            );
        }

        Map<String, Object> resp = new HashMap<>();
        resp.put("total", userPage.getTotalElements());
        resp.put("page", page);
        resp.put("page_size", pageSize);
        resp.put("total_pages", userPage.getTotalPages());
        resp.put("items", userPage.getContent().stream().map(UserDto::fromEntity).toList());
        return resp;
    }

    @Transactional
    public UserDto changeRole(Long userId, String newRole, String adminActor) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));

        String oldRole = user.getRole();
        String validRole = newRole.trim().toUpperCase();
        if (!validRole.equals("ADMIN") && !validRole.equals("REVIEWER") && !validRole.equals("OFFICER")) {
            throw new IllegalArgumentException("Invalid role: " + newRole + ". Permitted roles: ADMIN, REVIEWER, OFFICER");
        }

        user.setRole(validRole);
        user.setUpdatedAt(LocalDateTime.now());
        User updated = userRepository.save(user);

        auditService.recordLog(
                "ROLE_CHANGED",
                "users",
                user.getEmployeeId(),
                oldRole,
                validRole,
                adminActor != null ? adminActor : "ADMIN",
                "Administrator updated user role from " + oldRole + " to " + validRole,
                null
        );

        return UserDto.fromEntity(updated);
    }

    @Transactional
    public UserDto changeStatus(Long userId, boolean active, String adminActor) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));

        boolean oldStatus = Boolean.TRUE.equals(user.getIsActive());
        user.setIsActive(active);
        user.setStatus(active ? "ACTIVE" : "INACTIVE");
        user.setUpdatedAt(LocalDateTime.now());
        User updated = userRepository.save(user);

        String action = active ? "USER_ACTIVATED" : "USER_DEACTIVATED";
        auditService.recordLog(
                action,
                "users",
                user.getEmployeeId(),
                String.valueOf(oldStatus),
                String.valueOf(active),
                adminActor != null ? adminActor : "ADMIN",
                "Administrator toggled active status to " + active,
                null
        );

        return UserDto.fromEntity(updated);
    }

    @Transactional(readOnly = true)
    public UserDto getUserProfile(String identifier) {
        User user = userRepository.findByEmployeeIdOrEmail(identifier)
                .orElseThrow(() -> new ResourceNotFoundException("User not found: " + identifier));
        return UserDto.fromEntity(user);
    }
}
