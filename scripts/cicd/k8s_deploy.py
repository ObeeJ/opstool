#!/usr/bin/env python3
import os
import json
import subprocess
from kubernetes import client, config
from typing import Dict, Any

class KubernetesDeployment:
    def __init__(self):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
    
    def deploy_app(self, manifest_path: str, namespace: str = "default") -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", manifest_path, "-n", namespace],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        try:
            body = {"spec": {"replicas": replicas}}
            self.apps_v1.patch_namespaced_deployment_scale(
                name=name, namespace=namespace, body=body
            )
            return {"status": "success", "message": f"Scaled {name} to {replicas} replicas"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_pod_status(self, namespace: str = "default") -> Dict[str, Any]:
        try:
            pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            pod_info = []
            
            for pod in pods.items:
                pod_info.append({
                    "name": pod.metadata.name,
                    "status": pod.status.phase,
                    "ready": sum(1 for c in pod.status.container_statuses or [] if c.ready),
                    "restarts": sum(c.restart_count for c in pod.status.container_statuses or [])
                })
            
            return {"status": "success", "pods": pod_info}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    action = os.getenv("ACTION", "deploy")
    k8s = KubernetesDeployment()
    
    if action == "deploy":
        result = k8s.deploy_app(
            os.getenv("MANIFEST_PATH"),
            os.getenv("NAMESPACE", "default")
        )
    elif action == "scale":
        result = k8s.scale_deployment(
            os.getenv("DEPLOYMENT_NAME"),
            int(os.getenv("REPLICAS", "1")),
            os.getenv("NAMESPACE", "default")
        )
    elif action == "status":
        result = k8s.get_pod_status(os.getenv("NAMESPACE", "default"))
    else:
        result = {"status": "error", "message": f"Unknown action: {action}"}
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()