package com.sih.material.controller;

import com.sih.material.dto.AuthResponse;
import com.sih.material.dto.LoginRequest;
import com.sih.material.dto.RegisterRequest;
import com.sih.material.dto.UserDto;
import com.sih.material.service.AuditService;
import com.sih.material.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@Tag(name = "Authentication & Identity", description = "Enterprise JWT Login, Registration, and Session Management")
public class AuthController {

    private final UserService userService;
    private final AuditService auditService;

    public AuthController(UserService userService, AuditService auditService) {
        this.userService = userService;
        this.auditService = auditService;
    }

    @PostMapping("/login")
    @Operation(summary = "Enterprise User Login with Employee ID / Email")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(userService.login(request));
    }

    @PostMapping("/register")
    @Operation(summary = "Register New Officer Account")
    public ResponseEntity<UserDto> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(userService.register(request));
    }

    @GetMapping("/me")
    @Operation(summary = "Get Current Authenticated User Profile")
    public ResponseEntity<UserDto> getCurrentUser(Authentication authentication) {
        if (authentication == null) {
            return ResponseEntity.status(401).build();
        }
        return ResponseEntity.ok(userService.getUserProfile(authentication.getName()));
    }

    @PostMapping("/logout")
    @Operation(summary = "User Logout & Audit Log")
    public ResponseEntity<Map<String, String>> logout(Authentication authentication) {
        String actor = authentication != null ? authentication.getName() : "ANONYMOUS";
        auditService.recordLog(
                "LOGOUT",
                "users",
                actor,
                null,
                "User logged out",
                actor,
                "Session ended by user",
                null
        );
        return ResponseEntity.ok(Map.of("status", "SUCCESS", "message", "Logged out successfully"));
    }
}
