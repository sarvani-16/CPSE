package com.sih.material.repository;

import com.sih.material.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmployeeIdIgnoreCase(String employeeId);

    Optional<User> findByEmailIgnoreCase(String email);

    @Query("SELECT u FROM User u WHERE " +
           "LOWER(u.employeeId) = LOWER(CAST(:identifier AS string)) OR LOWER(u.email) = LOWER(CAST(:identifier AS string))")
    Optional<User> findByEmployeeIdOrEmail(@Param("identifier") String identifier);

    boolean existsByEmployeeIdIgnoreCase(String employeeId);

    boolean existsByEmailIgnoreCase(String email);

    @Query("SELECT u FROM User u WHERE " +
           "(:role IS NULL OR :role = '' OR LOWER(u.role) = LOWER(CAST(:role AS string))) AND " +
           "(:search IS NULL OR :search = '' OR " +
           "LOWER(u.name) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(u.employeeId) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(u.email) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')) OR " +
           "LOWER(COALESCE(u.cpseName, '')) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%')))")
    Page<User> searchUsers(@Param("role") String role, @Param("search") String search, Pageable pageable);

    long countByIsActiveTrue();
}
