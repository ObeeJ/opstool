package middleware

import (
	"net/http"

	"opstool/pkg/tracing"

	"go.opentelemetry.io/otel/attribute"
)

// TracingMiddleware adds OpenTelemetry tracing to HTTP requests
func TracingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ctx, span := tracing.CreateSpan(r.Context(), "http_request")
		defer span.End()

		// Add relevant HTTP request information to the span
		span.SetAttributes(
			attribute.String("http.method", r.Method),
			attribute.String("http.url", r.URL.String()),
			attribute.String("http.user_agent", r.UserAgent()),
			attribute.String("http.remote_addr", r.RemoteAddr),
		)

		// Add trace headers to response
		w.Header().Set("X-Trace-Id", span.SpanContext().TraceID().String())

		// Serve the request with the enhanced context
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
