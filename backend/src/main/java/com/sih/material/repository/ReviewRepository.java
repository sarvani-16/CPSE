package com.sih.material.repository;

import com.sih.material.entity.Review;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    Page<Review> findByStatusIgnoreCase(String status, Pageable pageable);

    @Query("SELECT r FROM Review r WHERE " +
           "(:status IS NULL OR :status = '' OR :status = 'ALL' OR LOWER(r.status) = LOWER(CAST(:status AS string)))")
    Page<Review> searchReviews(@Param("status") String status, Pageable pageable);

    @Query("SELECT r.status, COUNT(r) FROM Review r GROUP BY r.status")
    List<Object[]> countByStatus();

    Long countByStatus(String status);

    long countByStatusIgnoreCase(String status);

    @Query("SELECT COUNT(r) FROM Review r WHERE r.conflicts IS NOT NULL AND TRIM(r.conflicts) != '' AND TRIM(r.conflicts) != '[]'")
    long countWithConflicts();

    @Query("SELECT COUNT(r) FROM Review r WHERE r.hybridScore >= :minScore")
    long countByHybridScoreGreaterThanEqual(@Param("minScore") Double minScore);

    List<Review> findTop10ByStatusIgnoreCaseOrderByCreatedAtDesc(String status);

    @Query("SELECT r FROM Review r WHERE UPPER(r.status) IN ('PENDING', 'NEEDS_REVIEW') ORDER BY r.hybridScore DESC, r.id DESC")
    List<Review> findPendingQueue(Pageable pageable);

    @Query("SELECT COUNT(r) FROM Review r WHERE r.sourceMaterialId IN (SELECT s.id FROM SourceMaterial s WHERE LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string)))")
    long countBySourceMaterialCpse(@Param("cpseName") String cpseName);

    @Query("SELECT COUNT(r) FROM Review r WHERE LOWER(r.status) = 'pending' AND r.sourceMaterialId IN (SELECT s.id FROM SourceMaterial s WHERE LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string)))")
    long countPendingBySourceMaterialCpse(@Param("cpseName") String cpseName);

    @Query("SELECT COUNT(r) FROM Review r WHERE (LOWER(r.status) = 'needs_review' OR (r.conflicts IS NOT NULL AND TRIM(r.conflicts) != '' AND TRIM(r.conflicts) != '[]')) AND r.sourceMaterialId IN (SELECT s.id FROM SourceMaterial s WHERE LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string)))")
    long countAttentionBySourceMaterialCpse(@Param("cpseName") String cpseName);

    @Query("SELECT r FROM Review r WHERE r.sourceMaterialId IN (SELECT s.id FROM SourceMaterial s WHERE LOWER(s.cpseName) = LOWER(CAST(:cpseName AS string))) ORDER BY r.createdAt DESC")
    List<Review> findTop10BySourceMaterialCpse(@Param("cpseName") String cpseName, Pageable pageable);
}
