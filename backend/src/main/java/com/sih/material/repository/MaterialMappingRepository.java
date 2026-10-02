package com.sih.material.repository;

import com.sih.material.entity.MaterialMapping;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface MaterialMappingRepository extends JpaRepository<MaterialMapping, Long> {

    List<MaterialMapping> findByCanonicalMaterialCode(String canonicalCode);

    Optional<MaterialMapping> findByCpseNameAndOriginalMaterialCode(String cpseName, String originalCode);

    @Query("SELECT m FROM MaterialMapping m WHERE " +
           "(:cpseName IS NULL OR :cpseName = '' OR LOWER(m.cpseName) = LOWER(CAST(:cpseName AS string)))")
    Page<MaterialMapping> findByCpseFilter(@Param("cpseName") String cpseName, Pageable pageable);

    @Query("SELECT COUNT(DISTINCT m.sourceMaterialId) FROM MaterialMapping m")
    Long countDistinctMappedMaterials();

    long countByCpseNameIgnoreCase(String cpseName);
}
