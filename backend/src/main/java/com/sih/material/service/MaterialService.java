package com.sih.material.service;

import com.sih.material.dto.UploadPreviewResponse;
import com.sih.material.entity.MaterialMapping;
import com.sih.material.entity.SourceMaterial;
import com.sih.material.repository.MaterialMappingRepository;
import com.sih.material.repository.SourceMaterialRepository;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

@Service
public class MaterialService {

    private static final Logger log = LoggerFactory.getLogger(MaterialService.class);

    private final SourceMaterialRepository sourceMaterialRepository;
    private final MaterialMappingRepository mappingRepository;
    private final AuditService auditService;

    // Standard column synonyms
    private static final Map<String, List<String>> SYNONYMS = Map.of(
            "material_code", List.of("material_code", "mat_code", "matcode", "item_no", "item_code", "material_no", "part_no", "item_number"),
            "description", List.of("description", "mat_desc", "material_description", "item_description", "long_description", "short_desc", "title"),
            "specification", List.of("specification", "tech_spec", "technical_specification", "spec", "item_spec"),
            "material_grade", List.of("material_grade", "grade", "steel_grade", "metallurgy", "mat_grade"),
            "dimensions", List.of("dimensions", "size", "dimension", "dim", "rating"),
            "unit_of_measure", List.of("unit_of_measure", "uom", "base_uom", "unit", "measure_unit"),
            "category", List.of("category", "commodity", "group", "material_group", "item_category")
    );

