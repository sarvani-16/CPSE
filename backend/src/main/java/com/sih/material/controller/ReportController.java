package com.sih.material.controller;

import com.sih.material.service.ReportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reports")
@Tag(name = "Official Reports & Data Export", description = "Dynamic CSV and data exports from PostgreSQL enterprise records")
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    /**
     * Unified Export Endpoint for Report Templates
     */
    @GetMapping("/export")
    @Operation(summary = "Export Official Report to RFC 4180 CSV by Type")
    public ResponseEntity<String> exportReport(
            @RequestParam(value = "type", defaultValue = "harmonization-master") String type,
            @RequestParam(value = "cpse", required = false) String cpse,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "date", required = false) String date,
            @RequestParam(value = "action", required = false) String action,
            @RequestParam(value = "search", required = false) String search
    ) {
        String cleanType = type != null ? type.trim().toLowerCase() : "harmonization-master";
        String csvContent;
        String filename;

        switch (cleanType) {
            case "duplicate-analysis":
            case "duplicate":
            case "duplicates":
                csvContent = reportService.exportDuplicateReportCsv(cpse, status);
                filename = "duplicate-report.csv";
                break;

            case "review-audit-trail":
            case "review":
            case "reviews":
                csvContent = reportService.exportReviewReportCsv(status);
                filename = "review-report.csv";
                break;

            case "cpse-summary":
            case "summary":
                csvContent = reportService.exportCpseSummaryReportCsv();
                filename = "cpse-summary-report.csv";
                break;

            case "audit":
            case "audit-logs":
                csvContent = reportService.exportAuditReportCsv(action, null, null, date);
                filename = "audit-report.csv";
                break;

            case "materials":
            case "material-master":
                csvContent = reportService.exportMaterialsMasterCsv(cpse, search);
                filename = "material-master-report.csv";
                break;

            case "harmonization-master":
            case "harmonization":
            default:
                csvContent = reportService.exportHarmonizationReportCsv(cpse, status);
                filename = "harmonization-report.csv";
                break;
        }

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csvContent);
    }

    @GetMapping("/harmonization/export")
    @Operation(summary = "Export Harmonization Master to CSV")
    public ResponseEntity<String> exportHarmonization(
            @RequestParam(value = "cpse", required = false) String cpse,
            @RequestParam(value = "status", required = false) String status
    ) {
        String csv = reportService.exportHarmonizationReportCsv(cpse, status);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"harmonization-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }

    @GetMapping("/materials/export")
    @Operation(summary = "Export Material Master Catalog to CSV")
    public ResponseEntity<String> exportMaterials(
            @RequestParam(value = "cpse", required = false) String cpse,
            @RequestParam(value = "search", required = false) String search
    ) {
        String csv = reportService.exportMaterialsMasterCsv(cpse, search);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"material-master-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }

    @GetMapping("/duplicates/export")
    @Operation(summary = "Export Duplicate / Equivalence Candidates to CSV")
    public ResponseEntity<String> exportDuplicates(
            @RequestParam(value = "cpse", required = false) String cpse,
            @RequestParam(value = "status", required = false) String status
    ) {
        String csv = reportService.exportDuplicateReportCsv(cpse, status);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"duplicate-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }

    @GetMapping("/reviews/export")
    @Operation(summary = "Export Review Queue Decisions to CSV")
    public ResponseEntity<String> exportReviews(
            @RequestParam(value = "status", required = false) String status
    ) {
        String csv = reportService.exportReviewReportCsv(status);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"review-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }

    @GetMapping("/audit/export")
    @Operation(summary = "Export Governance Audit Trail to CSV")
    public ResponseEntity<String> exportAudit(
            @RequestParam(value = "action", required = false) String action,
            @RequestParam(value = "entity", required = false) String entity,
            @RequestParam(value = "user", required = false) String user,
            @RequestParam(value = "date", required = false) String date
    ) {
        String csv = reportService.exportAuditReportCsv(action, entity, user, date);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"audit-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }

    @GetMapping("/cpse-summary/export")
    @Operation(summary = "Export CPSE Inventory Breakdown to CSV")
    public ResponseEntity<String> exportCpseSummary() {
        String csv = reportService.exportCpseSummaryReportCsv();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"cpse-summary-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }
}
