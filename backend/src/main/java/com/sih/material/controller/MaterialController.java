package com.sih.material.controller;

import com.sih.material.service.MaterialService;
import com.sih.material.service.ReportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@RestController
@RequestMapping("/api/materials")
@Tag(name = "Material Master Ingestion", description = "Enterprise CSV/XLSX catalog upload, schema auto-detection, and source catalog retrieval")
public class MaterialController {

    private final MaterialService materialService;
    private final ReportService reportService;

    public MaterialController(MaterialService materialService, ReportService reportService) {
        this.materialService = materialService;
        this.reportService = reportService;
    }

    @GetMapping("/export")
    @Operation(summary = "Export Source Materials to RFC 4180 CSV")
    public ResponseEntity<String> exportMaterials(
            @RequestParam(value = "cpse_name", required = false) String cpseName,
            @RequestParam(value = "search", required = false) String search
    ) {
        String csv = reportService.exportMaterialsMasterCsv(cpseName, search);
        return ResponseEntity.ok()
                .header(org.springframework.http.HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"material-master-report.csv\"")
                .contentType(MediaType.parseMediaType("text/csv; charset=utf-8"))
                .body(csv);
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload CPSE Material Master (CSV/XLSX)")
    public ResponseEntity<Map<String, Object>> uploadMaterials(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "cpse_name", defaultValue = "ONGC") String cpseName,
            @RequestParam(value = "dry_run", defaultValue = "false") boolean dryRun
    ) throws Exception {
        Map<String, Object> result = materialService.importMaterials(file, cpseName, dryRun);
        return ResponseEntity.ok(result);
    }

    @GetMapping({"", "/source"})
    @Operation(summary = "Get Cataloged Source Materials")
    public ResponseEntity<Map<String, Object>> getSourceMaterials(
            @RequestParam(value = "cpse_name", required = false) String cpseName,
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "page_size", defaultValue = "20") int pageSize
    ) {
        return ResponseEntity.ok(materialService.getSourceMaterials(cpseName, search, page, pageSize));
    }

    @GetMapping("/mappings")
    @Operation(summary = "Get Permanent Material Mappings")
    public ResponseEntity<Map<String, Object>> getMaterialMappings(
            @RequestParam(value = "cpse_name", required = false) String cpseName,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "page_size", defaultValue = "20") int pageSize
    ) {
        return ResponseEntity.ok(materialService.getMaterialMappings(cpseName, page, pageSize));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get Detailed Material Information, Specs & Traceability")
    public ResponseEntity<Map<String, Object>> getMaterialDetail(@PathVariable("id") Long id) {
        return ResponseEntity.ok(materialService.getMaterialDetail(id));
    }
}
