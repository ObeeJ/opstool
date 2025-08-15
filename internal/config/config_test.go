package config

import (
	"os"
	"testing"
)

func TestLoadConfig(t *testing.T) {
	// Test default config loading
	cfg := Load()
	
	if cfg == nil {
		t.Fatal("Config should not be nil")
	}
	
	// Test default values
	if cfg.Server.Port == "" {
		t.Error("Server port should have a default value")
	}
	
	if cfg.Database.Host == "" {
		t.Error("Database host should have a default value")
	}
}

func TestLoadConfigWithEnvironmentVariables(t *testing.T) {
	// Set environment variables
	os.Setenv("DB_HOST", "test-host")
	os.Setenv("REDIS_HOST", "test-redis")
	defer func() {
		os.Unsetenv("DB_HOST")
		os.Unsetenv("REDIS_HOST")
	}()
	
	cfg := Load()
	
	if cfg.Database.Host != "test-host" {
		t.Errorf("Expected DB_HOST to be 'test-host', got '%s'", cfg.Database.Host)
	}
	
	if cfg.Redis.Host != "test-redis" {
		t.Errorf("Expected REDIS_HOST to be 'test-redis', got '%s'", cfg.Redis.Host)
	}
}
