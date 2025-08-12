#!/usr/bin/env python3
import psutil
import json
import time
import os
import redis
from typing import Dict, Any

class SystemMonitor:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        self.thresholds = {
            'cpu': float(os.getenv('CPU_THRESHOLD', '80.0')),
            'memory': float(os.getenv('MEMORY_THRESHOLD', '85.0')),
            'disk': float(os.getenv('DISK_THRESHOLD', '90.0'))
        }
    
    def collect_metrics(self) -> Dict[str, Any]:
        metrics = {
            'timestamp': time.time(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'available': psutil.virtual_memory().available,
                'total': psutil.virtual_memory().total
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'free': psutil.disk_usage('/').free,
                'total': psutil.disk_usage('/').total
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'processes': len(psutil.pids())
        }
        
        return metrics
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> list:
        alerts = []
        
        if metrics['cpu']['percent'] > self.thresholds['cpu']:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f"CPU usage at {metrics['cpu']['percent']:.1f}%",
                'value': metrics['cpu']['percent']
            })
        
        if metrics['memory']['percent'] > self.thresholds['memory']:
            alerts.append({
                'type': 'memory_high',
                'severity': 'critical' if metrics['memory']['percent'] > 95 else 'warning',
                'message': f"Memory usage at {metrics['memory']['percent']:.1f}%",
                'value': metrics['memory']['percent']
            })
        
        if metrics['disk']['percent'] > self.thresholds['disk']:
            alerts.append({
                'type': 'disk_full',
                'severity': 'critical',
                'message': f"Disk usage at {metrics['disk']['percent']:.1f}%",
                'value': metrics['disk']['percent']
            })
        
        return alerts
    
    def store_metrics(self, metrics: Dict[str, Any]):
        # Store current metrics
        self.redis_client.setex('system_metrics', 300, json.dumps(metrics))
        
        # Store in time series (keep last 24 hours)
        timestamp = int(metrics['timestamp'])
        self.redis_client.zadd('metrics_timeseries', {json.dumps(metrics): timestamp})
        
        # Clean old data (older than 24 hours)
        cutoff = timestamp - 86400
        self.redis_client.zremrangebyscore('metrics_timeseries', 0, cutoff)
    
    def get_service_health(self) -> Dict[str, Any]:
        health = {}
        
        # Check if OPSTOOL processes are running
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'opstool' in ' '.join(proc.info['cmdline'] or []).lower():
                    health['opstool_server'] = 'running'
                elif 'python' in proc.info['name'] and 'worker.py' in ' '.join(proc.info['cmdline'] or []):
                    health['python_workers'] = health.get('python_workers', 0) + 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check Redis connection
        try:
            self.redis_client.ping()
            health['redis'] = 'connected'
        except:
            health['redis'] = 'disconnected'
        
        return health
    
    def run_continuous_monitoring(self, interval: int = 60):
        print(f"Starting system monitoring (interval: {interval}s)")
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Add service health
                metrics['services'] = self.get_service_health()
                
                # Check for alerts
                alerts = self.check_thresholds(metrics)
                
                # Store metrics
                self.store_metrics(metrics)
                
                # Send alerts if any
                for alert in alerts:
                    alert['timestamp'] = metrics['timestamp']
                    self.redis_client.lpush('alert_queue', json.dumps(alert))
                
                print(f"Metrics collected: CPU {metrics['cpu']['percent']:.1f}%, "
                      f"Memory {metrics['memory']['percent']:.1f}%, "
                      f"Disk {metrics['disk']['percent']:.1f}%")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("Monitoring stopped")
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)

def main():
    action = os.getenv("ACTION", "monitor")
    monitor = SystemMonitor()
    
    if action == "monitor":
        interval = int(os.getenv("INTERVAL", "60"))
        monitor.run_continuous_monitoring(interval)
    elif action == "metrics":
        metrics = monitor.collect_metrics()
        print(json.dumps(metrics, indent=2))
    elif action == "health":
        health = monitor.get_service_health()
        print(json.dumps(health, indent=2))
    else:
        print(json.dumps({"error": f"Unknown action: {action}"}))

if __name__ == "__main__":
    main()