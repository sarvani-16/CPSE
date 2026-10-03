# Multi-stage Dockerfile for SIH26099 Spring Boot Backend
# Stage 1: Build stage with Maven and OpenJDK 17
FROM maven:3.9.9-eclipse-temurin-17-alpine AS builder
WORKDIR /workspace

# Copy Maven descriptor
COPY pom.xml .

# Pre-fetch dependencies for efficient Docker layer caching
RUN mvn dependency:go-offline -B || true

# Copy application source code and compile production jar
COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Lightweight Production Runtime (Eclipse Temurin JRE 17 Alpine)
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Create non-root application user for enterprise container security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Copy built Spring Boot executable jar from builder stage
COPY --from=builder /workspace/target/*.jar /app/app.jar

# Default port for local container testing; overridden by Render's $PORT at runtime
ENV PORT=8080
EXPOSE ${PORT}

# Production JVM tuning for Render 512MB Free Tier (prevents OOM SIGKILL restarts)
ENV JAVA_OPTS="-Xmx320m -Xms128m -XX:+UseG1GC -XX:+ExitOnOutOfMemoryError -XX:MaxMetaspaceSize=128m"

# Dynamic port binding: Render injects $PORT, Spring Boot binds 0.0.0.0:$PORT
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Dserver.port=${PORT:-8080} -Dserver.address=0.0.0.0 -Djava.security.egd=file:/dev/./urandom -jar /app/app.jar"]
