package health

import (
	"context"
	"database/sql"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

type HealthChecker struct {
	db    *sql.DB
	redis *redis.Client
}

type HealthStatus struct {
	Status    string            `json:"status"`
	Timestamp time.Time         `json:"timestamp"`
	Services  map[string]Status `json:"services"`
	Version   string            `json:"version"`
	Uptime    time.Duration     `json:"uptime"`
}

type Status struct {
	Status      string        `json:"status"`
	ResponseTime time.Duration `json:"response_time"`
	Error       string        `json:"error,omitempty"`
}

var startTime = time.Now()

func NewHealthChecker(db *sql.DB, redis *redis.Client) *HealthChecker {
	return &HealthChecker{db: db, redis: redis}
}

func (h *HealthChecker) CheckHealth() HealthStatus {
	ctx := context.Background()
	services := make(map[string]Status)
	
	// Check database
	dbStart := time.Now()
	if err := h.db.PingContext(ctx); err != nil {
		services["database"] = Status{
			Status:       "unhealthy",
			ResponseTime: time.Since(dbStart),
			Error:        err.Error(),
		}
	} else {
		services["database"] = Status{
			Status:       "healthy",
			ResponseTime: time.Since(dbStart),
		}
	}
	
	// Check Redis
	redisStart := time.Now()
	if err := h.redis.Ping(ctx).Err(); err != nil {
		services["redis"] = Status{
			Status:       "unhealthy",
			ResponseTime: time.Since(redisStart),
			Error:        err.Error(),
		}
	} else {
		services["redis"] = Status{
			Status:       "healthy",
			ResponseTime: time.Since(redisStart),
		}
	}
	
	// Overall status
	overallStatus := "healthy"
	for _, service := range services {
		if service.Status == "unhealthy" {
			overallStatus = "unhealthy"
			break
		}
	}
	
	return HealthStatus{
		Status:    overallStatus,
		Timestamp: time.Now(),
		Services:  services,
		Version:   "1.0.0",
		Uptime:    time.Since(startTime),
	}
}

func (h *HealthChecker) HealthHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		health := h.CheckHealth()
		
		statusCode := http.StatusOK
		if health.Status == "unhealthy" {
			statusCode = http.StatusServiceUnavailable
		}
		
		c.JSON(statusCode, health)
	}
}

func (h *HealthChecker) ReadinessHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := context.Background()
		
		if err := h.db.PingContext(ctx); err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status": "not ready",
				"reason": "database unavailable",
			})
			return
		}
		
		if err := h.redis.Ping(ctx).Err(); err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status": "not ready",
				"reason": "redis unavailable",
			})
			return
		}
		
		c.JSON(http.StatusOK, gin.H{
			"status": "ready",
			"timestamp": time.Now(),
		})
	}
}

func (h *HealthChecker) LivenessHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "alive",
			"timestamp": time.Now(),
			"uptime": time.Since(startTime).String(),
		})
	}
}