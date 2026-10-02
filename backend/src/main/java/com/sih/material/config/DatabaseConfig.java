package com.sih.material.config;

import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.sql.DataSource;
import java.net.URI;

/**
 * Enterprise Database Configuration:
 * Automatically detects and parses cloud PostgreSQL connection strings (Render / Heroku format)
 * such as postgres://user:pass@host:port/dbname into standard Spring Data JPA / HikariCP JDBC format.
 * If DATABASE_URL is not set, seamlessly falls back to standard Spring datasource properties.
 */
@Configuration
public class DatabaseConfig {

    private static final Logger log = LoggerFactory.getLogger(DatabaseConfig.class);

    @Bean
    @Primary
    public DataSource dataSource(DataSourceProperties properties) {
        String databaseUrl = System.getenv("DATABASE_URL");
        if (databaseUrl == null || databaseUrl.isBlank()) {
            databaseUrl = System.getenv("SPRING_DATASOURCE_URL");
        }

        if (databaseUrl != null && !databaseUrl.isBlank()) {
            String trimmed = databaseUrl.trim();
            if (trimmed.startsWith("postgres://") || trimmed.startsWith("postgresql://")) {
                try {
                    log.info("[DB] Configuring DataSource dynamically from cloud DATABASE_URL");
                    URI uri = new URI(trimmed);
                    String userInfo = uri.getUserInfo();
                    String username = properties.getUsername();
                    String password = properties.getPassword();

                    if (userInfo != null && userInfo.contains(":")) {
                        String[] parts = userInfo.split(":", 2);
                        username = parts[0];
                        password = parts[1];
                    }

                    String host = uri.getHost();
                    int port = uri.getPort() == -1 ? 5432 : uri.getPort();
                    String path = uri.getPath();
                    String dbName = (path != null && path.startsWith("/")) ? path.substring(1) : path;

                    String jdbcUrl = String.format("jdbc:postgresql://%s:%d/%s", host, port, dbName);
                    if (uri.getQuery() != null && !uri.getQuery().isBlank()) {
                        jdbcUrl += "?" + uri.getQuery();
                    }

                    HikariDataSource ds = new HikariDataSource();
                    ds.setDriverClassName("org.postgresql.Driver");
                    ds.setJdbcUrl(jdbcUrl);
                    if (username != null) ds.setUsername(username);
                    if (password != null) ds.setPassword(password);
                    return ds;
                } catch (Exception e) {
                    log.warn("[DB] Failed to parse DATABASE_URL as URI, falling back to standard configuration: {}", e.getMessage());
                }
            }
        }

        // Standard fallback to DataSourceProperties (application.yml, DB_HOST, DB_PORT, etc.)
        return properties.initializeDataSourceBuilder().type(HikariDataSource.class).build();
    }
}
