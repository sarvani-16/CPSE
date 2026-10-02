package com.sih.material.service;

import com.sih.material.dto.BatchApproveRequest;
import com.sih.material.dto.BatchApproveResponse;
import com.sih.material.entity.CanonicalMaterial;
import com.sih.material.entity.MaterialMapping;
import com.sih.material.entity.Review;
import com.sih.material.entity.SourceMaterial;
import com.sih.material.exception.ResourceNotFoundException;
import com.sih.material.repository.CanonicalMaterialRepository;
import com.sih.material.repository.MaterialMappingRepository;
import com.sih.material.repository.ReviewRepository;
import com.sih.material.repository.SourceMaterialRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class ReviewService {

    private static final Logger log = LoggerFactory.getLogger(ReviewService.class);

    private final ReviewRepository reviewRepository;
    private final SourceMaterialRepository sourceMaterialRepository;
    private final CanonicalMaterialRepository canonicalRepository;
    private final MaterialMappingRepository mappingRepository;
    private final AuditService auditService;

    public ReviewService(ReviewRepository reviewRepository,
                         SourceMaterialRepository sourceMaterialRepository,
                         CanonicalMaterialRepository canonicalRepository,
                         MaterialMappingRepository mappingRepository,
                         AuditService auditService) {
        this.reviewRepository = reviewRepository;
        this.sourceMaterialRepository = sourceMaterialRepository;
        this.canonicalRepository = canonicalRepository;
        this.mappingRepository = mappingRepository;
        this.auditService = auditService;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getReviews(String status, int page, int pageSize) {
        Pageable pageable = PageRequest.of(Math.max(0, page - 1), Math.max(1, Math.min(100, pageSize)));
        boolean hasStatus = status != null && !status.trim().isEmpty() && !"ALL".equalsIgnoreCase(status.trim());
        Page<Review> reviewPage = hasStatus ? reviewRepository.searchReviews(status.trim(), pageable) : reviewRepository.findAll(pageable);

        Map<String, Object> result = new HashMap<>();
        result.put("total", reviewPage.getTotalElements());
        result.put("page", page);
        result.put("page_size", pageSize);
        result.put("total_pages", reviewPage.getTotalPages());
        result.put("items", reviewPage.getContent());
        return result;
    }

    @Transactional
    public Map<String, Object> approveReview(Long id, String reviewerName, String comment) {
        Review review = reviewRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Review item not found with id: " + id));

        SourceMaterial source = sourceMaterialRepository.findById(review.getSourceMaterialId())
                .orElseThrow(() -> new ResourceNotFoundException("Source material not found with id: " + review.getSourceMaterialId()));

        CanonicalMaterial canonical = canonicalRepository.findByCanonicalCode(review.getSuggestedCanonicalCode())
                .or(() -> canonicalRepository.findByNationalMaterialCode(review.getSuggestedCanonicalCode()))
                .orElseThrow(() -> new ResourceNotFoundException("Canonical material not found: " + review.getSuggestedCanonicalCode()));

        String effectiveReviewer = reviewerName != null && !reviewerName.isBlank() ? reviewerName : "Govt Reviewer";
        String effectiveComment = comment != null ? comment : "Approved by human reviewer";

        // Update Review
        review.setStatus("APPROVED");
        review.setReviewerName(effectiveReviewer);
        review.setComments(effectiveComment);
        review.setReviewedAt(LocalDateTime.now());
        reviewRepository.save(review);

        // Create or update mapping
        MaterialMapping mapping = mappingRepository.findByCpseNameAndOriginalMaterialCode(source.getCpseName(), source.getMaterialCode())
                .orElse(new MaterialMapping());

        mapping.setSourceMaterialId(source.getId());
        mapping.setCpseName(source.getCpseName());
        mapping.setOriginalMaterialCode(source.getMaterialCode());
        mapping.setOriginalDescription(source.getDescription());
        mapping.setCanonicalMaterialCode(canonical.getCanonicalCode());
        mapping.setCanonicalDescription(canonical.getStandardizedDescription());
        mapping.setMatchStatus("APPROVED");
        mapping.setConfidence(review.getHybridScore() != null ? review.getHybridScore() : 1.0);
        mapping.setReviewer(effectiveReviewer);
        mapping.setTimestamp(LocalDateTime.now());
        mappingRepository.save(mapping);

        // Record Audit Event
        auditService.recordLog(
                "APPROVE_MATCH",
                "reviews",
                String.valueOf(id),
                "PENDING",
                "APPROVED",
                effectiveReviewer,
                effectiveComment,
                "{\"canonical_code\": \"" + canonical.getCanonicalCode() + "\", \"material_code\": \"" + source.getMaterialCode() + "\"}"
        );

        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "SUCCESS");
        resp.put("message", "Review approved and mapped successfully");
        resp.put("review_id", id);
        resp.put("canonical_code", canonical.getCanonicalCode());
        return resp;
    }

    @Transactional
    public Map<String, Object> rejectReview(Long id, String reviewerName, String comment) {
        Review review = reviewRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Review item not found with id: " + id));

        String effectiveReviewer = reviewerName != null && !reviewerName.isBlank() ? reviewerName : "Govt Reviewer";
        String effectiveComment = comment != null ? comment : "Rejected by human reviewer";

        review.setStatus("REJECTED");
        review.setReviewerName(effectiveReviewer);
        review.setComments(effectiveComment);
        review.setReviewedAt(LocalDateTime.now());
        reviewRepository.save(review);

        auditService.recordLog(
                "REJECT_MATCH",
                "reviews",
                String.valueOf(id),
                "PENDING",
                "REJECTED",
                effectiveReviewer,
                effectiveComment,
                null
        );

        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "SUCCESS");
        resp.put("message", "Review rejected");
        resp.put("review_id", id);
        return resp;
    }

    @Transactional
    public Map<String, Object> requestFurtherReview(Long id, String reviewerName, String comment) {
        Review review = reviewRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Review item not found with id: " + id));

        String effectiveReviewer = reviewerName != null && !reviewerName.isBlank() ? reviewerName : "Govt Reviewer";
        String effectiveComment = comment != null ? comment : "Flagged for technical committee evaluation";

        review.setStatus("NEEDS_REVIEW");
        review.setReviewerName(effectiveReviewer);
        review.setComments(effectiveComment);
        review.setReviewedAt(LocalDateTime.now());
        reviewRepository.save(review);

        auditService.recordLog(
                "NEEDS_REVIEW",
                "reviews",
                String.valueOf(id),
                "PENDING",
                "NEEDS_REVIEW",
                effectiveReviewer,
                effectiveComment,
                null
        );

        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "SUCCESS");
        resp.put("message", "Marked for committee review");
        resp.put("review_id", id);
        return resp;
    }

    @Transactional
    public BatchApproveResponse batchApprove(BatchApproveRequest req) {
        BatchApproveResponse response = new BatchApproveResponse();
        response.setTotalRequested(req.getReviewIds().size());

        List<Long> approvedIds = new ArrayList<>();
        List<Long> skippedIds = new ArrayList<>();
        List<String> reasons = new ArrayList<>();

        double minConfidence = req.getMinConfidence() != null ? req.getMinConfidence() : 0.80;

        for (Long rId : req.getReviewIds()) {
            Optional<Review> optReview = reviewRepository.findById(rId);
            if (optReview.isEmpty()) {
                skippedIds.add(rId);
                reasons.add("Review #" + rId + " not found");
                continue;
            }

            Review review = optReview.get();
            if ("APPROVED".equalsIgnoreCase(review.getStatus())) {
                skippedIds.add(rId);
                reasons.add("Review #" + rId + " already approved");
                continue;
            }

            // Guardrail: check technical conflicts
            if (review.getConflicts() != null && !review.getConflicts().isBlank() && !"[]".equals(review.getConflicts().trim())) {
                skippedIds.add(rId);
                reasons.add("Review #" + rId + " contains technical conflicts: " + review.getConflicts());
                continue;
            }

            // Check confidence threshold
            if (review.getHybridScore() != null && review.getHybridScore() < minConfidence) {
                skippedIds.add(rId);
                reasons.add("Review #" + rId + " score " + review.getHybridScore() + " is below threshold " + minConfidence);
                continue;
            }

            try {
                approveReview(rId, req.getReviewerName(), req.getComment());
                approvedIds.add(rId);
            } catch (Exception e) {
                skippedIds.add(rId);
                reasons.add("Review #" + rId + " error: " + e.getMessage());
            }
        }

        response.setApprovedCount(approvedIds.size());
        response.setSkippedCount(skippedIds.size());
        response.setApprovedIds(approvedIds);
        response.setSkippedIds(skippedIds);
        response.setReasons(reasons);

        return response;
    }
}
