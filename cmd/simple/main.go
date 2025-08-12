package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "5051"
	}

	r := gin.Default()
	r.LoadHTMLGlob("web/templates/*")

	// Health endpoints
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
			"message": "OPSTOOL server is running",
			"timestamp": time.Now(),
		})
	})

	r.GET("/ready", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ready"})
	})

	r.GET("/live", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "alive"})
	})

	// API endpoints
	r.GET("/api/v1/tasks", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"tasks": []gin.H{
				{"id": "1", "name": "Deploy Production API", "status": "success", "type": "kubernetes-deploy"},
				{"id": "2", "name": "Database Backup", "status": "running", "type": "backup-automation"},
				{"id": "3", "name": "Security Scan", "status": "completed", "type": "security-scanner"},
			},
		})
	})

	r.POST("/api/v1/tasks", func(c *gin.Context) {
		c.JSON(201, gin.H{
			"message": "Task created successfully",
			"id": "task-" + time.Now().Format("20060102150405"),
		})
	})

	// Dashboard
	r.GET("/", func(c *gin.Context) {
		c.HTML(200, "dashboard.html", gin.H{
			"title": "OPSTOOL Dashboard",
		})
	})

	log.Printf("🚀 OPSTOOL server starting on http://localhost:%s", port)
	
	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      r,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
	}
	
	log.Fatal(srv.ListenAndServe())
}