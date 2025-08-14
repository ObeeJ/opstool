#!/usr/bin/env python3
import os
import json
import subprocess
import requests
from typing import Dict, List, Any

class SecurityScanner:
    def __init__(self):
        self.vulnerabilities = []
    
    def scan_dependencies(self) -> Dict[str, Any]:
        """Scan Python dependencies for vulnerabilities"""
        try:
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True, text=True, cwd='scripts'
            )
            
            if result.stdout:
                vulns = json.loads(result.stdout)
                return {
                    "status": "completed",
                    "vulnerabilities": len(vulns),
                    "details": vulns
                }
            return {"status": "clean", "vulnerabilities": 0}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scan_secrets(self) -> Dict[str, Any]:
        """Scan for exposed secrets in code"""
        secrets_found = []
        patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        try:
            import re
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith(('.py', '.go', '.yml', '.yaml')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                for pattern in patterns:
                                    matches = re.findall(pattern, content, re.IGNORECASE)
                                    if matches:
                                        secrets_found.append({
                                            "file": filepath,
                                            "pattern": pattern,
                                            "matches": len(matches)
                                        })
                        except:
                            continue
            
            return {
                "status": "completed",
                "secrets_found": len(secrets_found),
                "details": secrets_found
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scan_docker_images(self) -> Dict[str, Any]:
        """Scan Docker images for vulnerabilities"""
        try:
            images = ['opstool/server:latest', 'opstool/worker:latest']
            results = []
            
            for image in images:
                result = subprocess.run(
                    ['docker', 'run', '--rm', '-v', '/var/run/docker.sock:/var/run/docker.sock',
                     'aquasec/trivy', 'image', '--format', 'json', image],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0 and result.stdout:
                    scan_result = json.loads(result.stdout)
                    results.append({
                        "image": image,
                        "vulnerabilities": len(scan_result.get('Results', [])),
                        "details": scan_result
                    })
            
            return {
                "status": "completed",
                "images_scanned": len(results),
                "results": results
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_ssl_config(self) -> Dict[str, Any]:
        """Check SSL/TLS configuration"""
        try:
            response = requests.get('https://localhost:8080', verify=False, timeout=5)
            return {
                "status": "ssl_enabled",
                "certificate_valid": False,  # Since we used verify=False
                "recommendation": "Use valid SSL certificate"
            }
        except requests.exceptions.SSLError:
            return {
                "status": "ssl_error",
                "recommendation": "Fix SSL configuration"
            }
        except Exception:
            return {
                "status": "no_ssl",
                "recommendation": "Enable HTTPS"
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        report = {
            "timestamp": time.time(),
            "scans": {
                "dependencies": self.scan_dependencies(),
                "secrets": self.scan_secrets(),
                "docker_images": self.scan_docker_images(),
                "ssl_config": self.check_ssl_config()
            }
        }
        
        # Calculate overall security score
        total_issues = 0
        for scan_name, scan_result in report["scans"].items():
            if scan_result.get("vulnerabilities"):
                total_issues += scan_result["vulnerabilities"]
            if scan_result.get("secrets_found"):
                total_issues += scan_result["secrets_found"]
        
        if total_issues == 0:
            report["security_score"] = "A"
        elif total_issues < 5:
            report["security_score"] = "B"
        elif total_issues < 10:
            report["security_score"] = "C"
        else:
            report["security_score"] = "F"
        
        return report

def main():
    import time
    scanner = SecurityScanner()
    print("Running security scan...")
    
    report = scanner.generate_report()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()