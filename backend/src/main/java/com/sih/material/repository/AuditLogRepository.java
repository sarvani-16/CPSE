package com.sih.material.repository;

import com.sih.material.entity.AuditLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {

    @Query("SELECT a FROM AuditLog a WHERE " +
           "(:action IS NULL OR :action = '' OR LOWER(a.action) = LOWER(CAST(:action AS string))) AND " +
           "(:entity IS NULL OR :entity = '' OR LOWER(a.entityType) LIKE LOWER(CONCAT('%', CAST(:entity AS string), '%')) OR LOWER(COALESCE(a.entityId, '')) LIKE LOWER(CONCAT('%', CAST(:entity AS string), '%'))) AND " +
           "(:user IS NULL OR :user = '' OR LOWER(a.performedBy) LIKE LOWER(CONCAT('%', CAST(:user AS string), '%')) OR LOWER(COALESCE(a.user, '')) LIKE LOWER(CONCAT('%', CAST(:user AS string), '%'))) AND " +
           "(:startDate IS NULL OR a.timestamp >= :startDate) AND " +
           "(:endDate IS NULL OR a.timestamp <= :endDate) " +
           "ORDER BY a.timestamp DESC")
    Page<AuditLog> findWithFilters(
            @Param("action") String action,
            @Param("entity") String entity,
            @Param("user") String user,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            Pageable pageable
    );

    @Query("SELECT DISTINCT a.action FROM AuditLog a WHERE a.action IS NOT NULL ORDER BY a.action")
    List<String> findDistinctActions();

    @Query("SELECT DISTINCT a.entityType FROM AuditLog a WHERE a.entityType IS NOT NULL ORDER BY a.entityType")
    List<String> findDistinctEntities();

    @Query("SELECT DISTINCT a.performedBy FROM AuditLog a WHERE a.performedBy IS NOT NULL ORDER BY a.performedBy")
    List<String> findDistinctUsers();

    List<AuditLog> findTop10ByOrderByTimestampDesc();

    @Query("SELECT a FROM AuditLog a WHERE " +
           "LOWER(a.performedBy) LIKE LOWER(CONCAT('%', CAST(:user AS string), '%')) OR " +
           "LOWER(COALESCE(a.entityId, '')) LIKE LOWER(CONCAT('%', CAST(:user AS string), '%')) OR " +
           "LOWER(COALESCE(a.details, '')) LIKE LOWER(CONCAT('%', CAST(:cpse AS string), '%')) OR " +
           "LOWER(COALESCE(a.newValue, '')) LIKE LOWER(CONCAT('%', CAST(:cpse AS string), '%')) " +
           "ORDER BY a.timestamp DESC")
    List<AuditLog> findRecentActivityForUserOrCpse(@Param("user") String user, @Param("cpse") String cpse, Pageable pageable);
}
