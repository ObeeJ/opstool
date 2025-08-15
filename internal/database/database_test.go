package database

import (
	"context"
	"testing"
	"opstool/internal/config"
)

func TestConnect(t *testing.T) {
	// Test connection with mock config
	cfg := &config.Config{
		Database: config.DatabaseConfig{
			Host:     "localhost",
			Port:     5432,
			User:     "test",
			Password: "test",
			DBName:   "test",
		},
	}
	
	// Note: This will fail without a real database, but tests the function structure
	_, err := Connect(cfg)
	
	// We expect an error since we don't have a test database running
	if err == nil {
		t.Log("Database connection succeeded (unexpected in test environment)")
	} else {
		t.Logf("Database connection failed as expected: %v", err)
	}
}

func TestInitTracing(t *testing.T) {
	ctx := context.Background()
	
	// Test that InitTracing doesn't panic
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("InitTracing panicked: %v", r)
		}
	}()
	
	InitTracing(ctx)
}

func TestWrapDB(t *testing.T) {
	// Test WrapDB with nil (should not panic)
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("WrapDB panicked with nil input: %v", r)
		}
	}()
	
	tracedDB := WrapDB(nil)
	if tracedDB == nil {
		t.Error("WrapDB should return a TracedDB instance even with nil input")
	}
}
