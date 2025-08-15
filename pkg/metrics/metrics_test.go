package metrics

import (
	"testing"

	"github.com/prometheus/client_golang/prometheus"
)

func TestMetricsInitialization(t *testing.T) {
	// Test that metrics can be initialized without panic
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Metrics initialization panicked: %v", r)
		}
	}()

	// Create a new registry for testing
	registry := prometheus.NewRegistry()

	// Test that we can register metrics
	counter := prometheus.NewCounter(prometheus.CounterOpts{
		Name: "test_counter",
		Help: "A test counter",
	})

	err := registry.Register(counter)
	if err != nil {
		t.Errorf("Failed to register counter: %v", err)
	}

	// Test incrementing
	counter.Inc()

	// Test that metric was registered correctly
	metrics, err := registry.Gather()
	if err != nil {
		t.Errorf("Failed to gather metrics: %v", err)
	}

	if len(metrics) == 0 {
		t.Error("Expected at least one metric")
	}
}

func TestRequestMetrics(t *testing.T) {
	// Test basic request counting
	requestCounter := prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint"},
	)

	// Test incrementing with labels
	requestCounter.WithLabelValues("GET", "/health").Inc()
	requestCounter.WithLabelValues("POST", "/api/tasks").Inc()

	// Test that metrics can be gathered
	registry := prometheus.NewRegistry()
	registry.MustRegister(requestCounter)

	families, err := registry.Gather()
	if err != nil {
		t.Errorf("Failed to gather metrics: %v", err)
	}

	if len(families) == 0 {
		t.Error("Expected at least one metric family")
	}
}