    public MaterialService(SourceMaterialRepository sourceMaterialRepository,
                           MaterialMappingRepository mappingRepository,
                           AuditService auditService) {
        this.sourceMaterialRepository = sourceMaterialRepository;
        this.mappingRepository = mappingRepository;
        this.auditService = auditService;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getSourceMaterials(Long userId, String userRole, String cpseName, String search, int page, int pageSize) {
        Pageable pageable = PageRequest.of(Math.max(0, page - 1), Math.max(1, Math.min(100, pageSize)));
        boolean hasCpse = cpseName != null && !cpseName.trim().isEmpty() && !"ALL".equalsIgnoreCase(cpseName.trim());
        boolean hasSearch = search != null && !search.trim().isEmpty();
        boolean isAdmin = userRole != null && "ADMIN".equalsIgnoreCase(userRole.trim());

        Page<SourceMaterial> p;
        if (isAdmin) {
            if (!hasCpse && !hasSearch) {
                p = sourceMaterialRepository.findAll(pageable);
            } else if (hasCpse && !hasSearch) {
                p = sourceMaterialRepository.findByCpseNameIgnoreCase(cpseName.trim(), pageable);
            } else {
                p = sourceMaterialRepository.searchMaterials(
                        hasCpse ? cpseName.trim() : null,
                        hasSearch ? search.trim() : null,
                        pageable
                );
            }
        } else {
            // Strictly isolate to the authenticated user's records
            if (userId == null) {
                p = Page.empty(pageable);
            } else {
                p = sourceMaterialRepository.searchMaterialsForUser(
                        userId,
                        hasCpse ? cpseName.trim() : null,
                        hasSearch ? search.trim() : null,
                        pageable
                );
            }
        }

        Map<String, Object> resp = new HashMap<>();
        resp.put("total", p.getTotalElements());
        resp.put("page", page);
        resp.put("page_size", pageSize);
        resp.put("total_pages", p.getTotalPages());
        resp.put("items", p.getContent());
        resp.put("materials", p.getContent());
        resp.put("content", p.getContent());
        return resp;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getSourceMaterials(String cpseName, String search, int page, int pageSize) {
        return getSourceMaterials(null, "ADMIN", cpseName, search, page, pageSize);
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getMaterialDetail(Long id, Long userId, String userRole) {
        boolean isAdmin = userRole != null && "ADMIN".equalsIgnoreCase(userRole.trim());
        SourceMaterial sm;
        if (isAdmin) {
            sm = sourceMaterialRepository.findById(id)
                    .orElseThrow(() -> new com.sih.material.exception.ResourceNotFoundException("Material not found: " + id));
        } else {
            sm = (userId != null)
                    ? sourceMaterialRepository.findByIdAndUserId(id, userId)
                            .orElseThrow(() -> new com.sih.material.exception.ResourceNotFoundException("Material not found: " + id))
                    : sourceMaterialRepository.findById(id)
                            .orElseThrow(() -> new com.sih.material.exception.ResourceNotFoundException("Material not found: " + id));
        }

        Map<String, Object> detail = new LinkedHashMap<>();
        detail.put("id", sm.getId());
        detail.put("material_code", sm.getMaterialCode());
        detail.put("description", sm.getDescription());
        detail.put("cpse_name", sm.getCpseName());
        detail.put("specification", sm.getSpecification());
        detail.put("material_type", sm.getMaterialType());
        detail.put("material_grade", sm.getMaterialGrade());
        detail.put("dimensions", sm.getDimensions());
        detail.put("unit_of_measure", sm.getUnitOfMeasure());
        detail.put("manufacturer", sm.getManufacturer());
        detail.put("part_number", sm.getPartNumber());
        detail.put("category", sm.getCategory());
        detail.put("source_file", sm.getSourceFile());
        detail.put("created_at", sm.getCreatedAt());

        // Normalized Info
        Map<String, Object> normalized = new LinkedHashMap<>();
        normalized.put("normalized_description", sm.getDescription().toUpperCase().replaceAll("\\s+", " "));
        normalized.put("extracted_attributes", Map.of(
                "grade", sm.getMaterialGrade() != null ? sm.getMaterialGrade() : "Standard",
                "dimensions", sm.getDimensions() != null ? sm.getDimensions() : "Standard",
                "uom", sm.getUnitOfMeasure() != null ? sm.getUnitOfMeasure() : "EA"
        ));
        normalized.put("technical_parameters", sm.getSpecification() != null ? sm.getSpecification() : "Industrial Standard");
        detail.put("normalized_info", normalized);

        // Mappings / Canonical association
        Optional<MaterialMapping> mapping = mappingRepository.findByCpseNameAndOriginalMaterialCode(sm.getCpseName(), sm.getMaterialCode());
        if (mapping.isPresent()) {
            detail.put("mapping", mapping.get());
            detail.put("canonical_code", mapping.get().getCanonicalMaterialCode());
            detail.put("status", mapping.get().getMatchStatus());
        } else {
            detail.put("status", "UNMAPPED");
        }

        return detail;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getMaterialDetail(Long id) {
        return getMaterialDetail(id, null, "ADMIN");
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getMaterialMappings(String cpseName, int page, int pageSize) {
        Pageable pageable = PageRequest.of(Math.max(0, page - 1), Math.max(1, Math.min(100, pageSize)));
        boolean hasCpse = cpseName != null && !cpseName.trim().isEmpty() && !"ALL".equalsIgnoreCase(cpseName.trim());
        Page<MaterialMapping> p = hasCpse ? mappingRepository.findByCpseFilter(cpseName.trim(), pageable) : mappingRepository.findAll(pageable);

        Map<String, Object> resp = new HashMap<>();
        resp.put("total", p.getTotalElements());
        resp.put("page", page);
        resp.put("page_size", pageSize);
        resp.put("total_pages", p.getTotalPages());
        resp.put("items", p.getContent());
        return resp;
    }

    public UploadPreviewResponse previewUpload(MultipartFile file, String cpseName) throws Exception {
        String filename = file.getOriginalFilename() != null ? file.getOriginalFilename() : "upload.csv";
        boolean isExcel = filename.toLowerCase().endsWith(".xlsx") || filename.toLowerCase().endsWith(".xls");

        List<String> headers = new ArrayList<>();
        List<Map<String, Object>> previewRows = new ArrayList<>();
        int totalRows = 0;

        if (isExcel) {
            try (Workbook workbook = new XSSFWorkbook(file.getInputStream())) {
                Sheet sheet = workbook.getSheetAt(0);
                Row headerRow = sheet.getRow(0);
                if (headerRow != null) {
                    for (Cell c : headerRow) {
                        headers.add(c.getStringCellValue().trim());
                    }
                }
                for (int i = 1; i <= Math.min(5, sheet.getLastRowNum()); i++) {
                    Row r = sheet.getRow(i);
                    if (r == null) continue;
                    Map<String, Object> rowMap = new HashMap<>();
                    for (int j = 0; j < headers.size(); j++) {
                        Cell c = r.getCell(j);
                        rowMap.put(headers.get(j), c != null ? c.toString() : "");
                    }
                    previewRows.add(rowMap);
                }
                totalRows = sheet.getLastRowNum();
            }
        } else {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8));
                 CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.builder().setHeader().setSkipHeaderRecord(true).build())) {
                headers.addAll(csvParser.getHeaderNames());
                for (CSVRecord record : csvParser) {
                    totalRows++;
                    if (previewRows.size() < 5) {
                        Map<String, Object> rowMap = new HashMap<>();
                        for (String h : headers) {
                            rowMap.put(h, record.isSet(h) ? record.get(h) : "");
                        }
                        previewRows.add(rowMap);
                    }
                }
            }
        }

        Map<String, String> suggestedMappings = detectMappings(headers);
        List<String> missingRequired = new ArrayList<>();
        if (!suggestedMappings.containsKey("material_code")) missingRequired.add("material_code");
        if (!suggestedMappings.containsKey("description")) missingRequired.add("description");

        UploadPreviewResponse response = new UploadPreviewResponse();
        response.setFilename(filename);
        response.setFileType(isExcel ? "xlsx" : "csv");
        response.setTotalRowsDetected(totalRows);
        response.setDetectedColumns(headers);
        response.setSuggestedMappings(suggestedMappings);
        response.setUnmappedColumns(new ArrayList<>());
        response.setMissingRequiredFields(missingRequired);
        response.setPreviewRows(previewRows);
        response.setValid(missingRequired.isEmpty());
        response.setValidationMessage(missingRequired.isEmpty() ? "Valid schema auto-detected." : "Missing required columns: " + missingRequired);

        return response;
    }

    private Map<String, String> detectMappings(List<String> headers) {
        Map<String, String> mappings = new HashMap<>();
        for (String h : headers) {
            String cleanH = h.trim().toLowerCase().replaceAll("[^a-z0-9_]", "_");
            for (Map.Entry<String, List<String>> entry : SYNONYMS.entrySet()) {
                if (entry.getValue().contains(cleanH)) {
                    mappings.put(entry.getKey(), h);
                    break;
                }
            }
        }
        return mappings;
    }

    @Transactional
    public SourceMaterial createMaterial(com.sih.material.dto.CreateMaterialRequest req, Long userId, String employeeId) {
        String cpseName = req.getCpseName() != null && !req.getCpseName().isBlank() ? req.getCpseName().trim() : "ONGC";
        String code = req.getMaterialCode().trim();

        Optional<SourceMaterial> existing = (userId != null)
                ? sourceMaterialRepository.findByUserIdAndCpseNameAndMaterialCode(userId, cpseName, code)
                : sourceMaterialRepository.findByCpseNameAndMaterialCode(cpseName, code);

        SourceMaterial mat = existing.orElse(new SourceMaterial());
        mat.setUserId(userId);
        mat.setCpseName(cpseName);
        mat.setMaterialCode(code);
        mat.setDescription(req.getDescription().trim());
        if (req.getSpecification() != null) mat.setSpecification(req.getSpecification().trim());
        if (req.getMaterialType() != null) mat.setMaterialType(req.getMaterialType().trim());
        if (req.getMaterialGrade() != null) mat.setMaterialGrade(req.getMaterialGrade().trim());
        if (req.getDimensions() != null) mat.setDimensions(req.getDimensions().trim());
        if (req.getUnitOfMeasure() != null) mat.setUnitOfMeasure(req.getUnitOfMeasure().trim());
        if (req.getManufacturer() != null) mat.setManufacturer(req.getManufacturer().trim());
        if (req.getPartNumber() != null) mat.setPartNumber(req.getPartNumber().trim());
        if (req.getCategory() != null) mat.setCategory(req.getCategory().trim());
        mat.setSourceFile("MANUAL_CREATION");

        SourceMaterial saved = sourceMaterialRepository.save(mat);

        auditService.recordLog(
                "CREATE_MATERIAL",
                "source_materials",
                String.valueOf(saved.getId()),
                null,
                saved.getMaterialCode(),
                employeeId != null ? employeeId : "SYSTEM",
                "User created material in catalog",
                "{\"materialCode\":\"" + saved.getMaterialCode() + "\",\"userId\":" + userId + "}"
        );

        return saved;
    }

    @Transactional
    public Map<String, Object> importMaterials(MultipartFile file, String cpseName, boolean dryRun, Long userId, String employeeId) throws Exception {
        UploadPreviewResponse preview = previewUpload(file, cpseName);
        if (!preview.isValid()) {
            throw new IllegalArgumentException("Invalid schema: " + preview.getValidationMessage());
        }

        if (dryRun) {
            Map<String, Object> resp = new HashMap<>();
            resp.put("status", "DRY_RUN");
            resp.put("preview", preview);
            return resp;
        }

        Map<String, String> mappings = preview.getSuggestedMappings();
        String codeCol = mappings.get("material_code");
        String descCol = mappings.get("description");
        String specCol = mappings.get("specification");
        String gradeCol = mappings.get("material_grade");
        String dimCol = mappings.get("dimensions");
        String uomCol = mappings.get("unit_of_measure");
        String catCol = mappings.get("category");

        int importedCount = 0;
        int skippedCount = 0;

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8));
             CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.builder().setHeader().setSkipHeaderRecord(true).build())) {

            for (CSVRecord record : csvParser) {
                String code = record.isSet(codeCol) ? record.get(codeCol).trim() : null;
                String desc = record.isSet(descCol) ? record.get(descCol).trim() : null;

                if (code == null || code.isBlank() || desc == null || desc.isBlank()) {
                    skippedCount++;
                    continue;
                }

                Optional<SourceMaterial> existing = (userId != null)
                        ? sourceMaterialRepository.findByUserIdAndCpseNameAndMaterialCode(userId, cpseName, code)
                        : sourceMaterialRepository.findByCpseNameAndMaterialCode(cpseName, code);
                SourceMaterial mat = existing.orElse(new SourceMaterial());
                mat.setUserId(userId);
                mat.setCpseName(cpseName);
                mat.setMaterialCode(code);
                mat.setDescription(desc);
                if (specCol != null && record.isSet(specCol)) mat.setSpecification(record.get(specCol).trim());
                if (gradeCol != null && record.isSet(gradeCol)) mat.setMaterialGrade(record.get(gradeCol).trim());
                if (dimCol != null && record.isSet(dimCol)) mat.setDimensions(record.get(dimCol).trim());
                if (uomCol != null && record.isSet(uomCol)) mat.setUnitOfMeasure(record.get(uomCol).trim());
                if (catCol != null && record.isSet(catCol)) mat.setCategory(record.get(catCol).trim());
                mat.setSourceFile(preview.getFilename());

                sourceMaterialRepository.save(mat);
                importedCount++;
            }
        }

        auditService.recordLog(
                "UPLOAD_MATERIALS",
                "source_materials",
                cpseName,
                null,
                "Imported " + importedCount + " records",
                employeeId != null ? employeeId : "PROCUREMENT_OFFICER",
                "Batch material catalog ingestion from " + preview.getFilename(),
                "{\"filename\": \"" + preview.getFilename() + "\", \"imported\": " + importedCount + ", \"user_id\": " + userId + "}"
        );

        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "SUCCESS");
        resp.put("imported_count", importedCount);
        resp.put("records_ingested", importedCount);
        resp.put("skipped_count", skippedCount);
        resp.put("cpse_name", cpseName);
        resp.put("filename", preview.getFilename());
        return resp;
    }

    @Transactional
    public Map<String, Object> importMaterials(MultipartFile file, String cpseName, boolean dryRun) throws Exception {
        return importMaterials(file, cpseName, dryRun, null, "PROCUREMENT_OFFICER");
    }
}
