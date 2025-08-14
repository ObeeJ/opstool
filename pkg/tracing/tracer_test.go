package tracing

import (
	"context"
	"testing"
	"time"
)

func TestTracing(t *testing.T) {
	// Initialize tracer
	shutdown, err := InitTracer()
	if err != nil {
		t.Fatalf("Failed to initialize tracer: %v", err)
	}
	defer shutdown()

	// Test creating a span
	ctx := context.Background()
	ctx, span := CreateSpan(ctx, "test_span")

	// Verify span was created
	if !span.SpanContext().IsValid() {
		t.Error("Expected valid span context")
	}

	// Add some attributes and events
	span.AddEvent("test event")

	// Test child span
	_, childSpan := CreateSpan(ctx, "child_span")
	if !childSpan.SpanContext().IsValid() {
		t.Error("Expected valid child span context")
	}

	// Clean up
	childSpan.End()
	span.End()

	// Give time for spans to be exported
	time.Sleep(time.Millisecond * 100)
}
