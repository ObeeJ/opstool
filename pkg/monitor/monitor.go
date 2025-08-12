package monitor

import (
	"bufio"
	"context"
	"log"
	"os"
	"regexp"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/gorilla/websocket"
)

type LogEntry struct {
	Timestamp time.Time `json:"timestamp"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
	Source    string    `json:"source"`
}

type Alert struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`
	Message   string    `json:"message"`
	Severity  string    `json:"severity"`
	Timestamp time.Time `json:"timestamp"`
}

type Monitor struct {
	redis     *redis.Client
	watchers  map[string]*FileWatcher
	alerts    chan Alert
	clients   map[*websocket.Conn]bool
	mutex     sync.RWMutex
	ctx       context.Context
	cancel    context.CancelFunc
}

type FileWatcher struct {
	path     string
	patterns []*regexp.Regexp
	file     *os.File
	scanner  *bufio.Scanner
}

func New(redisClient *redis.Client) *Monitor {
	ctx, cancel := context.WithCancel(context.Background())
	return &Monitor{
		redis:    redisClient,
		watchers: make(map[string]*FileWatcher),
		alerts:   make(chan Alert, 100),
		clients:  make(map[*websocket.Conn]bool),
		ctx:      ctx,
		cancel:   cancel,
	}
}

func (m *Monitor) Start() {
	go m.processAlerts()
}

func (m *Monitor) Stop() {
	m.cancel()
	for _, watcher := range m.watchers {
		if watcher.file != nil {
			watcher.file.Close()
		}
	}
}

func (m *Monitor) WatchFile(path string, alertPatterns []string) error {
	patterns := make([]*regexp.Regexp, len(alertPatterns))
	for i, pattern := range alertPatterns {
		regex, err := regexp.Compile(pattern)
		if err != nil {
			return err
		}
		patterns[i] = regex
	}

	file, err := os.Open(path)
	if err != nil {
		return err
	}

	// Seek to end of file
	file.Seek(0, 2)

	watcher := &FileWatcher{
		path:     path,
		patterns: patterns,
		file:     file,
		scanner:  bufio.NewScanner(file),
	}

	m.watchers[path] = watcher
	go m.watchFile(watcher)
	return nil
}

func (m *Monitor) watchFile(watcher *FileWatcher) {
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-m.ctx.Done():
			return
		case <-ticker.C:
			for watcher.scanner.Scan() {
				line := watcher.scanner.Text()
				m.processLogLine(line, watcher)
			}
		}
	}
}

func (m *Monitor) processLogLine(line string, watcher *FileWatcher) {
	for _, pattern := range watcher.patterns {
		if pattern.MatchString(line) {
			alert := Alert{
				ID:        generateID(),
				Type:      "log_alert",
				Message:   line,
				Severity:  m.determineSeverity(line),
				Timestamp: time.Now(),
			}
			
			select {
			case m.alerts <- alert:
			default:
				log.Println("Alert channel full, dropping alert")
			}
			break
		}
	}
}

func (m *Monitor) processAlerts() {
	for {
		select {
		case <-m.ctx.Done():
			return
		case alert := <-m.alerts:
			m.handleAlert(alert)
		}
	}
}

func (m *Monitor) handleAlert(alert Alert) {
	// Store in Redis
	alertKey := "alert:" + alert.ID
	m.redis.HSet(m.ctx, alertKey, map[string]interface{}{
		"type":      alert.Type,
		"message":   alert.Message,
		"severity":  alert.Severity,
		"timestamp": alert.Timestamp.Unix(),
	})

	// Broadcast to WebSocket clients
	m.broadcastAlert(alert)

	// Trigger automation if critical
	if alert.Severity == "critical" {
		m.triggerAutomation(alert)
	}
}

func (m *Monitor) broadcastAlert(alert Alert) {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	for client := range m.clients {
		err := client.WriteJSON(alert)
		if err != nil {
			client.Close()
			delete(m.clients, client)
		}
	}
}

func (m *Monitor) triggerAutomation(alert Alert) {
	// Queue automation task
	task := map[string]interface{}{
		"type":   "alert_response",
		"alert":  alert,
		"script": "scripts/alert_handler.py",
	}
	
	m.redis.LPush(m.ctx, "task_queue", task)
}

func (m *Monitor) AddWebSocketClient(conn *websocket.Conn) {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	m.clients[conn] = true
}

func (m *Monitor) determineSeverity(line string) string {
	if regexp.MustCompile(`(?i)(error|fail|critical|fatal)`).MatchString(line) {
		return "critical"
	}
	if regexp.MustCompile(`(?i)(warn|warning)`).MatchString(line) {
		return "warning"
	}
	return "info"
}

func generateID() string {
	return time.Now().Format("20060102150405") + "-" + "alert"
}