package com.sih.material.service;

import com.sih.material.dto.AuditLogsResponse;
import com.sih.material.entity.AuditLog;
import com.sih.material.repository.AuditLogRepository;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.StringWriter;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.regex.Pattern;

/**
 * Enterprise Audit Service:
 * Provides immutable data governance logging for all CPSE material master lifecycle events.
 * GUARANTEES: Secrets, passwords, JWT tokens, and private keys are NEVER persisted.
 */
@Service
public class AuditService {

    private static final Logger log = LoggerFactory.getLogger(AuditService.class);

    private static final Pattern SENSITIVE_PATTERN = Pattern.compile(
            "(?i)\\b(pass(word)?|token|secret|api[_-]?key|bearer|credential|private[_-]?key|cookie|auth(orization)?)\\b\\s*[:=]\\s*[\"']?[^\"'\\s,;{}]+[\"']?"
    );

    private static final Pattern BEARER_PATTERN = Pattern.compile(
            "(?i)\\bBearer\\s+[a-zA-Z0-9_\\-\\.]+"
    );

    private final AuditLogRepository auditLogRepository;

    public AuditService(AuditLogRepository auditLogRepository) {
        this.auditLogRepository = auditLogRepository;
    }

    /**
     * Sanitizes strings by replacing confidential tokens with [REDACTED_CONFIDENTIAL].
     */
    public String sanitize(String input) {
        if (input == null || input.isBlank()) {
            return input;
        }
        String sanitized = SENSITIVE_PATTERN.matcher(input).replaceAll("$1=[REDACTED_CONFIDENTIAL]");
        sanitized = BEARER_PATTERN.matcher(sanitized).replaceAll("Bearer [REDACTED_CONFIDENTIAL]");
        return sanitized;
    }

    @Transactional
    public AuditLog recordLog(String action, String entityType, String entityId,
                              String oldValue, String newValue, String performedBy,
                              String reason, String details) {
        AuditLog entry = new AuditLog();
        entry.setAction(action != null ? action.trim() : "UNKNOWN_ACTION");
        entry.setEntityType(entityType != null ? entityType.trim() : "SYSTEM");
        entry.setEntityId(entityId);
        entry.setOldValue(sanitize(oldValue));
        entry.setNewValue(sanitize(newValue));
        entry.setPerformedBy(performedBy != null && !performedBy.isBlank() ? performedBy.trim() : "SYSTEM");
        entry.setReason(sanitize(reason));
        entry.setDetails(sanitize(details));
        entry.setUser(entry.getPerformedBy());
        entry.setTimestamp(LocalDateTime.now());

        log.debug("Recording audit event: action={}, entity={}/{}", entry.getAction(), entry.getEntityType(), entry.getEntityId());
        return auditLogRepository.save(entry);
    }

    @Transactional(readOnly = true)
    public AuditLogsResponse getAuditLogs(String action, String entity, String user, String date, int page, int pageSize) {
        LocalDateTime startDate = null;
        LocalDateTime endDate = null;
        if (date != null && !date.isBlank()) {
            try {
                LocalDate d = LocalDate.parse(date.trim());
                startDate = d.atStartOfDay();
                endDate = d.plusDays(1).atStartOfDay();
            } catch (Exception e) {
                log.warn("Invalid date filter format: {}", date);
            }
        }

        Pageable pageable = PageRequest.of(Math.max(0, page - 1), Math.max(1, Math.min(10000, pageSize)));
        boolean hasAction = action != null && !action.isBlank() && !"ALL".equalsIgnoreCase(action.trim());
        boolean hasEntity = entity != null && !entity.isBlank() && !"ALL".equalsIgnoreCase(entity.trim());
        boolean hasUser = user != null && !user.isBlank();
        boolean hasDate = startDate != null;

        Page<AuditLog> logPage;
        if (!hasAction && !hasEntity && !hasUser && !hasDate) {
            logPage = auditLogRepository.findAll(PageRequest.of(pageable.getPageNumber(), pageable.getPageSize(), org.springframework.data.domain.Sort.by(org.springframework.data.domain.Sort.Direction.DESC, "timestamp")));
        } else {
            logPage = auditLogRepository.findWithFilters(
                    hasAction ? action.trim() : null,
                    hasEntity ? entity.trim() : null,
                    hasUser ? user.trim() : null,
                    startDate,
                    endDate,
                    pageable
            );
        }

        AuditLogsResponse response = new AuditLogsResponse();
        response.setTotal(logPage.getTotalElements());
        response.setPage(page);
        response.setPageSize(pageSize);
        response.setTotalPages(logPage.getTotalPages());
        response.setItems(logPage.getContent());
        response.setAvailableActions(auditLogRepository.findDistinctActions());
        response.setAvailableEntities(auditLogRepository.findDistinctEntities());
        response.setAvailableUsers(auditLogRepository.findDistinctUsers());

        return response;
    }

    @Transactional(readOnly = true)
    public String exportAuditLogsCsv(String action, String entity, String user, String date) {
        AuditLogsResponse logs = getAuditLogs(action, entity, user, date, 1, 5000);

        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT.builder()
                .setHeader("id", "action", "entity_type", "entity_id", "old_value", "new_value", "performed_by", "timestamp", "reason")
                .build())) {

            for (AuditLog l : logs.getItems()) {
                printer.printRecord(
                        l.getId(),
                        l.getAction(),
                        l.getEntityType(),
                        l.getEntityId() != null ? l.getEntityId() : "",
                        l.getOldValue() != null ? l.getOldValue() : "",
                        l.getNewValue() != null ? l.getNewValue() : "",
                        l.getPerformedBy(),
                        l.getTimestamp() != null ? l.getTimestamp().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) : "",
                        l.getReason() != null ? l.getReason() : ""
                );
            }
            printer.flush();
        } catch (Exception e) {
            log.error("Failed to generate audit CSV export: ", e);
            throw new RuntimeException("Failed to generate audit CSV export", e);
        }

        return sw.toString();
    }
}
