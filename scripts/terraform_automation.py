#!/usr/bin/env python3
import os
import json
import subprocess
from typing import Dict, Any

class TerraformAutomation:
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
    
    def init(self) -> Dict[str, Any]:
        return self._run_command(["terraform", "init"])
    
    def plan(self, var_file: str = None) -> Dict[str, Any]:
        cmd = ["terraform", "plan"]
        if var_file:
            cmd.extend(["-var-file", var_file])
        return self._run_command(cmd)
    
    def apply(self, var_file: str = None, auto_approve: bool = True) -> Dict[str, Any]:
        cmd = ["terraform", "apply"]
        if var_file:
            cmd.extend(["-var-file", var_file])
        if auto_approve:
            cmd.append("-auto-approve")
        return self._run_command(cmd)
    
    def destroy(self, auto_approve: bool = True) -> Dict[str, Any]:
        cmd = ["terraform", "destroy"]
        if auto_approve:
            cmd.append("-auto-approve")
        return self._run_command(cmd)
    
    def output(self, output_name: str = None) -> Dict[str, Any]:
        cmd = ["terraform", "output", "-json"]
        if output_name:
            cmd.append(output_name)
        return self._run_command(cmd)
    
    def _run_command(self, cmd: list) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                cmd, cwd=self.working_dir, capture_output=True, text=True, timeout=1800
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Terraform command timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    action = os.getenv("ACTION", "plan")
    working_dir = os.getenv("TERRAFORM_DIR", ".")
    
    tf = TerraformAutomation(working_dir)
    
    if action == "init":
        result = tf.init()
    elif action == "plan":
        result = tf.plan(os.getenv("VAR_FILE"))
    elif action == "apply":
        result = tf.apply(os.getenv("VAR_FILE"))
    elif action == "destroy":
        result = tf.destroy()
    elif action == "output":
        result = tf.output(os.getenv("OUTPUT_NAME"))
    else:
        result = {"status": "error", "message": f"Unknown action: {action}"}
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()