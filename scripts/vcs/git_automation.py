#!/usr/bin/env python3
import os
import json

from git import Repo, GitCommandError
from typing import Dict, List, Any

class GitAutomation:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except Exception as e:
            raise Exception(f"Failed to initialize repository: {e}")
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> Dict[str, Any]:
        """Create a new branch"""
        try:
            # Ensure we're on the base branch
            self.repo.git.checkout(base_branch)
            self.repo.git.pull()
            
            # Create and checkout new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            return {
                "status": "success",
                "message": f"Branch '{branch_name}' created successfully",
                "branch": branch_name
            }
        except GitCommandError as e:
            return {"status": "error", "message": f"Git error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create branch: {e}"}
    
    def commit_changes(self, message: str, files: List[str] = None) -> Dict[str, Any]:
        """Commit changes to the current branch"""
        try:
            if files:
                self.repo.index.add(files)
            else:
                self.repo.git.add(A=True)  # Add all changes
            
            if self.repo.is_dirty():
                commit = self.repo.index.commit(message)
                return {
                    "status": "success",
                    "message": "Changes committed successfully",
                    "commit_hash": commit.hexsha
                }
            else:
                return {"status": "info", "message": "No changes to commit"}
                
        except Exception as e:
            return {"status": "error", "message": f"Failed to commit: {e}"}
    
    def push_branch(self, branch_name: str = None, remote: str = "origin") -> Dict[str, Any]:
        """Push branch to remote"""
        try:
            if not branch_name:
                branch_name = self.repo.active_branch.name
            
            origin = self.repo.remote(remote)
            origin.push(branch_name)
            
            return {
                "status": "success",
                "message": f"Branch '{branch_name}' pushed to {remote}",
                "branch": branch_name
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to push: {e}"}
    
    def merge_branch(self, source_branch: str, target_branch: str = "main") -> Dict[str, Any]:
        """Merge source branch into target branch"""
        try:
            # Checkout target branch
            self.repo.git.checkout(target_branch)
            self.repo.git.pull()
            
            # Merge source branch
            self.repo.git.merge(source_branch)
            
            return {
                "status": "success",
                "message": f"Branch '{source_branch}' merged into '{target_branch}'"
            }
        except GitCommandError as e:
            return {"status": "error", "message": f"Merge conflict or error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to merge: {e}"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get repository status"""
        try:
            status = {
                "current_branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
                "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
                "last_commit": {
                    "hash": self.repo.head.commit.hexsha,
                    "message": self.repo.head.commit.message.strip(),
                    "author": str(self.repo.head.commit.author),
                    "date": self.repo.head.commit.committed_datetime.isoformat()
                }
            }
            
            return {"status": "success", "data": status}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get status: {e}"}
    
    def sync_with_remote(self, branch: str = None, remote: str = "origin") -> Dict[str, Any]:
        """Sync local branch with remote"""
        try:
            if not branch:
                branch = self.repo.active_branch.name
            
            # Fetch latest changes
            origin = self.repo.remote(remote)
            origin.fetch()
            
            # Pull changes
            self.repo.git.checkout(branch)
            origin.pull(branch)
            
            return {
                "status": "success",
                "message": f"Branch '{branch}' synced with {remote}",
                "branch": branch
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to sync: {e}"}
    
    def create_tag(self, tag_name: str, message: str = None) -> Dict[str, Any]:
        """Create a git tag"""
        try:
            if message:
                self.repo.create_tag(tag_name, message=message)
            else:
                self.repo.create_tag(tag_name)
            
            return {
                "status": "success",
                "message": f"Tag '{tag_name}' created successfully",
                "tag": tag_name
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to create tag: {e}"}

def main():
    repo_path = os.getenv("REPO_PATH", ".")
    action = os.getenv("ACTION", "status")
    
    try:
        git_auto = GitAutomation(repo_path)
        
        if action == "create_branch":
            branch_name = os.getenv("BRANCH_NAME")
            base_branch = os.getenv("BASE_BRANCH", "main")
            result = git_auto.create_branch(branch_name, base_branch)
            
        elif action == "commit":
            message = os.getenv("COMMIT_MESSAGE", "Automated commit")
            files = os.getenv("FILES", "").split(",") if os.getenv("FILES") else None
            result = git_auto.commit_changes(message, files)
            
        elif action == "push":
            branch_name = os.getenv("BRANCH_NAME")
            remote = os.getenv("REMOTE", "origin")
            result = git_auto.push_branch(branch_name, remote)
            
        elif action == "merge":
            source_branch = os.getenv("SOURCE_BRANCH")
            target_branch = os.getenv("TARGET_BRANCH", "main")
            result = git_auto.merge_branch(source_branch, target_branch)
            
        elif action == "sync":
            branch = os.getenv("BRANCH")
            remote = os.getenv("REMOTE", "origin")
            result = git_auto.sync_with_remote(branch, remote)
            
        elif action == "tag":
            tag_name = os.getenv("TAG_NAME")
            message = os.getenv("TAG_MESSAGE")
            result = git_auto.create_tag(tag_name, message)
            
        elif action == "status":
            result = git_auto.get_status()
            
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}
            
    except Exception as e:
        result = {"status": "error", "message": str(e)}
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()