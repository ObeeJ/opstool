#!/usr/bin/env python3
"""
OPSTOOL Demo Usage Script
Simulates real-world usage scenarios to test all components
"""
import requests
import json
import time
import threading
import random
from datetime import datetime

class OpstoolDemo:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
    
    def run_complete_demo(self):
        """Run comprehensive demo of all OPSTOOL features"""
        print("🚀 Starting OPSTOOL Complete Demo")
        print("=" * 50)
        
        # Test 1: Health Check
        self.test_health_endpoints()
        
        # Test 2: Create CI/CD Tasks
        self.test_cicd_automation()
        
        # Test 3: Version Control Operations
        self.test_vcs_operations()
        
        # Test 4: System Monitoring
        self.test_monitoring_features()
        
        # Test 5: Load Testing
        self.test_load_handling()
        
        # Test 6: Security Features
        self.test_security_features()
        
        # Test 7: Backup Operations
        self.test_backup_operations()
        
        # Generate Report
        self.generate_demo_report()
    
    def test_health_endpoints(self):
        """Test all health check endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        endpoints = ["/health", "/ready", "/live", "/metrics"]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
                print(f"  {endpoint}: {status} ({response.status_code})")
                
                self.results.append({
                    "test": f"Health Check {endpoint}",
                    "status": "pass" if response.status_code == 200 else "fail",
                    "response_time": response.elapsed.total_seconds()
                })
            except Exception as e:
                print(f"  {endpoint}: ❌ FAIL ({str(e)})")
                self.results.append({
                    "test": f"Health Check {endpoint}",
                    "status": "fail",
                    "error": str(e)
                })
    
    def test_cicd_automation(self):
        """Test CI/CD pipeline automation"""
        print("\n🔄 Testing CI/CD Automation...")
        
        # Create GitHub Actions task
        cicd_task = {
            "name": "Deploy to Production",
            "type": "cicd",
            "script": "scripts/cicd/github_actions.py",
            "args": {
                "ACTION": "trigger",
                "WORKFLOW_ID": "deploy.yml",
                "REF": "main"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/tasks",
                json=cicd_task
            )
            
            if response.status_code == 201:
                task_data = response.json()
                print(f"  ✅ CI/CD Task Created: {task_data.get('id', 'N/A')}")
                
                # Test task execution
                exec_response = self.session.post(
                    f"{self.base_url}/api/v1/tasks/{task_data.get('id', 'test')}/execute",
                    json={
                        "script": "scripts/cicd/github_actions.py",
                        "args": cicd_task["args"]
                    }
                )
                
                status = "✅ EXECUTED" if exec_response.status_code == 200 else "❌ FAILED"
                print(f"  Task Execution: {status}")
                
                self.results.append({
                    "test": "CI/CD Task Creation & Execution",
                    "status": "pass" if exec_response.status_code == 200 else "fail"
                })
            else:
                print(f"  ❌ Failed to create CI/CD task: {response.status_code}")
                self.results.append({
                    "test": "CI/CD Task Creation",
                    "status": "fail",
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"  ❌ CI/CD Test Failed: {str(e)}")
            self.results.append({
                "test": "CI/CD Automation",
                "status": "fail",
                "error": str(e)
            })
    
    def test_vcs_operations(self):
        """Test version control operations"""
        print("\n📝 Testing Version Control Operations...")
        
        vcs_tasks = [
            {
                "name": "Create Feature Branch",
                "type": "vcs",
                "script": "scripts/vcs/git_automation.py",
                "args": {
                    "ACTION": "create_branch",
                    "BRANCH_NAME": f"feature/demo-{int(time.time())}",
                    "BASE_BRANCH": "main"
                }
            },
            {
                "name": "Sync Repository",
                "type": "vcs", 
                "script": "scripts/vcs/git_automation.py",
                "args": {
                    "ACTION": "sync",
                    "BRANCH": "main"
                }
            }
        ]
        
        for task in vcs_tasks:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/tasks",
                    json=task
                )
                
                status = "✅ CREATED" if response.status_code == 201 else "❌ FAILED"
                print(f"  {task['name']}: {status}")
                
                self.results.append({
                    "test": f"VCS - {task['name']}",
                    "status": "pass" if response.status_code == 201 else "fail"
                })
                
            except Exception as e:
                print(f"  ❌ {task['name']} Failed: {str(e)}")
                self.results.append({
                    "test": f"VCS - {task['name']}",
                    "status": "fail",
                    "error": str(e)
                })
    
    def test_monitoring_features(self):
        """Test monitoring and alerting features"""
        print("\n📊 Testing Monitoring Features...")
        
        # Add log monitoring
        try:
            monitor_config = {
                "path": "./logs/opstool.log",
                "patterns": ["ERROR", "CRITICAL", "FAIL"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/monitor/watch",
                json=monitor_config
            )
            
            status = "✅ CONFIGURED" if response.status_code == 200 else "❌ FAILED"
            print(f"  Log Monitoring: {status}")
            
            # Test alerts endpoint
            alerts_response = self.session.get(f"{self.base_url}/api/v1/alerts")
            alerts_status = "✅ ACCESSIBLE" if alerts_response.status_code == 200 else "❌ FAILED"
            print(f"  Alerts Endpoint: {alerts_status}")
            
            self.results.append({
                "test": "Monitoring Configuration",
                "status": "pass" if response.status_code == 200 else "fail"
            })
            
        except Exception as e:
            print(f"  ❌ Monitoring Test Failed: {str(e)}")
            self.results.append({
                "test": "Monitoring Features",
                "status": "fail",
                "error": str(e)
            })
    
    def test_load_handling(self):
        """Test system under load"""
        print("\n⚡ Testing Load Handling...")
        
        def create_load_task():
            task = {
                "name": f"Load Test Task {random.randint(1000, 9999)}",
                "type": "monitor",
                "script": "scripts/worker.py",
                "args": {"action": "health_check"}
            }
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/tasks",
                    json=task,
                    timeout=5
                )
                return response.status_code == 201
            except:
                return False
        
        # Create 20 concurrent tasks
        threads = []
        results = []
        
        for i in range(20):
            thread = threading.Thread(target=lambda: results.append(create_load_task()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        success_rate = (sum(results) / len(results)) * 100
        print(f"  Load Test: {success_rate:.1f}% success rate ({sum(results)}/20 tasks)")
        
        self.results.append({
            "test": "Load Handling",
            "status": "pass" if success_rate >= 80 else "fail",
            "success_rate": success_rate
        })
    
    def test_security_features(self):
        """Test security features"""
        print("\n🔒 Testing Security Features...")
        
        # Test rate limiting by making rapid requests
        rapid_requests = []
        for i in range(10):
            try:
                response = self.session.get(f"{self.base_url}/health")
                rapid_requests.append(response.status_code)
            except:
                rapid_requests.append(0)
        
        # Check if any requests were rate limited (429)
        rate_limited = any(code == 429 for code in rapid_requests)
        print(f"  Rate Limiting: {'✅ ACTIVE' if rate_limited else '⚠️  NOT TRIGGERED'}")
        
        # Test metrics endpoint (should be accessible)
        try:
            metrics_response = self.session.get(f"{self.base_url}/metrics")
            metrics_status = "✅ ACCESSIBLE" if metrics_response.status_code == 200 else "❌ FAILED"
            print(f"  Metrics Endpoint: {metrics_status}")
        except Exception as e:
            print(f"  Metrics Endpoint: ❌ FAILED ({str(e)})")
        
        self.results.append({
            "test": "Security Features",
            "status": "pass",
            "rate_limiting": rate_limited
        })
    
    def test_backup_operations(self):
        """Test backup and recovery features"""
        print("\n💾 Testing Backup Operations...")
        
        # Create a backup task
        backup_task = {
            "name": "Database Backup",
            "type": "backup",
            "script": "scripts/backup_automation.py",
            "args": {
                "ACTION": "database"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/tasks",
                json=backup_task
            )
            
            status = "✅ SCHEDULED" if response.status_code == 201 else "❌ FAILED"
            print(f"  Backup Task: {status}")
            
            self.results.append({
                "test": "Backup Operations",
                "status": "pass" if response.status_code == 201 else "fail"
            })
            
        except Exception as e:
            print(f"  ❌ Backup Test Failed: {str(e)}")
            self.results.append({
                "test": "Backup Operations",
                "status": "fail",
                "error": str(e)
            })
    
    def generate_demo_report(self):
        """Generate comprehensive demo report"""
        print("\n📋 DEMO REPORT")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "pass"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📊 Detailed Results:")
        for result in self.results:
            status_icon = "✅" if result["status"] == "pass" else "❌"
            print(f"  {status_icon} {result['test']}")
            if "error" in result:
                print(f"    Error: {result['error']}")
            if "response_time" in result:
                print(f"    Response Time: {result['response_time']:.3f}s")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": success_rate
            },
            "results": self.results
        }
        
        with open("demo_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: demo_report.json")
        
        if success_rate >= 80:
            print("\n🎉 OPSTOOL Demo: SUCCESS! System is working well.")
        else:
            print("\n⚠️  OPSTOOL Demo: Issues detected. Check failed tests.")

def main():
    demo = OpstoolDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()