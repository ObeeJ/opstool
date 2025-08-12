package audit

import (
	"database/sql"
	"encoding/json"
	"log"
	"time"
)

type AuditLogger struct {
	db *sql.DB
}

type AuditEntry struct {
	UserID       string                 `json:"user_id"`
	TenantID     string                 `json:"tenant_id"`
	Action       string                 `json:"action"`
	ResourceType string                 `json:"resource_type"`
	ResourceID   string                 `json:"resource_id"`
	Details      map[string]interface{} `json:"details"`
	IPAddress    string                 `json:"ip_address"`
	UserAgent    string                 `json:"user_agent"`
	Timestamp    time.Time              `json:"timestamp"`
}

func NewAuditLogger(db *sql.DB) *AuditLogger {
	return &AuditLogger{db: db}
}

func (a *AuditLogger) Log(entry AuditEntry) error {
	entry.Timestamp = time.Now()
	
	detailsJSON, err := json.Marshal(entry.Details)
	if err != nil {
		log.Printf("Failed to marshal audit details: %v", err)
		detailsJSON = []byte("{}")
	}
	
	query := `
		INSERT INTO audit_logs (user_id, tenant_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`
	
	_, err = a.db.Exec(query,
		entry.UserID, entry.TenantID, entry.Action, entry.ResourceType,
		entry.ResourceID, detailsJSON, entry.IPAddress, entry.UserAgent, entry.Timestamp)
	
	if err != nil {
		log.Printf("Failed to log audit entry: %v", err)
	}
	
	return err
}

func (a *AuditLogger) LogTaskCreation(userID, tenantID, taskID string, details map[string]interface{}) {
	a.Log(AuditEntry{
		UserID:       userID,
		TenantID:     tenantID,
		Action:       "task.create",
		ResourceType: "task",
		ResourceID:   taskID,
		Details:      details,
	})
}

func (a *AuditLogger) LogTaskExecution(userID, tenantID, taskID string, status string) {
	a.Log(AuditEntry{
		UserID:       userID,
		TenantID:     tenantID,
		Action:       "task.execute",
		ResourceType: "task",
		ResourceID:   taskID,
		Details:      map[string]interface{}{"status": status},
	})
}

func (a *AuditLogger) LogUserLogin(userID, tenantID, ipAddress, userAgent string) {
	a.Log(AuditEntry{
		UserID:       userID,
		TenantID:     tenantID,
		Action:       "user.login",
		ResourceType: "user",
		ResourceID:   userID,
		IPAddress:    ipAddress,
		UserAgent:    userAgent,
	})
}

func (a *AuditLogger) GetAuditTrail(tenantID string, limit int) ([]AuditEntry, error) {
	query := `
		SELECT user_id, tenant_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at
		FROM audit_logs 
		WHERE tenant_id = $1 
		ORDER BY created_at DESC 
		LIMIT $2`
	
	rows, err := a.db.Query(query, tenantID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var entries []AuditEntry
	for rows.Next() {
		var entry AuditEntry
		var detailsJSON []byte
		
		err := rows.Scan(&entry.UserID, &entry.TenantID, &entry.Action,
			&entry.ResourceType, &entry.ResourceID, &detailsJSON,
			&entry.IPAddress, &entry.UserAgent, &entry.Timestamp)
		if err != nil {
			continue
		}
		
		json.Unmarshal(detailsJSON, &entry.Details)
		entries = append(entries, entry)
	}
	
	return entries, nil
}