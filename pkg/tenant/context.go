package tenant

import (
	"context"
	"database/sql"
	"encoding/json"
)

type TenantContext struct {
	ID       string                 `json:"id"`
	Name     string                 `json:"name"`
	Slug     string                 `json:"slug"`
	Settings map[string]interface{} `json:"settings"`
	UserID   string                 `json:"user_id"`
	Role     string                 `json:"role"`
}

type TenantManager struct {
	db *sql.DB
}

func NewTenantManager(db *sql.DB) *TenantManager {
	return &TenantManager{db: db}
}

func (tm *TenantManager) GetTenant(tenantID string) (*TenantContext, error) {
	query := `SELECT id, name, slug, settings FROM tenants WHERE id = $1`
	
	var tenant TenantContext
	var settingsJSON []byte
	
	err := tm.db.QueryRow(query, tenantID).Scan(
		&tenant.ID, &tenant.Name, &tenant.Slug, &settingsJSON)
	if err != nil {
		return nil, err
	}
	
	json.Unmarshal(settingsJSON, &tenant.Settings)
	return &tenant, nil
}

func (tm *TenantManager) CreateTenant(name, slug string, settings map[string]interface{}) (*TenantContext, error) {
	settingsJSON, _ := json.Marshal(settings)
	
	query := `INSERT INTO tenants (name, slug, settings) VALUES ($1, $2, $3) RETURNING id`
	
	var tenantID string
	err := tm.db.QueryRow(query, name, slug, settingsJSON).Scan(&tenantID)
	if err != nil {
		return nil, err
	}
	
	return &TenantContext{
		ID:       tenantID,
		Name:     name,
		Slug:     slug,
		Settings: settings,
	}, nil
}

func (tm *TenantManager) ValidateAccess(userID, tenantID string) bool {
	query := `SELECT COUNT(*) FROM users WHERE id = $1 AND tenant_id = $2 AND is_active = true`
	
	var count int
	tm.db.QueryRow(query, userID, tenantID).Scan(&count)
	return count > 0
}

func WithTenantContext(ctx context.Context, tenant *TenantContext) context.Context {
	return context.WithValue(ctx, "tenant", tenant)
}

func GetTenantContext(ctx context.Context) *TenantContext {
	if tenant, ok := ctx.Value("tenant").(*TenantContext); ok {
		return tenant
	}
	return nil
}

func (tm *TenantManager) GetUserTenants(userID string) ([]*TenantContext, error) {
	query := `
		SELECT t.id, t.name, t.slug, t.settings 
		FROM tenants t 
		JOIN users u ON u.tenant_id = t.id 
		WHERE u.id = $1 AND u.is_active = true`
	
	rows, err := tm.db.Query(query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var tenants []*TenantContext
	for rows.Next() {
		var tenant TenantContext
		var settingsJSON []byte
		
		err := rows.Scan(&tenant.ID, &tenant.Name, &tenant.Slug, &settingsJSON)
		if err != nil {
			continue
		}
		
		json.Unmarshal(settingsJSON, &tenant.Settings)
		tenants = append(tenants, &tenant)
	}
	
	return tenants, nil
}