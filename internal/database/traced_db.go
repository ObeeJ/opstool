package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"opstool/pkg/tracing"

	"go.opentelemetry.io/otel/attribute"
)

// TracedDB wraps sql.DB with tracing capabilities
type TracedDB struct {
	*sql.DB
}

// QueryContext executes a query with tracing
func (db *TracedDB) QueryContext(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error) {
	ctx, span := tracing.CreateSpan(ctx, "db.query")
	defer span.End()

	startTime := time.Now()
	rows, err := db.DB.QueryContext(ctx, query, args...)
	duration := time.Since(startTime)

	// Add database operation details to span
	span.SetAttributes(
		attribute.String("db.type", "postgres"),
		attribute.String("db.operation", "query"),
		attribute.Float64("db.duration_ms", float64(duration.Milliseconds())),
	)

	if err != nil {
		span.RecordError(err)
		return nil, fmt.Errorf("database query error: %w", err)
	}

	return rows, nil
}

// ExecContext executes a command with tracing
func (db *TracedDB) ExecContext(ctx context.Context, query string, args ...interface{}) (sql.Result, error) {
	ctx, span := tracing.CreateSpan(ctx, "db.exec")
	defer span.End()

	startTime := time.Now()
	result, err := db.DB.ExecContext(ctx, query, args...)
	duration := time.Since(startTime)

	// Add database operation details to span
	span.SetAttributes(
		attribute.String("db.type", "postgres"),
		attribute.String("db.operation", "exec"),
		attribute.Float64("db.duration_ms", float64(duration.Milliseconds())),
	)

	if err != nil {
		span.RecordError(err)
		return nil, fmt.Errorf("database exec error: %w", err)
	}

	return result, nil
}

// NewTracedDB creates a new TracedDB instance
func NewTracedDB(db *sql.DB) *TracedDB {
	return &TracedDB{db}
}

// UnderlyingDB returns the underlying sql.DB instance
func (db *TracedDB) UnderlyingDB() *sql.DB {
	return db.DB
}
