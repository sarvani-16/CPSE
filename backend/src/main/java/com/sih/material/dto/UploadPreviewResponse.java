package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class UploadPreviewResponse {

    private String filename;

    @JsonProperty("file_type")
    private String fileType;

    @JsonProperty("total_rows_detected")
    private int totalRowsDetected;

    @JsonProperty("detected_columns")
    private List<String> detectedColumns;

    @JsonProperty("suggested_mappings")
    private Map<String, String> suggestedMappings;

    @JsonProperty("unmapped_columns")
    private List<String> unmappedColumns;

    @JsonProperty("missing_required_fields")
    private List<String> missingRequiredFields;

    @JsonProperty("preview_rows")
    private List<Map<String, Object>> previewRows;

    @JsonProperty("is_valid")
    private boolean isValid;

    @JsonProperty("validation_message")
    private String validationMessage;

    public UploadPreviewResponse() {}

    public String getFilename() { return filename; }
    public void setFilename(String filename) { this.filename = filename; }

    public String getFileType() { return fileType; }
    public void setFileType(String fileType) { this.fileType = fileType; }

    public int getTotalRowsDetected() { return totalRowsDetected; }
    public void setTotalRowsDetected(int totalRowsDetected) { this.totalRowsDetected = totalRowsDetected; }

    public List<String> getDetectedColumns() { return detectedColumns; }
    public void setDetectedColumns(List<String> detectedColumns) { this.detectedColumns = detectedColumns; }

    public Map<String, String> getSuggestedMappings() { return suggestedMappings; }
    public void setSuggestedMappings(Map<String, String> suggestedMappings) { this.suggestedMappings = suggestedMappings; }

    public List<String> getUnmappedColumns() { return unmappedColumns; }
    public void setUnmappedColumns(List<String> unmappedColumns) { this.unmappedColumns = unmappedColumns; }

    public List<String> getMissingRequiredFields() { return missingRequiredFields; }
    public void setMissingRequiredFields(List<String> missingRequiredFields) { this.missingRequiredFields = missingRequiredFields; }

    public List<Map<String, Object>> getPreviewRows() { return previewRows; }
    public void setPreviewRows(List<Map<String, Object>> previewRows) { this.previewRows = previewRows; }

    public boolean isValid() { return isValid; }
    public void setValid(boolean valid) { isValid = valid; }

    public String getValidationMessage() { return validationMessage; }
    public void setValidationMessage(String validationMessage) { this.validationMessage = validationMessage; }
}
