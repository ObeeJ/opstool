#!/usr/bin/env python3
import json
import redis
import subprocess
import sys
import os
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskWorker:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', ''),
            decode_responses=True
        )
        
    def run(self):
        logger.info("Starting OPSTOOL Python worker...")
        
        while True:
            try:
                # Block and wait for tasks
                result = self.redis_client.brpop('task_queue', timeout=5)
                if result:
                    _, task_data = result
                    task = json.loads(task_data)
                    self.process_task(task)
                    
            except KeyboardInterrupt:
                logger.info("Worker shutting down...")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(1)
    
    def process_task(self, task: Dict[str, Any]):
        task_id = task.get('id', 'unknown')
        task_type = task.get('type', 'unknown')
        
        logger.info(f"Processing task {task_id} of type {task_type}")
        
        try:
            if task_type == 'cicd':
                result = self.handle_cicd_task(task)
            elif task_type == 'vcs':
                result = self.handle_vcs_task(task)
            elif task_type == 'monitor':
                result = self.handle_monitor_task(task)
            elif task_type == 'alert_response':
                result = self.handle_alert_response(task)
            else:
                result = {'status': 'error', 'message': f'Unknown task type: {task_type}'}
            
            # Send result back to Go service
            result['task_id'] = task_id
            self.redis_client.lpush('task_results', json.dumps(result))
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            error_result = {
                'task_id': task_id,
                'status': 'error',
                'message': str(e)
            }
            self.redis_client.lpush('task_results', json.dumps(error_result))
    
    def handle_cicd_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        script_path = task.get('script', '')
        args = task.get('args', {})
        
        if not script_path:
            return {'status': 'error', 'message': 'No script specified'}
        
        # Execute CI/CD script
        env = os.environ.copy()
        env.update(args)
        
        try:
            result = subprocess.run(
                ['python', script_path],
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Task timed out'}
    
    def handle_vcs_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Version control operations
        action = task.get('args', {}).get('action', '')
        
        if action == 'sync_repos':
            return self.sync_repositories(task)
        elif action == 'create_branch':
            return self.create_branch(task)
        elif action == 'merge_pr':
            return self.merge_pull_request(task)
        
        return {'status': 'error', 'message': f'Unknown VCS action: {action}'}
    
    def handle_monitor_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # System monitoring tasks
        action = task.get('args', {}).get('action', '')
        
        if action == 'health_check':
            return self.system_health_check()
        elif action == 'log_analysis':
            return self.analyze_logs(task)
        
        return {'status': 'error', 'message': f'Unknown monitor action: {action}'}
    
    def handle_alert_response(self, task: Dict[str, Any]) -> Dict[str, Any]:
        alert = task.get('alert', {})
        severity = alert.get('severity', 'info')
        
        if severity == 'critical':
            # Execute emergency response
            return self.emergency_response(alert)
        
        return {'status': 'acknowledged', 'message': 'Alert processed'}
    
    def sync_repositories(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for repository synchronization
        return {'status': 'completed', 'message': 'Repositories synced'}
    
    def create_branch(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for branch creation
        return {'status': 'completed', 'message': 'Branch created'}
    
    def merge_pull_request(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for PR merge
        return {'status': 'completed', 'message': 'Pull request merged'}
    
    def system_health_check(self) -> Dict[str, Any]:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'timestamp': time.time()
        }
        
        return {
            'status': 'completed',
            'data': health_data,
            'message': 'Health check completed'
        }
    
    def analyze_logs(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for log analysis
        return {'status': 'completed', 'message': 'Log analysis completed'}
    
    def emergency_response(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for emergency response
        logger.warning(f"Emergency response triggered for: {alert.get('message', '')}")
        return {'status': 'completed', 'message': 'Emergency response executed'}

if __name__ == '__main__':
    worker = TaskWorker()
    worker.run()