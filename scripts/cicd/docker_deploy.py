#!/usr/bin/env python3
import docker
import json
import os
from typing import Dict, Any

class DockerDeployment:
    def __init__(self):
        self.client = docker.from_env()
    
    def build_image(self, dockerfile_path: str, tag: str, context_path: str = ".") -> Dict[str, Any]:
        try:
            image, logs = self.client.images.build(
                path=context_path,
                dockerfile=dockerfile_path,
                tag=tag,
                rm=True
            )
            return {"status": "success", "image_id": image.id, "tag": tag}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def deploy_container(self, image: str, name: str, ports: Dict[str, int] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports or {},
                environment=env or {},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            return {"status": "success", "container_id": container.id}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def stop_container(self, name: str) -> Dict[str, Any]:
        try:
            container = self.client.containers.get(name)
            container.stop()
            container.remove()
            return {"status": "success", "message": f"Container {name} stopped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    action = os.getenv("ACTION", "deploy")
    deployer = DockerDeployment()
    
    if action == "build":
        result = deployer.build_image(
            os.getenv("DOCKERFILE", "Dockerfile"),
            os.getenv("TAG", "latest"),
            os.getenv("CONTEXT", ".")
        )
    elif action == "deploy":
        result = deployer.deploy_container(
            os.getenv("IMAGE"),
            os.getenv("CONTAINER_NAME"),
            json.loads(os.getenv("PORTS", "{}")),
            dict(os.environ)
        )
    elif action == "stop":
        result = deployer.stop_container(os.getenv("CONTAINER_NAME"))
    else:
        result = {"status": "error", "message": f"Unknown action: {action}"}
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()