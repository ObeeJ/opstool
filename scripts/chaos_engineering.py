#!/usr/bin/env python3
import random
import time
import subprocess
import json
import os
from typing import Dict, Any

class ChaosEngineer:
    def __init__(self):
        self.experiments = {
            'kill_random_pod': self.kill_random_pod,
            'network_latency': self.inject_network_latency,
            'cpu_stress': self.inject_cpu_stress,
            'memory_stress': self.inject_memory_stress,
            'disk_fill': self.fill_disk_space,
            'redis_failure': self.simulate_redis_failure
        }
    
    def run_experiment(self, experiment_name: str, duration: int = 60) -> Dict[str, Any]:
        if experiment_name not in self.experiments:
            return {"status": "error", "message": f"Unknown experiment: {experiment_name}"}
        
        print(f"Starting chaos experiment: {experiment_name}")
        start_time = time.time()
        
        try:
            result = self.experiments[experiment_name](duration)
            result['duration'] = time.time() - start_time
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "duration": time.time() - start_time
            }
    
    def kill_random_pod(self, duration: int) -> Dict[str, Any]:
        # Get random pod
        result = subprocess.run([
            'kubectl', 'get', 'pods', '-n', 'opstool', '-o', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"status": "error", "message": "Failed to get pods"}
        
        pods = json.loads(result.stdout)['items']
        if not pods:
            return {"status": "error", "message": "No pods found"}
        
        target_pod = random.choice(pods)['metadata']['name']
        
        # Kill the pod
        subprocess.run([
            'kubectl', 'delete', 'pod', target_pod, '-n', 'opstool'
        ], capture_output=True)
        
        return {
            "status": "completed",
            "message": f"Killed pod: {target_pod}",
            "target": target_pod
        }
    
    def inject_network_latency(self, duration: int) -> Dict[str, Any]:
        # Simulate network latency using tc (traffic control)
        latency = random.randint(100, 500)  # ms
        
        subprocess.run([
            'tc', 'qdisc', 'add', 'dev', 'eth0', 'root', 'netem', 'delay', f'{latency}ms'
        ], capture_output=True)
        
        time.sleep(duration)
        
        # Remove latency
        subprocess.run([
            'tc', 'qdisc', 'del', 'dev', 'eth0', 'root'
        ], capture_output=True)
        
        return {
            "status": "completed",
            "message": f"Injected {latency}ms network latency for {duration}s"
        }
    
    def inject_cpu_stress(self, duration: int) -> Dict[str, Any]:
        # Use stress tool to consume CPU
        cpu_cores = os.cpu_count()
        stress_cores = random.randint(1, cpu_cores)
        
        process = subprocess.Popen([
            'stress', '--cpu', str(stress_cores), '--timeout', f'{duration}s'
        ])
        
        process.wait()
        
        return {
            "status": "completed",
            "message": f"CPU stress test completed ({stress_cores} cores for {duration}s)"
        }
    
    def inject_memory_stress(self, duration: int) -> Dict[str, Any]:
        # Consume memory
        memory_mb = random.randint(100, 500)
        
        process = subprocess.Popen([
            'stress', '--vm', '1', '--vm-bytes', f'{memory_mb}M', '--timeout', f'{duration}s'
        ])
        
        process.wait()
        
        return {
            "status": "completed",
            "message": f"Memory stress test completed ({memory_mb}MB for {duration}s)"
        }
    
    def fill_disk_space(self, duration: int) -> Dict[str, Any]:
        # Create temporary large file
        file_size = random.randint(100, 1000)  # MB
        temp_file = f"/tmp/chaos_fill_{int(time.time())}"
        
        subprocess.run([
            'dd', 'if=/dev/zero', f'of={temp_file}', f'bs=1M', f'count={file_size}'
        ], capture_output=True)
        
        time.sleep(duration)
        
        # Clean up
        os.remove(temp_file)
        
        return {
            "status": "completed",
            "message": f"Disk fill test completed ({file_size}MB for {duration}s)"
        }
    
    def simulate_redis_failure(self, duration: int) -> Dict[str, Any]:
        # Block Redis port using iptables
        subprocess.run([
            'iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '6379', '-j', 'DROP'
        ], capture_output=True)
        
        time.sleep(duration)
        
        # Restore Redis access
        subprocess.run([
            'iptables', '-D', 'OUTPUT', '-p', 'tcp', '--dport', '6379', '-j', 'DROP'
        ], capture_output=True)
        
        return {
            "status": "completed",
            "message": f"Redis failure simulation completed ({duration}s)"
        }
    
    def run_random_experiment(self, duration: int = 60) -> Dict[str, Any]:
        experiment = random.choice(list(self.experiments.keys()))
        return self.run_experiment(experiment, duration)

def main():
    chaos = ChaosEngineer()
    experiment = os.getenv("EXPERIMENT", "random")
    duration = int(os.getenv("DURATION", "60"))
    
    if experiment == "random":
        result = chaos.run_random_experiment(duration)
    else:
        result = chaos.run_experiment(experiment, duration)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()