package models

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"time"

	
)

// JSONB is a custom type for handling JSONB columns in PostgreSQL
type JSONB map[string]interface{}

// Value implements the driver.Valuer interface for JSONB
func (j JSONB) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

// Scan implements the sql.Scanner interface for JSONB
func (j *JSONB) Scan(value interface{}) error {
	if value == nil {
		*j = nil
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("Scan source was not []byte")
	}
	return json.Unmarshal(bytes, &j)
}

// Task represents a scheduled or on-demand task
type Task struct {
	ID        string    `gorm:"primaryKey;type:varchar(255)" json:"id"`
	Name      string    `gorm:"type:varchar(255);not null" json:"name"`
	Type      string    `gorm:"type:varchar(50);not null" json:"type"`
	Script    string    `gorm:"type:varchar(500);not null" json:"script"`
	Schedule  string    `gorm:"type:varchar(100)" json:"schedule"`
	Args      JSONB     `gorm:"type:jsonb" json:"args"`
	Status    string    `gorm:"type:varchar(50);default:'created'" json:"status"`
	CreatedAt time.Time `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt time.Time `gorm:"autoUpdateTime" json:"updated_at"`
}

// Alert represents a system alert
type Alert struct {
	ID        string    `gorm:"primaryKey;type:varchar(255)" json:"id"`
	Type      string    `gorm:"type:varchar(50);not null" json:"type"`
	Message   string    `gorm:"type:text;not null" json:"message"`
	Severity  string    `gorm:"type:varchar(20);not null" json:"severity"`
	CreatedAt time.Time `gorm:"autoCreateTime" json:"created_at"`
}
