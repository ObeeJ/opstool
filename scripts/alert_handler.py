#!/usr/bin/env python3
import json
import os
import requests
import subprocess
from typing import Dict, Any

class AlertHandler:
    def __init__(self):
        self.webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        self.escalation_threshold = int(os.getenv("ESCALATION_THRESHOLD", "3"))
    
    def handle_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        severity = alert.get("severity", "info")
        message = alert.get("message", "")
        
        if severity == "critical":
            return self.handle_critical_alert(alert)
        elif severity == "warning":
            return self.handle_warning_alert(alert)
        else:
            return self.handle_info_alert(alert)
    
    def handle_critical_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        actions_taken = []
        
        # Send immediate notification
        if self.webhook_url:
            self.send_webhook_notification(alert, "🚨 CRITICAL ALERT")
            actions_taken.append("webhook_sent")
        
        # Auto-restart services if deployment failure
        if "deployment" in alert.get("message", "").lower():
            restart_result = self.restart_failed_services()
            actions_taken.append(f"restart_attempt: {restart_result['status']}")
        
        # Scale up workers if queue overload
        if "queue" in alert.get("message", "").lower():
            scale_result = self.scale_workers(replicas=10)
            actions_taken.append(f"scale_up: {scale_result['status']}")
        
        return {
            "status": "handled",
            "severity": "critical",
            "actions_taken": actions_taken
        }
    
    def handle_warning_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        if self.webhook_url:
            self.send_webhook_notification(alert, "⚠️ WARNING")
        
        return {"status": "acknowledged", "severity": "warning"}
    
    def handle_info_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "logged", "severity": "info"}
    
    def send_webhook_notification(self, alert: Dict[str, Any], prefix: str):
        payload = {
            "text": f"{prefix}: {alert.get('message', 'Unknown alert')}",
            "attachments": [{
                "color": "danger" if alert.get("severity") == "critical" else "warning",
                "fields": [
                    {"title": "Severity", "value": alert.get("severity", "unknown"), "short": True},
                    {"title": "Timestamp", "value": alert.get("timestamp", ""), "short": True},
                    {"title": "Source", "value": alert.get("source", "OPSTOOL"), "short": True}
                ]
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            print(f"Failed to send webhook: {e}")
    
    def restart_failed_services(self) -> Dict[str, Any]:
        try:
            result = subprocess.run([
                "kubectl", "rollout", "restart", "deployment/opstool-server", "-n", "opstool"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"status": "success", "message": "Services restarted"}
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scale_workers(self, replicas: int) -> Dict[str, Any]:
        try:
            result = subprocess.run([
                "kubectl", "scale", "deployment/opstool-worker", 
                f"--replicas={replicas}", "-n", "opstool"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"status": "success", "message": f"Scaled to {replicas} replicas"}
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    alert_data = json.loads(os.getenv("ALERT_DATA", "{}"))
    handler = AlertHandler()
    result = handler.handle_alert(alert_data)
    print(json.dumps(result))

if __name__ == "__main__":
    main()