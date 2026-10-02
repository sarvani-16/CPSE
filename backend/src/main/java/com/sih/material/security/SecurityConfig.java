package com.sih.material.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final JwtAuthenticationEntryPoint unauthorizedHandler;
    private final CustomAccessDeniedHandler accessDeniedHandler;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter,
                          JwtAuthenticationEntryPoint unauthorizedHandler,
                          CustomAccessDeniedHandler accessDeniedHandler) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
        this.unauthorizedHandler = unauthorizedHandler;
        this.accessDeniedHandler = accessDeniedHandler;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .cors(Customizer.withDefaults())
                .csrf(csrf -> csrf.disable())
                .exceptionHandling(exceptions -> exceptions
                        .authenticationEntryPoint(unauthorizedHandler)
                        .accessDeniedHandler(accessDeniedHandler)
                )
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                )
                .authorizeHttpRequests(auth -> auth
                        // 0. Preflight CORS OPTIONS requests
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()

                        // 1. Public Authentication & Health Endpoints
                        .requestMatchers("/api/auth/login", "/api/auth/register").permitAll()
                        .requestMatchers("/api/health").permitAll()
                        .requestMatchers("/swagger-ui/**", "/swagger-ui.html", "/v3/api-docs/**").permitAll()
                        .requestMatchers("/error").permitAll()

                        // 2. ADMIN ONLY Endpoints
                        .requestMatchers("/api/dashboard/admin").hasRole("ADMIN")
                        .requestMatchers("/api/users/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.POST, "/api/taxonomy/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.PUT, "/api/taxonomy/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.DELETE, "/api/taxonomy/**").hasRole("ADMIN")

                        // 3. REVIEWER & ADMIN Endpoints (Review approvals strictly forbidden for OFFICER)
                        .requestMatchers("/api/dashboard/reviewer").hasAnyRole("ADMIN", "REVIEWER")
                        .requestMatchers(HttpMethod.POST, "/api/reviews/**").hasAnyRole("ADMIN", "REVIEWER")
                        .requestMatchers(HttpMethod.PUT, "/api/reviews/**").hasAnyRole("ADMIN", "REVIEWER")
                        .requestMatchers("/api/audit-logs/**").hasAnyRole("ADMIN", "REVIEWER")

                        // 4. OFFICER & ADMIN Endpoints (Material submission and operational cataloging)
                        .requestMatchers("/api/dashboard/officer").hasAnyRole("ADMIN", "OFFICER")
                        .requestMatchers(HttpMethod.POST, "/api/materials/upload").hasAnyRole("ADMIN", "OFFICER")

                        // 5. Shared Authenticated Endpoints (All valid roles)
                        .requestMatchers("/api/dashboard/overview").authenticated()
                        .requestMatchers("/api/materials/**").authenticated()
                        .requestMatchers("/api/matching/**").authenticated()
                        .requestMatchers("/api/canonical-materials/**").authenticated()
                        .requestMatchers("/api/reviews").authenticated()
                        .requestMatchers("/api/auth/me", "/api/auth/logout").authenticated()
                        .requestMatchers("/api/reports/**").authenticated()

                        // Any other request must be authenticated
                        .anyRequest().authenticated()
                );

        http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
