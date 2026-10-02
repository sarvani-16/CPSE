package com.sih.material.controller;

import com.sih.material.dto.BatchApproveRequest;
import com.sih.material.dto.BatchApproveResponse;
import com.sih.material.dto.ReviewActionRequest;
import com.sih.material.service.ReviewService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/reviews")
@Tag(name = "Human-in-the-Loop Review Center", description = "Review and resolution of AI suggested material matches")
public class ReviewController {

    private final ReviewService reviewService;

    public ReviewController(ReviewService reviewService) {
        this.reviewService = reviewService;
    }

    @GetMapping
    @Operation(summary = "Get Paginated Candidate Reviews")
    public ResponseEntity<Map<String, Object>> getReviews(
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "page", defaultValue = "1") int page,
            @RequestParam(value = "page_size", defaultValue = "20") int pageSize
    ) {
        return ResponseEntity.ok(reviewService.getReviews(status, page, pageSize));
    }

    @PostMapping("/{id}/approve")
    @Operation(summary = "Approve Candidate Match")
    public ResponseEntity<Map<String, Object>> approveReview(
            @PathVariable("id") Long id,
            @RequestBody(required = false) ReviewActionRequest request
    ) {
        String reviewer = request != null ? request.getReviewerName() : "Govt Reviewer";
        String comment = request != null ? request.getComment() : null;
        return ResponseEntity.ok(reviewService.approveReview(id, reviewer, comment));
    }

    @PostMapping("/{id}/reject")
    @Operation(summary = "Reject Candidate Match")
    public ResponseEntity<Map<String, Object>> rejectReview(
            @PathVariable("id") Long id,
            @RequestBody(required = false) ReviewActionRequest request
    ) {
        String reviewer = request != null ? request.getReviewerName() : "Govt Reviewer";
        String comment = request != null ? request.getComment() : null;
        return ResponseEntity.ok(reviewService.rejectReview(id, reviewer, comment));
    }

    @PostMapping("/{id}/request-review")
    @Operation(summary = "Mark Review as Needs Committee Review")
    public ResponseEntity<Map<String, Object>> requestFurtherReview(
            @PathVariable("id") Long id,
            @RequestBody(required = false) ReviewActionRequest request
    ) {
        String reviewer = request != null ? request.getReviewerName() : "Govt Reviewer";
        String comment = request != null ? request.getComment() : null;
        return ResponseEntity.ok(reviewService.requestFurtherReview(id, reviewer, comment));
    }

    @PostMapping("/batch-approve")
    @Operation(summary = "Batch Approve Multiple Candidate Matches")
    public ResponseEntity<BatchApproveResponse> batchApprove(
            @Valid @RequestBody BatchApproveRequest request
    ) {
        return ResponseEntity.ok(reviewService.batchApprove(request));
    }
}
