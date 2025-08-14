#!/usr/bin/env python3
"""
OPSTOOL Startup Verification Script
Ensures all components are running correctly before demo
"""
import subprocess
import requests
import os

class StartupChecker:
    def __init__(self):
        self.checks = []
        self.base_url = "http://localhost:8080"
    
    def run_all_checks(self):
        """Run all startup verification checks"""
        print("🔍 OPSTOOL Startup Verification")
        print("=" * 40)
        
        self.check_dependencies()
        self.check_services()
        self.check_database()
        self.check_redis()
        self.check_api_endpoints()
        self.check_file_structure()
        
        self.generate_startup_report()
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("\n📦 Checking Dependencies...")
        
        # Check Go
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Go installed:", result.stdout.strip())
                self.checks.append({"name": "Go Installation", "status": "pass"})
            else:
                print("  ❌ Go not found")
                self.checks.append({"name": "Go Installation", "status": "fail"})
        except FileNotFoundError:
            print("  ❌ Go not installed")
            self.checks.append({"name": "Go Installation", "status": "fail"})
        
        # Check Python
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Python installed:", result.stdout.strip())
                self.checks.append({"name": "Python Installation", "status": "pass"})
            else:
                print("  ❌ Python not found")
                self.checks.append({"name": "Python Installation", "status": "fail"})
        except FileNotFoundError:
            print("  ❌ Python not installed")
            self.checks.append({"name": "Python Installation", "status": "fail"})
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Docker installed:", result.stdout.strip())
                self.checks.append({"name": "Docker Installation", "status": "pass"})
            else:
                print("  ❌ Docker not found")
                self.checks.append({"name": "Docker Installation", "status": "fail"})
        except FileNotFoundError:
            print("  ❌ Docker not installed")
            self.checks.append({"name": "Docker Installation", "status": "fail"})
    
    def check_services(self):
        """Check if required services are running"""
        print("\n🔧 Checking Services...")
        
        # Check if OPSTOOL server is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ OPSTOOL Server running")
                self.checks.append({"name": "OPSTOOL Server", "status": "pass"})
            else:
                print(f"  ❌ OPSTOOL Server unhealthy: {response.status_code}")
                self.checks.append({"name": "OPSTOOL Server", "status": "fail"})
        except requests.exceptions.RequestException as e:
            print(f"  ❌ OPSTOOL Server not accessible: {str(e)}")
            self.checks.append({"name": "OPSTOOL Server", "status": "fail"})
    
    def check_database(self):
        """Check database connectivity"""
        print("\n🗄️  Checking Database...")
        
        try:
            response = requests.get(f"{self.base_url}/ready", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ready":
                    print("  ✅ Database connected")
                    self.checks.append({"name": "Database Connection", "status": "pass"})
                else:
                    print("  ❌ Database not ready")
                    self.checks.append({"name": "Database Connection", "status": "fail"})
            else:
                print("  ❌ Database check failed")
                self.checks.append({"name": "Database Connection", "status": "fail"})
        except Exception as e:
            print(f"  ❌ Database check error: {str(e)}")
            self.checks.append({"name": "Database Connection", "status": "fail"})
    
    def check_redis(self):
        """Check Redis connectivity"""
        print("\n🔴 Checking Redis...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                redis_status = health_data.get("services", {}).get("redis", {}).get("status")
                if redis_status == "healthy":
                    print("  ✅ Redis connected")
                    self.checks.append({"name": "Redis Connection", "status": "pass"})
                else:
                    print("  ❌ Redis unhealthy")
                    self.checks.append({"name": "Redis Connection", "status": "fail"})
            else:
                print("  ❌ Redis check failed")
                self.checks.append({"name": "Redis Connection", "status": "fail"})
        except Exception as e:
            print(f"  ❌ Redis check error: {str(e)}")
            self.checks.append({"name": "Redis Connection", "status": "fail"})
    
    def check_api_endpoints(self):
        """Check critical API endpoints"""
        print("\n🌐 Checking API Endpoints...")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/ready", "Readiness Check"),
            ("/live", "Liveness Check"),
            ("/metrics", "Metrics Endpoint"),
            ("/api/v1/tasks", "Tasks API")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 201]:
                    print(f"  ✅ {name}")
                    self.checks.append({"name": name, "status": "pass"})
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
                    self.checks.append({"name": name, "status": "fail"})
            except Exception as e:
                print(f"  ❌ {name}: {str(e)}")
                self.checks.append({"name": name, "status": "fail"})
    
    def check_file_structure(self):
        """Check if all required files exist"""
        print("\n📁 Checking File Structure...")
        
        required_files = [
            "go.mod",
            "cmd/server/main.go",
            "pkg/api/api.go",
            "pkg/scheduler/scheduler.go",
            "pkg/monitor/monitor.go",
            "scripts/worker.py",
            "scripts/requirements.txt",
            "deployments/docker/docker-compose.yml",
            "web/templates/dashboard.html"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}")
                self.checks.append({"name": f"File: {file_path}", "status": "pass"})
            else:
                print(f"  ❌ {file_path} missing")
                self.checks.append({"name": f"File: {file_path}", "status": "fail"})
    
    def generate_startup_report(self):
        """Generate startup verification report"""
        print("\n📋 STARTUP VERIFICATION REPORT")
        print("=" * 40)
        
        total_checks = len(self.checks)
        passed_checks = len([c for c in self.checks if c["status"] == "pass"])
        failed_checks = total_checks - passed_checks
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks} ✅")
        print(f"Failed: {failed_checks} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_checks > 0:
            print("\n❌ Failed Checks:")
            for check in self.checks:
                if check["status"] == "fail":
                    print(f"  - {check['name']}")
        
        if success_rate >= 90:
            print("\n🎉 OPSTOOL is ready for demo!")
            return True
        elif success_rate >= 70:
            print("\n⚠️  OPSTOOL has some issues but may work for basic demo")
            return True
        else:
            print("\n🚨 OPSTOOL has critical issues. Fix before running demo.")
            return False

def main():
    checker = StartupChecker()
    is_ready = checker.run_all_checks()
    
    if is_ready:
        print("\n🚀 You can now run: python scripts/demo_usage.py")
    else:
        print("\n🔧 Please fix the issues above before running the demo")
        
        # Provide quick fix suggestions
        print("\n💡 Quick Fix Suggestions:")
        print("  1. Start services: make docker-run")
        print("  2. Install dependencies: go mod tidy && pip install -r scripts/requirements.txt")
        print("  3. Build and run: make build && make run")

if __name__ == "__main__":
    main()