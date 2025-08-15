package auth

import (
	"testing"
	"time"
)

func TestGenerateJWT(t *testing.T) {
	// Test JWT generation
	userID := "test-user-123"
	role := "user"
	token, err := GenerateToken(userID, role)

	if err != nil {
		t.Errorf("Failed to generate JWT: %v", err)
	}

	if token == "" {
		t.Error("Generated token should not be empty")
	}
}

func TestValidateJWT(t *testing.T) {
	// Test JWT validation with valid token
	userID := "test-user-456"
	role := "admin"
	token, err := GenerateToken(userID, role)
	if err != nil {
		t.Fatalf("Failed to generate JWT for validation test: %v", err)
	}

	// Validate the token
	claims, err := ValidateToken(token)
	if err != nil {
		t.Errorf("Failed to validate JWT: %v", err)
	}

	if claims == nil {
		t.Error("Claims should not be nil for valid token")
	}

	// Test with invalid token
	_, err = ValidateToken("invalid.token.here")
	if err == nil {
		t.Error("Expected error for invalid token")
	}
}

func TestJWTExpiration(t *testing.T) {
	// This test checks JWT structure but doesn't test actual expiration
	// since that would require waiting or mocking time
	userID := "test-user-789"
	role := "user"
	token, err := GenerateToken(userID, role)

	if err != nil {
		t.Fatalf("Failed to generate JWT: %v", err)
	}

	claims, err := ValidateToken(token)
	if err != nil {
		t.Fatalf("Failed to validate JWT: %v", err)
	}

	// Check that expiration is set to future
	if claims.ExpiresAt.Time.Before(time.Now()) {
		t.Error("JWT should not be expired immediately after creation")
	}
}
