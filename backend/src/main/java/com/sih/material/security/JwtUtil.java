package com.sih.material.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * JWT Utility for Generating, Signing, and Validating Enterprise Access Tokens.
 */
@Component
public class JwtUtil {

    private static final Logger log = LoggerFactory.getLogger(JwtUtil.class);

    // Default 256-bit signing key for local development
    private final Key key;
    private final long expirationMs;

    public JwtUtil(
            @Value("${jwt.secret:SIH26099EnterpriseSecureMaterialHarmonizationSecretKey2026_CPSE_National_Master}") String secret,
            @Value("${jwt.expiration-ms:86400000}") long expirationMs // 24 hours
    ) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes());
        this.expirationMs = expirationMs;
    }

    public String generateToken(Long userId, String employeeId, String name, String email, String role, String cpseName, boolean isActive) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("employeeId", employeeId);
        claims.put("name", name);
        claims.put("email", email);
        claims.put("role", role);
        claims.put("cpseName", cpseName != null ? cpseName : "CPSE_CONSORTIUM");
        claims.put("isActive", isActive);

        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expirationMs);

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(employeeId)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    public Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    public String extractEmployeeId(String token) {
        return extractAllClaims(token).getSubject();
    }

    public String extractRole(String token) {
        return (String) extractAllClaims(token).get("role");
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token);
            return true;
        } catch (SecurityException | MalformedJwtException e) {
            log.warn("Invalid JWT signature / token format: {}", e.getMessage());
        } catch (ExpiredJwtException e) {
            log.warn("Expired JWT token: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.warn("Unsupported JWT token: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.warn("JWT claims string is empty: {}", e.getMessage());
        }
        return false;
    }
}
