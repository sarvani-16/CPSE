package com.sih.material.controller;

import com.sih.material.service.JobService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/jobs")
@Tag(name = "Processing Jobs Management", description = "Real-time tracking of ingestion and normalization pipeline jobs")
public class JobController {

    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    @GetMapping("/{jobId}")
    @Operation(summary = "Get Status of Specific Ingestion Job")
    public ResponseEntity<Map<String, Object>> getJobStatus(@PathVariable("jobId") String jobId) {
        return ResponseEntity.ok(jobService.getJob(jobId));
    }

    @GetMapping
    @Operation(summary = "List Recent Processing and Ingestion Jobs")
    public ResponseEntity<List<Map<String, Object>>> listJobs() {
        return ResponseEntity.ok(jobService.listRecentJobs());
    }
}
