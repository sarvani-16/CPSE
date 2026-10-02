package com.sih.material.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.sih.material.entity.AuditLog;
import java.util.List;

public class AuditLogsResponse {

    private long total;
    private int page;

    @JsonProperty("page_size")
    private int pageSize;

    @JsonProperty("total_pages")
    private int totalPages;

    private List<AuditLog> items;

    @JsonProperty("available_actions")
    private List<String> availableActions;

    @JsonProperty("available_entities")
    private List<String> availableEntities;

    @JsonProperty("available_users")
    private List<String> availableUsers;

    public AuditLogsResponse() {}

    public long getTotal() { return total; }
    public void setTotal(long total) { this.total = total; }

    public int getPage() { return page; }
    public void setPage(int page) { this.page = page; }

    public int getPageSize() { return pageSize; }
    public void setPageSize(int pageSize) { this.pageSize = pageSize; }

    public int getTotalPages() { return totalPages; }
    public void setTotalPages(int totalPages) { this.totalPages = totalPages; }

    public List<AuditLog> getItems() { return items; }
    public void setItems(List<AuditLog> items) { this.items = items; }

    public List<String> getAvailableActions() { return availableActions; }
    public void setAvailableActions(List<String> availableActions) { this.availableActions = availableActions; }

    public List<String> getAvailableEntities() { return availableEntities; }
    public void setAvailableEntities(List<String> availableEntities) { this.availableEntities = availableEntities; }

    public List<String> getAvailableUsers() { return availableUsers; }
    public void setAvailableUsers(List<String> availableUsers) { this.availableUsers = availableUsers; }
}
