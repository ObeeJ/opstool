package gdpr

import (
	"testing"
	"time"
)

func TestGDPRManager(t *testing.T) {
	manager := NewGDPRManager()

	// Test retention policy
	data := PersonalData{
		ID:              "user123",
		DataType:        "personal_info",
		Value:           "John Doe",
		ConsentGranted:  true,
		ConsentDate:     time.Now(),
		RetentionPeriod: time.Now().Add(time.Hour * 24 * 365),
		Encrypted:       true,
	}

	if !manager.CheckRetention(data) {
		t.Error("Expected data to be within retention period")
	}

	// Test expired data
	expiredData := PersonalData{
		ID:              "user123",
		DataType:        "personal_info",
		Value:           "John Doe",
		ConsentGranted:  true,
		ConsentDate:     time.Now().Add(-time.Hour * 24 * 366), // Over 1 year old
		RetentionPeriod: time.Now().Add(-time.Hour),
		Encrypted:       true,
	}

	if manager.CheckRetention(expiredData) {
		t.Error("Expected data to be outside retention period")
	}

	// Test data serialization
	testData := []PersonalData{data}
	serialized, err := manager.SerializeForExport(testData)
	if err != nil {
		t.Errorf("Failed to serialize data: %v", err)
	}
	if len(serialized) == 0 {
		t.Error("Expected non-empty serialized data")
	}
}
