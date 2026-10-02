package com.sih.material.repository;

import com.sih.material.entity.SourceMaterial;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface SourceMaterialRepository extends JpaRepository<SourceMaterial, Long> {

    Optional<SourceMaterial> findByCpseNameAndMaterialCode(String cpseName, String materialCode);

    Optional<SourceMaterial> findByUserIdAndCpseNameAndMaterialCode(Long userId, String cpseName, String materialCode);

    Optional<SourceMaterial> findByIdAndUserId(Long id, Long userId);

    Page<SourceMaterial> findByCpseNameIgnoreCase(String cpseName, Pageable pageable);

    Page<SourceMaterial> findByUserId(Long userId, Pageable pageable);

    @Query("SELECT s FROM SourceMaterial s WHERE " +
           "(:cpseName IS NULL OR :cpseName = '' OR LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string))) AND " +
           "(:search IS NULL OR :search = '' OR " +
           "LOWER(s.materialCode) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(s.description) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(COALESCE(s.materialGrade, '')) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')))")
    Page<SourceMaterial> searchMaterials(
            @Param("cpseName") String cpseName,
            @Param("search") String search,
            Pageable pageable
    );

    @Query("SELECT s FROM SourceMaterial s WHERE " +
           "s.userId = :userId AND " +
           "(:cpseName IS NULL OR :cpseName = '' OR LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string))) AND " +
           "(:search IS NULL OR :search = '' OR " +
           "LOWER(s.materialCode) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(s.description) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(COALESCE(s.materialGrade, '')) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')))")
    Page<SourceMaterial> searchMaterialsForUser(
            @Param("userId") Long userId,
            @Param("cpseName") String cpseName,
            @Param("search") String search,
            Pageable pageable
    );

    @Query("SELECT s FROM SourceMaterial s WHERE " +
           "s.userId = :userId AND " +
           "(:cpseName IS NULL OR :cpseName = '' OR LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string))) AND " +
           "(:search IS NULL OR :search = '' OR " +
           "LOWER(s.materialCode) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(s.description) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(COALESCE(s.materialGrade, '')) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')))")
    List<SourceMaterial> findForExportUser(
            @Param("userId") Long userId,
            @Param("cpseName") String cpseName,
            @Param("search") String search,
            org.springframework.data.domain.Sort sort
    );

    @Query("SELECT s.cpseName, COUNT(s) FROM SourceMaterial s GROUP BY s.cpseName")
    List<Object[]> countByCpse();

    long countByCpseNameIgnoreCase(String cpseName);

    long countByUserId(Long userId);

    @Query("SELECT COUNT(s) FROM SourceMaterial s WHERE s.userId = :userId AND s.createdAt >= :since")
    long countByUserIdAndCreatedAtAfter(@Param("userId") Long userId, @Param("since") LocalDateTime since);

    @Query("SELECT COUNT(s) FROM SourceMaterial s WHERE LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string)) AND s.createdAt >= :since")
    long countByCpseNameAndCreatedAtAfter(@Param("cpseName") String cpseName, @Param("since") LocalDateTime since);

    List<SourceMaterial> findTop10ByUserIdOrderByCreatedAtDesc(Long userId);

    List<SourceMaterial> findTop10ByCpseNameIgnoreCaseOrderByCreatedAtDesc(String cpseName);

    List<SourceMaterial> findTop10ByOrderByCreatedAtDesc();
}
