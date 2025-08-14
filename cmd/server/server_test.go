package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"opstool/pkg/health"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func setupRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	// Health & liveness
	hc := health.NewHealthChecker(nil, nil)
	r.GET("/live", hc.LivenessHandler())
	// Metrics
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))
	return r
}

func TestLivenessEndpoint(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/live", nil)
	r.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", w.Code)
	}
	// Check body contains "alive"
	if body := w.Body.String(); body == "" || !contains(body, "alive") {
		t.Errorf("Expected response body to contain 'alive', got %s", body)
	}
}

func TestMetricsEndpoint(t *testing.T) {
	r := setupRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/metrics", nil)
	r.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", w.Code)
	}
	if contentType := w.Header().Get("Content-Type"); contentType == "" || contentType[0:9] != "text/plain" {
		t.Errorf("Expected Content-Type text/plain, got %s", contentType)
	}
}

// contains is a helper to check substring
func contains(s, substr string) bool {
	return strings.Contains(s, substr)
}
