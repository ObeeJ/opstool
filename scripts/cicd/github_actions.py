#!/usr/bin/env python3
import os
import requests
import json
import time
from typing import Dict, List, Any

class GitHubActionsManager:
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def trigger_workflow(self, workflow_id: str, ref: str = "main", inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a GitHub Actions workflow"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_id}/dispatches"
        
        payload = {
            "ref": ref,
            "inputs": inputs or {}
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 204:
            return {"status": "success", "message": "Workflow triggered successfully"}
        else:
            return {"status": "error", "message": f"Failed to trigger workflow: {response.text}"}
    
    def get_workflow_runs(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow runs"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_id}/runs"
        params = {"per_page": limit}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json().get("workflow_runs", [])
        return []
    
    def get_run_status(self, run_id: int) -> Dict[str, Any]:
        """Get status of a specific workflow run"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            run_data = response.json()
            return {
                "id": run_data["id"],
                "status": run_data["status"],
                "conclusion": run_data["conclusion"],
                "created_at": run_data["created_at"],
                "updated_at": run_data["updated_at"],
                "html_url": run_data["html_url"]
            }
        return {}
    
    def cancel_workflow_run(self, run_id: int) -> Dict[str, Any]:
        """Cancel a workflow run"""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/cancel"
        
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 202:
            return {"status": "success", "message": "Workflow run cancelled"}
        else:
            return {"status": "error", "message": f"Failed to cancel run: {response.text}"}
    
    def wait_for_completion(self, run_id: int, timeout: int = 1800) -> Dict[str, Any]:
        """Wait for workflow run to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_run_status(run_id)
            
            if status.get("status") == "completed":
                return {
                    "status": "completed",
                    "conclusion": status.get("conclusion"),
                    "run_data": status
                }
            
            time.sleep(30)  # Check every 30 seconds
        
        return {"status": "timeout", "message": "Workflow run timed out"}

def main():
    # Example usage
    token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("REPO_OWNER", "your-org")
    repo_name = os.getenv("REPO_NAME", "your-repo")
    workflow_id = os.getenv("WORKFLOW_ID", "ci.yml")
    
    if not token:
        print(json.dumps({"status": "error", "message": "GITHUB_TOKEN not provided"}))
        return
    
    manager = GitHubActionsManager(token, repo_owner, repo_name)
    
    action = os.getenv("ACTION", "trigger")
    
    if action == "trigger":
        ref = os.getenv("REF", "main")
        inputs = json.loads(os.getenv("INPUTS", "{}"))
        result = manager.trigger_workflow(workflow_id, ref, inputs)
        
    elif action == "status":
        run_id = int(os.getenv("RUN_ID", "0"))
        result = manager.get_run_status(run_id)
        
    elif action == "list":
        runs = manager.get_workflow_runs(workflow_id)
        result = {"status": "success", "runs": runs}
        
    elif action == "cancel":
        run_id = int(os.getenv("RUN_ID", "0"))
        result = manager.cancel_workflow_run(run_id)
        
    else:
        result = {"status": "error", "message": f"Unknown action: {action}"}
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()