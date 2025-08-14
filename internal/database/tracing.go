package database

import (
	"fmt"
	"time"

	"opstool/pkg/tracing"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
	"gorm.io/gorm"
)

// TracingPlugin implements GORM's plugin interface for tracing
type TracingPlugin struct{}

// Name returns the name of the plugin
func (p *TracingPlugin) Name() string {
	return "TracingPlugin"
}

// Initialize implements GORM plugin interface
func (p *TracingPlugin) Initialize(db *gorm.DB) error {
	// Add callbacks for Create, Query, Update, Delete operations
	err := db.Callback().Create().Before("gorm:create").Register("tracing:before_create", before("create"))
	if err != nil {
		return err
	}

	err = db.Callback().Query().Before("gorm:query").Register("tracing:before_query", before("query"))
	if err != nil {
		return err
	}

	err = db.Callback().Update().Before("gorm:update").Register("tracing:before_update", before("update"))
	if err != nil {
		return err
	}

	err = db.Callback().Delete().Before("gorm:delete").Register("tracing:before_delete", before("delete"))
	if err != nil {
		return err
	}

	err = db.Callback().Create().After("gorm:create").Register("tracing:after_create", after())
	if err != nil {
		return err
	}

	err = db.Callback().Query().After("gorm:query").Register("tracing:after_query", after())
	if err != nil {
		return err
	}

	err = db.Callback().Update().After("gorm:update").Register("tracing:after_update", after())
	if err != nil {
		return err
	}

	err = db.Callback().Delete().After("gorm:delete").Register("tracing:after_delete", after())
	if err != nil {
		return err
	}

	return nil
}

// before returns a callback function that starts a span
func before(operation string) func(db *gorm.DB) {
	return func(db *gorm.DB) {
		ctx, span := tracing.CreateSpan(db.Statement.Context, fmt.Sprintf("db.%s", operation))
		db.Statement.Context = ctx
		db.InstanceSet("span", span)
		db.InstanceSet("startTime", time.Now())
	}
}

// after returns a callback function that ends the span
func after() func(db *gorm.DB) {
	return func(db *gorm.DB) {
		spanInterface, exists := db.InstanceGet("span")
		if !exists {
			return
		}

		startTimeInterface, exists := db.InstanceGet("startTime")
		if !exists {
			return
		}

		span := spanInterface.(trace.Span)
		startTime := startTimeInterface.(time.Time)
		duration := time.Since(startTime)

		// Add database operation details to span
		span.SetAttributes(
			attribute.String("db.type", "postgres"),
			attribute.String("db.table", db.Statement.Table),
			attribute.String("db.sql", db.Statement.SQL.String()),
			attribute.Float64("db.duration_ms", float64(duration.Milliseconds())),
		)

		if db.Error != nil {
			span.RecordError(db.Error)
		}

		span.End()
	}
}

// EnableTracing adds tracing capabilities to a GORM database instance
func EnableTracing(db *gorm.DB) error {
	return db.Use(&TracingPlugin{})
}
