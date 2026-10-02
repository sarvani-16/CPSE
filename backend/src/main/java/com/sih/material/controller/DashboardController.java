package com.sih.material.controller;

import com.sih.material.dto.DashboardOverviewResponse;
import com.sih.material.security.UserPrincipal;
import com.sih.material.service.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping({"/api/dashboard", "/api/analytics"})
@Tag(name = "Executive Dashboard", description = "Role-based analytics, KPI metrics, and harmonization pipeline status")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping("/overview")
    @Operation(summary = "Get Dynamic Dashboard KPIs & Charts (Overview)")
    public ResponseEntity<DashboardOverviewResponse> getOverview() {
        return ResponseEntity.ok(dashboardService.getOverview());
    }

    @GetMapping("/admin")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Get Administration Dashboard KPIs, Charts & System Health")
    public ResponseEntity<Map<String, Object>> getAdminDashboard() {
        return ResponseEntity.ok(dashboardService.getAdminDashboard());
    }

    @GetMapping("/reviewer")
    @PreAuthorize("hasAnyRole('ADMIN', 'REVIEWER')")
    @Operation(summary = "Get Reviewer Dashboard KPIs & Prioritized Review Queue")
    public ResponseEntity<Map<String, Object>> getReviewerDashboard() {
        return ResponseEntity.ok(dashboardService.getReviewerDashboard());
    }

    @GetMapping("/officer")
    @PreAuthorize("hasAnyRole('ADMIN', 'OFFICER')")
    @Operation(summary = "Get Material Operations Dashboard for Officer CPSE")
    public ResponseEntity<Map<String, Object>> getOfficerDashboard(Authentication authentication) {
        String cpseName = null;
        String username = null;
        if (authentication != null) {
            username = authentication.getName();
            if (authentication.getPrincipal() instanceof UserPrincipal principal) {
                cpseName = principal.getCpseName();
            }
        }
        return ResponseEntity.ok(dashboardService.getOfficerDashboard(cpseName, username));
    }
}
