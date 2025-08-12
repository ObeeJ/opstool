package scheduler

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os/exec"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/robfig/cron/v3"
)

type Task struct {
	ID       string            `json:"id"`
	Name     string            `json:"name"`
	Type     string            `json:"type"` // "cicd", "vcs", "monitor"
	Script   string            `json:"script"`
	Schedule string            `json:"schedule"`
	Args     map[string]string `json:"args"`
	Status   string            `json:"status"`
	Created  time.Time         `json:"created"`
}

type Scheduler struct {
	cron   *cron.Cron
	redis  *redis.Client
	tasks  map[string]*Task
	mutex  sync.RWMutex
	ctx    context.Context
	cancel context.CancelFunc
}

func New(redisClient *redis.Client) *Scheduler {
	ctx, cancel := context.WithCancel(context.Background())
	return &Scheduler{
		cron:   cron.New(),
		redis:  redisClient,
		tasks:  make(map[string]*Task),
		ctx:    ctx,
		cancel: cancel,
	}
}

func (s *Scheduler) Start() {
	s.cron.Start()
	go s.processQueue()
}

func (s *Scheduler) Stop() {
	s.cron.Stop()
	s.cancel()
}

func (s *Scheduler) AddTask(task *Task) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if task.Schedule != "" {
		_, err := s.cron.AddFunc(task.Schedule, func() {
			s.executeTask(task)
		})
		if err != nil {
			return err
		}
	}

	s.tasks[task.ID] = task
	return s.saveTask(task)
}

func (s *Scheduler) executeTask(task *Task) {
	log.Printf("Executing task: %s", task.Name)
	
	// Queue task for Python worker
	taskData, _ := json.Marshal(task)
	err := s.redis.LPush(s.ctx, "task_queue", taskData).Err()
	if err != nil {
		log.Printf("Failed to queue task %s: %v", task.ID, err)
		return
	}

	task.Status = "queued"
	s.saveTask(task)
}

func (s *Scheduler) processQueue() {
	for {
		select {
		case <-s.ctx.Done():
			return
		default:
			result, err := s.redis.BRPop(s.ctx, time.Second*5, "task_results").Result()
			if err != nil {
				continue
			}

			var taskResult map[string]interface{}
			if err := json.Unmarshal([]byte(result[1]), &taskResult); err != nil {
				log.Printf("Failed to unmarshal task result: %v", err)
				continue
			}

			taskID := taskResult["task_id"].(string)
			s.updateTaskStatus(taskID, taskResult["status"].(string))
		}
	}
}

func (s *Scheduler) updateTaskStatus(taskID, status string) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	if task, exists := s.tasks[taskID]; exists {
		task.Status = status
		s.saveTask(task)
	}
}

func (s *Scheduler) saveTask(task *Task) error {
	taskData, err := json.Marshal(task)
	if err != nil {
		return err
	}
	return s.redis.Set(s.ctx, fmt.Sprintf("task:%s", task.ID), taskData, 0).Err()
}

func (s *Scheduler) GetTasks() []*Task {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	tasks := make([]*Task, 0, len(s.tasks))
	for _, task := range s.tasks {
		tasks = append(tasks, task)
	}
	return tasks
}

func (s *Scheduler) ExecuteImmediate(script string, args map[string]string) error {
	cmd := exec.Command("python", script)
	for key, value := range args {
		cmd.Env = append(cmd.Env, fmt.Sprintf("%s=%s", key, value))
	}
	return cmd.Run()
}