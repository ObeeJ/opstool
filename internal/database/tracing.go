package database

import (
	"context"
	"database/sql"
	"log"
	"time"

	"opstool/pkg/tracing"

	"go.opentelemetry.io/otel/attribute"
)

// InitTracing initializes database-specific tracing configuration
func InitTracing(ctx context.Context) {
	log.Println("Database tracing initialized")
}

// WrapDB wraps a sql.DB with tracing capabilities
func WrapDB(db *sql.DB) *TracedDB {
	return &TracedDB{DB: db}
}

// TraceQuery executes a query with automatic tracing
func TraceQuery(ctx context.Context, db *sql.DB, query string, args ...interface{}) (*sql.Rows, error) {
	ctx, span := tracing.CreateSpan(ctx, "db.query")
	defer span.End()

	startTime := time.Now()
	rows, err := db.QueryContext(ctx, query, args...)
	duration := time.Since(startTime)

	// Add attributes to the span
	span.SetAttributes(
		attribute.String("db.statement", query),
		attribute.String("db.operation", "query"),
		attribute.Int64("db.duration_ms", duration.Milliseconds()),
	)

	if err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.Bool("db.error", true))
	}

	return rows, err
}

// TraceExec executes a command with automatic tracing
func TraceExec(ctx context.Context, db *sql.DB, query string, args ...interface{}) (sql.Result, error) {
	ctx, span := tracing.CreateSpan(ctx, "db.exec")
	defer span.End()

	startTime := time.Now()
	result, err := db.ExecContext(ctx, query, args...)
	duration := time.Since(startTime)

	// Add attributes to the span
	span.SetAttributes(
		attribute.String("db.statement", query),
		attribute.String("db.operation", "exec"),
		attribute.Int64("db.duration_ms", duration.Milliseconds()),
	)

	if err != nil {
		span.RecordError(err)
		span.SetAttributes(attribute.Bool("db.error", true))
	}

	return result, err
}