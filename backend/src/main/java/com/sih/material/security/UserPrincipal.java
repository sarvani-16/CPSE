package com.sih.material.security;

import com.sih.material.entity.User;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Collections;

public class UserPrincipal implements UserDetails {

    private final Long id;
    private final String employeeId;
    private final String name;
    private final String email;
    private final String password;
    private final String role;
    private final String cpseName;
    private final boolean active;
    private final Collection<? extends GrantedAuthority> authorities;

    public UserPrincipal(Long id, String employeeId, String name, String email, String password,
                         String role, String cpseName, boolean active) {
        this.id = id;
        this.employeeId = employeeId;
        this.name = name;
        this.email = email;
        this.password = password;
        this.role = role;
        this.cpseName = cpseName;
        this.active = active;
        // Prefix with ROLE_ for Spring Security hasRole() matchers
        String roleWithPrefix = role.startsWith("ROLE_") ? role : "ROLE_" + role.toUpperCase();
        this.authorities = Collections.singletonList(new SimpleGrantedAuthority(roleWithPrefix));
    }

    public static UserPrincipal create(User user) {
        return new UserPrincipal(
                user.getId(),
                user.getEmployeeId(),
                user.getName(),
                user.getEmail(),
                user.getPasswordHash(),
                user.getRole(),
                user.getCpseName(),
                Boolean.TRUE.equals(user.getIsActive())
        );
    }

    public Long getId() { return id; }
    public String getEmployeeId() { return employeeId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getRole() { return role; }
    public String getCpseName() { return cpseName; }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() { return authorities; }

    @Override
    public String getPassword() { return password; }

    @Override
    public String getUsername() { return employeeId; }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return active; }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return active; }
}
