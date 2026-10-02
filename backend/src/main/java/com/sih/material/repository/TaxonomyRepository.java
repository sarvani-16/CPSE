package com.sih.material.repository;

import com.sih.material.entity.Taxonomy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TaxonomyRepository extends JpaRepository<Taxonomy, Long> {

    Optional<Taxonomy> findByCodeIgnoreCase(String code);

    List<Taxonomy> findByParentCodeIgnoreCase(String parentCode);

    List<Taxonomy> findByLevelOrderByCodeAsc(Integer level);

    List<Taxonomy> findAllByOrderByLevelAscCodeAsc();
}
