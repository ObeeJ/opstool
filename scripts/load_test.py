#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import time
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    def __init__(self, base_url="http://localhost:5044"):
        self.base_url = base_url
        self.results = []
    
    async def create_task(self, session, task_data):
        start_time = time.time()
        try:
            async with session.post(f"{self.base_url}/api/v1/tasks", json=task_data) as response:
                duration = time.time() - start_time
                return {
                    "status": response.status,
                    "duration": duration,
                    "success": response.status == 201
                }
        except Exception as e:
            return {
                "status": 0,
                "duration": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    async def run_load_test(self, concurrent_users=10, requests_per_user=100):
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            for user in range(concurrent_users):
                for req in range(requests_per_user):
                    task_data = {
                        "name": f"Load Test {user}-{req}",
                        "type": "monitor",
                        "script": "scripts/worker.py",
                        "args": {"action": "health_check"}
                    }
                    tasks.append(self.create_task(session, task_data))
            
            results = await asyncio.gather(*tasks)
            return self.analyze_results(results)
    
    def analyze_results(self, results):
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests
        
        durations = [r["duration"] for r in results if r["success"]]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests) * 100,
            "average_response_time": avg_duration,
            "max_response_time": max(durations) if durations else 0,
            "min_response_time": min(durations) if durations else 0
        }

async def main():
    tester = LoadTester()
    print("Starting load test...")
    
    results = await tester.run_load_test(concurrent_users=50, requests_per_user=20)
    
    print("\n=== Load Test Results ===")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())