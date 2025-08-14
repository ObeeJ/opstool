package main

import (
	"context"
	"log"
	"net/http"
	"opstool/internal/config"
	"opstool/internal/database"
	"opstool/pkg/api"
	"opstool/pkg/audit"
	"opstool/pkg/health"
	"opstool/pkg/middleware"
	"opstool/pkg/monitor"
	"opstool/pkg/scheduler"
	"opstool/pkg/tracing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
	cfg := config.Load()

	// Initialize tracing
	shutdown, err := tracing.InitTracer()
	if err != nil {
		log.Fatalf("Failed to initialize tracer: %v", err)
	}
	defer shutdown()

	// Initialize Redis
	rdb := redis.NewClient(&redis.Options{
		Addr:     cfg.Redis.Host + ":" + cfg.Redis.Port,
		Password: cfg.Redis.Password,
		DB:       0,
	})

	ctx := context.Background()
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Printf("Redis connection failed: %v", err)
	}

	// Initialize Database
	db, err := database.Connect(cfg)
	if err != nil {
		log.Fatalf("Database connection failed: %v", err)
	}
	sqlDB, err := db.DB.DB()
	if err != nil {
		log.Fatalf("Failed to get underlying sql.DB for closing: %v", err)
	}
	defer sqlDB.Close()

	// Create traced database wrapper
	tracedDB := database.NewTracedDB(sqlDB)

	// Apply database schema
	if err := db.InitSchema(); err != nil {
		log.Printf("Schema initialization failed: %v", err)
	}

	// Initialize components with traced DB
	sched := scheduler.New(rdb)
	mon := monitor.New(rdb)
	auditor := audit.NewAuditLogger(tracedDB.UnderlyingDB())
	healthChecker := health.NewHealthChecker(tracedDB.UnderlyingDB(), rdb)

	// Rate limiter
	rateLimiter := middleware.NewRateLimiter(100, 200)

	// Start services
	sched.Start()
	mon.Start()

	// Setup routes
	r := gin.Default()

	// Middleware
	r.Use(rateLimiter.Middleware())
	r.Use(func(c *gin.Context) {
		middleware.TracingMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			c.Request = r
			c.Next()
		})).ServeHTTP(c.Writer, c.Request)
	})

	// Health endpoints
	r.GET("/health", healthChecker.HealthHandler())
	r.GET("/ready", healthChecker.ReadinessHandler())
	r.GET("/live", healthChecker.LivenessHandler())

	// Metrics endpoint
	r.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// API routes
	apiServer := api.New(sched, mon)
	apiGroup := r.Group("/api/v1")
	{
		apiGroup.POST("/tasks", apiServer.CreateTask)
		apiGroup.GET("/tasks", apiServer.GetTasks)
		apiGroup.POST("/tasks/:id/execute", apiServer.ExecuteTask)
		apiGroup.POST("/monitor/watch", apiServer.AddLogWatch)
		apiGroup.GET("/alerts", apiServer.GetAlerts)
	}

	// WebSocket endpoint
	r.GET("/ws", apiServer.HandleWebSocket)

	// Static files and dashboard
	r.Static("/static", "./web/static")
	r.LoadHTMLGlob("web/templates/*")
	r.GET("/", apiServer.Dashboard)

	// Use auditor for logging
	_ = auditor

	log.Printf("OPSTOOL server starting on %s:%s", cfg.Server.Host, cfg.Server.Port)

	srv := &http.Server{
		Addr:         cfg.Server.Host + ":" + cfg.Server.Port,
		Handler:      r,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
	}

	log.Fatal(srv.ListenAndServe())
}
