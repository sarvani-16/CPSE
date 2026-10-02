package com.sih.material.service;

import com.sih.material.entity.MaterialMapping;
import com.sih.material.entity.Review;
import com.sih.material.entity.SourceMaterial;
import com.sih.material.repository.CanonicalMaterialRepository;
import com.sih.material.repository.MaterialMappingRepository;
import com.sih.material.repository.ReviewRepository;
import com.sih.material.repository.SourceMaterialRepository;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.StringWriter;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
public class ReportService {

    private static final Logger log = LoggerFactory.getLogger(ReportService.class);
    private static final DateTimeFormatter ISO_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final SourceMaterialRepository sourceMaterialRepository;
    private final CanonicalMaterialRepository canonicalRepository;
    private final MaterialMappingRepository mappingRepository;
    private final ReviewRepository reviewRepository;
    private final AuditService auditService;

    public ReportService(SourceMaterialRepository sourceMaterialRepository,
                         CanonicalMaterialRepository canonicalRepository,
                         MaterialMappingRepository mappingRepository,
                         ReviewRepository reviewRepository,
                         AuditService auditService) {
        this.sourceMaterialRepository = sourceMaterialRepository;
        this.canonicalRepository = canonicalRepository;
        this.mappingRepository = mappingRepository;
        this.reviewRepository = reviewRepository;
        this.auditService = auditService;
    }

