package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class CompareResponse {

    @JsonProperty("title_a")
    private String titleA;

    @JsonProperty("title_b")
    private String titleB;

    @JsonProperty("match_decision")
    private String matchDecision; // MATCH, REVIEW, NOT_MATCH

    @JsonProperty("hybrid_score")
    private Double hybridScore;

    @JsonProperty("semantic_score")
    private Double semanticScore;

    @JsonProperty("lexical_score")
    private Double lexicalScore;

    @JsonProperty("fuzzy_score")
    private Double fuzzyScore;

    @JsonProperty("explanation")
    private List<String> explanation;

    @JsonProperty("technical_tokens")
    private Map<String, Object> technicalTokens;

    @JsonProperty("sub_scores")
    private Map<String, Double> subScores;

    @JsonProperty("weights")
    private Map<String, Double> weights;

    public CompareResponse() {}

    public String getTitleA() { return titleA; }
    public void setTitleA(String titleA) { this.titleA = titleA; }

    public String getTitleB() { return titleB; }
    public void setTitleB(String titleB) { this.titleB = titleB; }

    public String getMatchDecision() { return matchDecision; }
    public void setMatchDecision(String matchDecision) { this.matchDecision = matchDecision; }

    public Double getHybridScore() { return hybridScore; }
    public void setHybridScore(Double hybridScore) { this.hybridScore = hybridScore; }

    public Double getSemanticScore() { return semanticScore; }
    public void setSemanticScore(Double semanticScore) { this.semanticScore = semanticScore; }

    public Double getLexicalScore() { return lexicalScore; }
    public void setLexicalScore(Double lexicalScore) { this.lexicalScore = lexicalScore; }

    public Double getFuzzyScore() { return fuzzyScore; }
    public void setFuzzyScore(Double fuzzyScore) { this.fuzzyScore = fuzzyScore; }

    public List<String> getExplanation() { return explanation; }
    public void setExplanation(List<String> explanation) { this.explanation = explanation; }

    public Map<String, Object> getTechnicalTokens() { return technicalTokens; }
    public void setTechnicalTokens(Map<String, Object> technicalTokens) { this.technicalTokens = technicalTokens; }

    public Map<String, Double> getSubScores() { return subScores; }
    public void setSubScores(Map<String, Double> subScores) { this.subScores = subScores; }

    public Map<String, Double> getWeights() { return weights; }
    public void setWeights(Map<String, Double> weights) { this.weights = weights; }
}
