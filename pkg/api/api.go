package api

import (
	"net/http"
	"opstool/pkg/monitor"
	"opstool/pkg/scheduler"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

type API struct {
	scheduler *scheduler.Scheduler
	monitor   *monitor.Monitor
	upgrader  websocket.Upgrader
}

func New(s *scheduler.Scheduler, m *monitor.Monitor) *API {
	return &API{
		scheduler: s,
		monitor:   m,
		upgrader: websocket.Upgrader {
			CheckOrigin: func(r *http.Request) bool { return true },
		},
	}
}

func (a *API) CreateTask(c *gin.Context) {
	var task scheduler.Task
	if err := c.ShouldBindJSON(&task); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	task.Created = time.Now()
	task.Status = "created"
	if task.ID == "" {
		task.ID = generateTaskID()
	}

	if err := a.scheduler.AddTask(&task); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, task)
}

func (a *API) GetTasks(c *gin.Context) {
	tasks := a.scheduler.GetTasks()
	c.JSON(http.StatusOK, gin.H{"tasks": tasks})
}

func (a *API) ExecuteTask(c *gin.Context) {
	taskID := c.Param("id")
	
	var req struct {
		Script string            `json:"script"`
		Args   map[string]string `json:"args"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := a.scheduler.ExecuteImmediate(req.Script, req.Args); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Task executed", "task_id": taskID})
}

func (a *API) AddLogWatch(c *gin.Context) {
	var req struct {
		Path     string   `json:"path"`
		Patterns []string `json:"patterns"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := a.monitor.WatchFile(req.Path, req.Patterns); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Log watch added"})
}

func (a *API) GetAlerts(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"alerts": []interface{}{}})
}

func (a *API) HandleWebSocket(c *gin.Context) {
	conn, err := a.upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		return
	}
	defer conn.Close()

	a.monitor.AddWebSocketClient(conn)

	for {
		_, _, err := conn.ReadMessage()
		if err != nil {
			break
		}
	}
}

func (a *API) Dashboard(c *gin.Context) {
	c.HTML(http.StatusOK, "dashboard.html", gin.H{
		"title": "OPSTOOL Dashboard",
	})
}

func generateTaskID() string {
	return time.Now().Format("20060102150405") + "-task"
}