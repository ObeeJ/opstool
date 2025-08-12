package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	TasksTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "opstool_tasks_total",
			Help: "Total number of tasks processed",
		},
		[]string{"type", "status"},
	)
	
	TaskDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "opstool_task_duration_seconds",
			Help: "Task execution duration",
		},
		[]string{"type"},
	)
	
	ActiveWorkers = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "opstool_active_workers",
			Help: "Number of active Python workers",
		},
	)
	
	QueueSize = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "opstool_queue_size",
			Help: "Current queue size",
		},
	)
)