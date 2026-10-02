package com.sih.material.repository;

import com.sih.material.entity.CanonicalMaterial;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CanonicalMaterialRepository extends JpaRepository<CanonicalMaterial, Long> {

    Optional<CanonicalMaterial> findByNationalMaterialCode(String code);

    Optional<CanonicalMaterial> findByCanonicalCode(String code);

    @Query("SELECT c FROM CanonicalMaterial c WHERE " +
           "(:category IS NULL OR :category = '' OR LOWER(COALESCE(c.category, '')) = LOWER(CAST(:category AS string))) AND " +
           "(:status IS NULL OR :status = '' OR LOWER(c.approvalStatus) = LOWER(CAST(:status AS string))) AND " +
           "(:search IS NULL OR :search = '' OR " +
           "LOWER(c.nationalMaterialCode) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(c.standardizedDescription) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(COALESCE(c.standardSpecification, '')) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')))")
    Page<CanonicalMaterial> searchCanonical(
            @Param("search") String search,
            @Param("category") String category,
            @Param("status") String status,
            Pageable pageable
    );

    @Query("SELECT COALESCE(c.category, 'Uncategorized'), COUNT(c) FROM CanonicalMaterial c GROUP BY c.category")
    List<Object[]> countByCategory();

    @Query("SELECT MAX(c.id) FROM CanonicalMaterial c")
    Long getMaxId();
}