    /**
     * 1. Material Harmonization Master Report
     * Maps source catalog items to National Canonical codes with confidence, status, and specs.
     */
    @Transactional(readOnly = true)
    public String exportHarmonizationReportCsv(String cpseName, String status) {
        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT.builder()
                .setHeader("CPSE", "Original Material Code", "Original Description", "Canonical Material Code",
                        "Canonical Description", "Confidence Rating", "Match Status", "Reviewer", "Timestamp")
                .build())) {

            List<MaterialMapping> mappings;
            boolean hasCpse = cpseName != null && !cpseName.isBlank() && !"ALL".equalsIgnoreCase(cpseName.trim());
            if (hasCpse) {
                Page<MaterialMapping> p = mappingRepository.findByCpseFilter(cpseName.trim(), PageRequest.of(0, 10000, Sort.by(Sort.Direction.DESC, "timestamp")));
                mappings = p.getContent();
            } else {
                mappings = mappingRepository.findAll(Sort.by(Sort.Direction.DESC, "timestamp"));
            }

            for (MaterialMapping m : mappings) {
                if (status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status.trim()) && !status.equalsIgnoreCase(m.getMatchStatus())) {
                    continue;
                }
                printer.printRecord(
                        m.getCpseName(),
                        m.getOriginalMaterialCode(),
                        m.getOriginalDescription(),
                        m.getCanonicalMaterialCode(),
                        m.getCanonicalDescription(),
                        String.format("%.2f%%", (m.getConfidence() != null ? m.getConfidence() : 1.0) * 100.0),
                        m.getMatchStatus(),
                        m.getReviewer(),
                        m.getTimestamp() != null ? m.getTimestamp().format(ISO_FMT) : ""
                );
            }
            printer.flush();
        } catch (Exception e) {
            log.error("Failed to generate harmonization CSV export: ", e);
            throw new RuntimeException("Failed to generate harmonization CSV report", e);
        }
        return sw.toString();
    }

    /**
     * 2. Source Material Master Catalog Report
     * Ingested items across CPSEs with material code, specs, UOM, and grade.
     */
    @Transactional(readOnly = true)
    public String exportMaterialsMasterCsv(Long userId, String userRole, String cpseName, String search) {
        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT.builder()
                .setHeader("Material Code", "Description", "CPSE", "Category", "Material Type",
                        "Material Grade", "Specification", "Dimensions", "Unit of Measure", "Source File", "Created Date")
                .build())) {

            boolean hasCpse = cpseName != null && !cpseName.isBlank() && !"ALL".equalsIgnoreCase(cpseName.trim());
            boolean hasSearch = search != null && !search.isBlank();
            boolean isAdmin = userRole != null && "ADMIN".equalsIgnoreCase(userRole.trim());

            List<SourceMaterial> materials;
            if (isAdmin) {
                if (hasCpse || hasSearch) {
                    Page<SourceMaterial> p = sourceMaterialRepository.searchMaterials(
                            hasCpse ? cpseName.trim() : null,
                            hasSearch ? search.trim() : null,
                            PageRequest.of(0, 10000, Sort.by(Sort.Direction.ASC, "materialCode"))
                    );
                    materials = p.getContent();
                } else {
                    materials = sourceMaterialRepository.findAll(Sort.by(Sort.Direction.ASC, "materialCode"));
                }
            } else {
                if (userId == null) {
                    materials = Collections.emptyList();
                } else {
                    materials = sourceMaterialRepository.findForExportUser(
                            userId,
                            hasCpse ? cpseName.trim() : null,
                            hasSearch ? search.trim() : null,
                            Sort.by(Sort.Direction.ASC, "materialCode")
                    );
                }
            }

            for (SourceMaterial m : materials) {
                printer.printRecord(
                        m.getMaterialCode(),
                        m.getDescription(),
                        m.getCpseName(),
                        m.getCategory() != null ? m.getCategory() : "",
                        m.getMaterialType() != null ? m.getMaterialType() : "",
                        m.getMaterialGrade() != null ? m.getMaterialGrade() : "",
                        m.getSpecification() != null ? m.getSpecification() : "",
                        m.getDimensions() != null ? m.getDimensions() : "",
                        m.getUnitOfMeasure() != null ? m.getUnitOfMeasure() : "",
                        m.getSourceFile() != null ? m.getSourceFile() : "",
                        m.getCreatedAt() != null ? m.getCreatedAt().format(ISO_FMT) : ""
                );
            }
            printer.flush();
        } catch (Exception e) {
            log.error("Failed to generate materials master CSV export: ", e);
            throw new RuntimeException("Failed to generate material master CSV report", e);
        }
        return sw.toString();
    }

    @Transactional(readOnly = true)
    public String exportMaterialsMasterCsv(String cpseName, String search) {
        return exportMaterialsMasterCsv(null, "ADMIN", cpseName, search);
    }

    /**
     * 3. Cross-CPSE Duplicate Identification Report
     * Duplicates, candidate pairs, and AI similarity match scores.
     */
    @Transactional(readOnly = true)
    public String exportDuplicateReportCsv(String cpseName, String status) {
        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT.builder()
                .setHeader("Review ID", "Source Material ID", "Source Material Code", "CPSE", "Original Description",
                        "Suggested Canonical Code", "Hybrid Score", "Lexical Score", "Semantic Score",
                        "Match Status", "Reviewer", "Review Comments", "Created Date")
                .build())) {

            List<Review> reviews = reviewRepository.findAll(Sort.by(Sort.Direction.DESC, "createdAt"));
            List<Long> sourceIds = reviews.stream().map(Review::getSourceMaterialId).filter(Objects::nonNull).distinct().collect(Collectors.toList());
            Map<Long, SourceMaterial> sourceMap = sourceMaterialRepository.findAllById(sourceIds).stream()
                    .collect(Collectors.toMap(SourceMaterial::getId, Function.identity()));

            boolean filterCpse = cpseName != null && !cpseName.isBlank() && !"ALL".equalsIgnoreCase(cpseName.trim());
            boolean filterStatus = status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status.trim());

            for (Review r : reviews) {
                SourceMaterial sm = sourceMap.get(r.getSourceMaterialId());
                if (filterCpse && sm != null && !cpseName.equalsIgnoreCase(sm.getCpseName())) {
                    continue;
                }
                if (filterStatus && !status.equalsIgnoreCase(r.getStatus())) {
                    continue;
                }

                printer.printRecord(
                        r.getId(),
                        r.getSourceMaterialId(),
                        sm != null ? sm.getMaterialCode() : "",
                        sm != null ? sm.getCpseName() : "",
                        sm != null ? sm.getDescription() : "",
                        r.getSuggestedCanonicalCode(),
                        r.getHybridScore() != null ? String.format("%.4f", r.getHybridScore()) : "",
                        r.getLexicalScore() != null ? String.format("%.4f", r.getLexicalScore()) : "",
                        r.getSemanticScore() != null ? String.format("%.4f", r.getSemanticScore()) : "",
                        r.getStatus(),
                        r.getReviewerName() != null ? r.getReviewerName() : "",
                        r.getComments() != null ? r.getComments() : "",
                        r.getCreatedAt() != null ? r.getCreatedAt().format(ISO_FMT) : ""
                );
            }
            printer.flush();
        } catch (Exception e) {
            log.error("Failed to generate duplicate analysis CSV export: ", e);
            throw new RuntimeException("Failed to generate duplicate analysis CSV report", e);
        }
        return sw.toString();
    }

    /**
     * 4. Human-in-the-Loop Review Queue Report
     */
    @Transactional(readOnly = true)
    public String exportReviewReportCsv(String status) {
        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT.builder()
                .setHeader("Review ID", "Source Material ID", "Suggested Canonical Code", "Status",
                        "Hybrid Score", "Lexical Score", "Semantic Score", "Reviewer", "Comments", "Created At", "Reviewed At")
                .build())) {

            boolean hasStatus = status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status.trim());
            List<Review> reviews = hasStatus
                    ? reviewRepository.searchReviews(status.trim(), PageRequest.of(0, 10000)).getContent()
                    : reviewRepository.findAll(Sort.by(Sort.Direction.DESC, "createdAt"));

            for (Review r : reviews) {
                printer.printRecord(
                        r.getId(),
                        r.getSourceMaterialId(),
                        r.getSuggestedCanonicalCode(),
                        r.getStatus(),
                        r.getHybridScore() != null ? String.format("%.4f", r.getHybridScore()) : "",
                        r.getLexicalScore() != null ? String.format("%.4f", r.getLexicalScore()) : "",
                        r.getSemanticScore() != null ? String.format("%.4f", r.getSemanticScore()) : "",
                        r.getReviewerName() != null ? r.getReviewerName() : "",
                        r.getComments() != null ? r.getComments() : "",
                        r.getCreatedAt() != null ? r.getCreatedAt().format(ISO_FMT) : "",
                        r.getReviewedAt() != null ? r.getReviewedAt().format(ISO_FMT) : ""
                );
            }
            printer.flush();
        } catch (Exception e) {
            log.error("Failed to generate review audit CSV export: ", e);
            throw new RuntimeException("Failed to generate review audit CSV report", e);
        }
        return sw.toString();
    }

    /**
     * 5. Audit Trail Report
     */
    @Transactional(readOnly = true)
    public String exportAuditReportCsv(String action, String entity, String user, String date) {
        return auditService.exportAuditLogsCsv(action, entity, user, date);
    }

    /**
     * 6. CPSE Inventory & Equivalence Breakdown Report
     */
    @Transactional(readOnly = true)
    public String exportCpseSummaryReportCsv() {
        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT.builder()
                .setHeader("CPSE Code", "Participating Enterprise Name", "Total Materials Ingested",
                        "Harmonized Items", "Pending Review Items", "Harmonization Coverage (%)")
                .build())) {

            Map<String, String> cpseNames = new LinkedHashMap<>();
            cpseNames.put("ONGC", "Oil and Natural Gas Corporation Limited");
            cpseNames.put("BHEL", "Bharat Heavy Electricals Limited");
            cpseNames.put("IOCL", "Indian Oil Corporation Limited");
            cpseNames.put("NTPC", "NTPC Limited");
            cpseNames.put("SAIL", "Steel Authority of India Limited");
            cpseNames.put("GAIL", "GAIL (India) Limited");

            for (Map.Entry<String, String> entry : cpseNames.entrySet()) {
                String code = entry.getKey();
                String name = entry.getValue();

                long total = sourceMaterialRepository.countByCpseNameIgnoreCase(code);
                long mapped = mappingRepository.countByCpseNameIgnoreCase(code);
                long pending = reviewRepository.countPendingBySourceMaterialCpse(code);
                double pct = total > 0 ? ((double) mapped / total) * 100.0 : 0.0;

                printer.printRecord(code, name, total, mapped, pending, String.format("%.1f%%", pct));
            }
            printer.flush();
        } catch (Exception e) {
            log.error("Failed to generate CPSE summary CSV export: ", e);
            throw new RuntimeException("Failed to generate CPSE summary CSV report", e);
        }
        return sw.toString();
    }
}
