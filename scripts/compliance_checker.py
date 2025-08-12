#!/usr/bin/env python3
import json
import os
import subprocess
import yaml
from typing import Dict, List, Any

class ComplianceChecker:
    def __init__(self):
        self.checks = {
            'security': self.check_security_compliance,
            'gdpr': self.check_gdpr_compliance,
            'soc2': self.check_soc2_compliance,
            'kubernetes': self.check_k8s_compliance
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        results = {}
        for check_name, check_func in self.checks.items():
            results[check_name] = check_func()
        
        # Calculate overall compliance score
        total_checks = sum(len(result.get('checks', [])) for result in results.values())
        passed_checks = sum(
            len([c for c in result.get('checks', []) if c.get('status') == 'pass'])
            for result in results.values()
        )
        
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'overall_score': compliance_score,
            'results': results,
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': total_checks - passed_checks
            }
        }
    
    def check_security_compliance(self) -> Dict[str, Any]:
        checks = []
        
        # Check for HTTPS enforcement
        checks.append({
            'name': 'HTTPS Enforcement',
            'status': 'pass' if self._check_https_config() else 'fail',
            'description': 'All endpoints should enforce HTTPS'
        })
        
        # Check for authentication
        checks.append({
            'name': 'Authentication Required',
            'status': 'pass' if self._check_auth_config() else 'fail',
            'description': 'All API endpoints should require authentication'
        })
        
        # Check for secrets in environment
        checks.append({
            'name': 'No Hardcoded Secrets',
            'status': 'pass' if self._check_no_hardcoded_secrets() else 'fail',
            'description': 'No secrets should be hardcoded in configuration'
        })
        
        return {
            'category': 'Security',
            'checks': checks,
            'score': len([c for c in checks if c['status'] == 'pass']) / len(checks) * 100
        }
    
    def check_gdpr_compliance(self) -> Dict[str, Any]:
        checks = []
        
        # Check for data encryption
        checks.append({
            'name': 'Data Encryption at Rest',
            'status': 'pass' if self._check_encryption_at_rest() else 'fail',
            'description': 'Personal data must be encrypted at rest'
        })
        
        # Check for audit logging
        checks.append({
            'name': 'Audit Logging',
            'status': 'pass' if self._check_audit_logging() else 'fail',
            'description': 'All data access must be logged'
        })
        
        # Check for data retention policy
        checks.append({
            'name': 'Data Retention Policy',
            'status': 'pass' if self._check_data_retention() else 'fail',
            'description': 'Data retention policies must be implemented'
        })
        
        return {
            'category': 'GDPR',
            'checks': checks,
            'score': len([c for c in checks if c['status'] == 'pass']) / len(checks) * 100
        }
    
    def check_soc2_compliance(self) -> Dict[str, Any]:
        checks = []
        
        # Check for access controls
        checks.append({
            'name': 'Role-Based Access Control',
            'status': 'pass' if self._check_rbac() else 'fail',
            'description': 'RBAC must be implemented'
        })
        
        # Check for monitoring
        checks.append({
            'name': 'System Monitoring',
            'status': 'pass' if self._check_monitoring() else 'fail',
            'description': 'Comprehensive monitoring must be in place'
        })
        
        # Check for backup procedures
        checks.append({
            'name': 'Backup Procedures',
            'status': 'pass' if self._check_backup_procedures() else 'fail',
            'description': 'Regular backup procedures must be implemented'
        })
        
        return {
            'category': 'SOC2',
            'checks': checks,
            'score': len([c for c in checks if c['status'] == 'pass']) / len(checks) * 100
        }
    
    def check_k8s_compliance(self) -> Dict[str, Any]:
        checks = []
        
        # Check for resource limits
        checks.append({
            'name': 'Resource Limits',
            'status': 'pass' if self._check_k8s_resource_limits() else 'fail',
            'description': 'All containers must have resource limits'
        })
        
        # Check for security contexts
        checks.append({
            'name': 'Security Contexts',
            'status': 'pass' if self._check_k8s_security_contexts() else 'fail',
            'description': 'Containers must run with security contexts'
        })
        
        # Check for network policies
        checks.append({
            'name': 'Network Policies',
            'status': 'pass' if self._check_k8s_network_policies() else 'fail',
            'description': 'Network policies must be defined'
        })
        
        return {
            'category': 'Kubernetes',
            'checks': checks,
            'score': len([c for c in checks if c['status'] == 'pass']) / len(checks) * 100
        }
    
    def _check_https_config(self) -> bool:
        # Check if HTTPS is configured in ingress
        try:
            result = subprocess.run([
                'kubectl', 'get', 'ingress', '-n', 'opstool', '-o', 'json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                ingresses = json.loads(result.stdout)
                for ingress in ingresses.get('items', []):
                    if 'tls' in ingress.get('spec', {}):
                        return True
            return False
        except:
            return False
    
    def _check_auth_config(self) -> bool:
        # Check if authentication middleware is configured
        return os.path.exists('pkg/auth/jwt.go')
    
    def _check_no_hardcoded_secrets(self) -> bool:
        # Simple check for common secret patterns
        secret_patterns = ['password=', 'secret=', 'key=', 'token=']
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.go', '.py', '.yml', '.yaml')):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read().lower()
                            for pattern in secret_patterns:
                                if pattern in content and 'example' not in content:
                                    return False
                    except:
                        continue
        return True
    
    def _check_encryption_at_rest(self) -> bool:
        return os.path.exists('pkg/encryption/crypto.go')
    
    def _check_audit_logging(self) -> bool:
        return os.path.exists('pkg/audit/logger.go')
    
    def _check_data_retention(self) -> bool:
        # Check if cleanup scripts exist
        return os.path.exists('scripts/backup_automation.py')
    
    def _check_rbac(self) -> bool:
        return os.path.exists('pkg/tenant/context.go')
    
    def _check_monitoring(self) -> bool:
        return os.path.exists('deployments/monitoring/prometheus.yml')
    
    def _check_backup_procedures(self) -> bool:
        return os.path.exists('scripts/backup_automation.py')
    
    def _check_k8s_resource_limits(self) -> bool:
        try:
            with open('deployments/k8s/opstool-server.yaml', 'r') as f:
                content = yaml.safe_load(f)
                containers = content.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                for container in containers:
                    if 'resources' not in container:
                        return False
            return True
        except:
            return False
    
    def _check_k8s_security_contexts(self) -> bool:
        try:
            with open('deployments/k8s/opstool-server.yaml', 'r') as f:
                content = yaml.safe_load(f)
                containers = content.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                for container in containers:
                    if 'securityContext' not in container:
                        return False
            return True
        except:
            return False
    
    def _check_k8s_network_policies(self) -> bool:
        return os.path.exists('deployments/k8s/network-policy.yaml')

def main():
    checker = ComplianceChecker()
    results = checker.run_all_checks()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()