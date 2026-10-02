package com.sih.material.controller;

import com.sih.material.dto.ChangeRoleRequest;
import com.sih.material.dto.ChangeStatusRequest;
import com.sih.material.dto.UserDto;
import com.sih.material.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping({"/api/users", "/api/admin/users"})
@PreAuthorize("hasRole('ADMIN')")
@Tag(name = "User Management (Admin Only)", description = "Enterprise Role-Based User Management and Status Administration")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    @Operation(summary = "List Users with Role and Search Filters")
    public ResponseEntity<Map<String, Object>> getUsers(
            @RequestParam(value = "role", required = false) String role,
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "page_size", defaultValue = "20") int pageSize
    ) {
        return ResponseEntity.ok(userService.getAllUsers(role, search, page, pageSize));
    }

    @PutMapping("/{id}/role")
    @Operation(summary = "Change User Role (ADMIN, REVIEWER, OFFICER)")
    public ResponseEntity<UserDto> changeRole(
            @PathVariable("id") Long id,
            @Valid @RequestBody ChangeRoleRequest request,
            Authentication authentication
    ) {
        String adminActor = authentication != null ? authentication.getName() : "ADMIN";
        return ResponseEntity.ok(userService.changeRole(id, request.getRole(), adminActor));
    }

    @PutMapping("/{id}/status")
    @Operation(summary = "Toggle User Active Status (Activate / Deactivate)")
    public ResponseEntity<UserDto> changeStatus(
            @PathVariable("id") Long id,
            @Valid @RequestBody ChangeStatusRequest request,
            Authentication authentication
    ) {
        String adminActor = authentication != null ? authentication.getName() : "ADMIN";
        return ResponseEntity.ok(userService.changeStatus(id, request.getActive(), adminActor));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get User by ID")
    public ResponseEntity<UserDto> getUserById(@PathVariable("id") Long id) {
        return ResponseEntity.ok(userService.getUserProfile(String.valueOf(id)));
    }
}
