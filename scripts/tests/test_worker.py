import pytest
import json
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker import TaskWorker

class TestTaskWorker:
    def setup_method(self):
        self.worker = TaskWorker()
        self.worker.redis_client = Mock()
    
    def test_handle_cicd_task(self):
        task = {
            'id': 'test-123',
            'type': 'cicd',
            'script': 'test_script.py',
            'args': {'ACTION': 'test'}
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'Success'
            mock_run.return_value.stderr = ''
            
            result = self.worker.handle_cicd_task(task)
            
            assert result['status'] == 'completed'
            assert 'Success' in result['stdout']
    
    def test_system_health_check(self):
        result = self.worker.system_health_check()
        
        assert result['status'] == 'completed'
        assert 'cpu_usage' in result['data']
        assert 'memory_usage' in result['data']
        assert 'disk_usage' in result['data']
    
    def test_handle_alert_response(self):
        task = {
            'alert': {
                'severity': 'critical',
                'message': 'Test alert'
            }
        }
        
        result = self.worker.handle_alert_response(task)
        assert result['status'] in ['completed', 'acknowledged']