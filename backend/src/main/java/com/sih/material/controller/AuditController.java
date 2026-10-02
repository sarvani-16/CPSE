package com.sih.material.controller;

import com.sih.material.dto.AuditLogsResponse;
import com.sih.material.service.AuditService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@RestController
@RequestMapping({"/api/audit-logs", "/api/admin/audit-logs"})
@Tag(name = "Enterprise Governance & Audit Trail", description = "Immutable lifecycle event logging, multi-factor filtering, and CSV export")
public class AuditController {

    private final AuditService auditService;

    public AuditController(AuditService auditService) {
        this.auditService = auditService;
    }

    @GetMapping
    @Operation(summary = "Get Paginated Governance Audit Logs with Multi-Factor Filters")
    public ResponseEntity<AuditLogsResponse> getAuditLogs(
            @RequestParam(value = "action", required = false) String action,
            @RequestParam(value = "entity", required = false) String entity,
            @RequestParam(value = "user", required = false) String user,
            @RequestParam(value = "date", required = false) String date,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "page_size", defaultValue = "25") int pageSize
    ) {
        return ResponseEntity.ok(auditService.getAuditLogs(action, entity, user, date, page, pageSize));
    }

    @GetMapping("/export")
    @Operation(summary = "Export Audit Report to RFC 4180 CSV")
    public ResponseEntity<String> exportAuditLogs(
            @RequestParam(value = "action", required = false) String action,
            @RequestParam(value = "entity", required = false) String entity,
            @RequestParam(value = "user", required = false) String user,
            @RequestParam(value = "date", required = false) String date
    ) {
        String csvContent = auditService.exportAuditLogsCsv(action, entity, user, date);
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String filename = "SIH26099_Audit_Report_" + timestamp + ".csv";

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csvContent);
    }
}
