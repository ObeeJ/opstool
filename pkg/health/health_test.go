package health

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"github.com/gin-gonic/gin"
)

func TestHealthChecker(t *testing.T) {
	// Create a health checker
	hc := NewHealthChecker(nil, nil)
	
	if hc == nil {
		t.Fatal("NewHealthChecker should not return nil")
	}
}

func TestLivenessHandler(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	// Create router and health checker
	r := gin.New()
	hc := NewHealthChecker(nil, nil)
	r.GET("/live", hc.LivenessHandler())
	
	// Create test request
	req, _ := http.NewRequest("GET", "/live", nil)
	w := httptest.NewRecorder()
	
	// Perform request
	r.ServeHTTP(w, req)
	
	// Check response
	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", w.Code)
	}
	
	if w.Body.String() == "" {
		t.Error("Response body should not be empty")
	}
}

func TestReadinessHandler(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	// Create router and health checker
	r := gin.New()
	hc := NewHealthChecker(nil, nil)
	r.GET("/ready", hc.ReadinessHandler())
	
	// Create test request
	req, _ := http.NewRequest("GET", "/ready", nil)
	w := httptest.NewRecorder()
	
	// Perform request
	r.ServeHTTP(w, req)
	
	// Check response (might be 503 due to missing dependencies)
	if w.Code != http.StatusOK && w.Code != http.StatusServiceUnavailable {
		t.Errorf("Expected status 200 or 503, got %d", w.Code)
	}
}

func TestHealthHandler(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	// Create router and health checker
	r := gin.New()
	hc := NewHealthChecker(nil, nil)
	r.GET("/health", hc.HealthHandler())
	
	// Create test request
	req, _ := http.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()
	
	// Perform request
	r.ServeHTTP(w, req)
	
	// Check response
	if w.Code != http.StatusOK && w.Code != http.StatusServiceUnavailable {
		t.Errorf("Expected status 200 or 503, got %d", w.Code)
	}
}
