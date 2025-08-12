#!/usr/bin/env python3
import os
import json
import subprocess
import boto3
from datetime import datetime
from typing import Dict, Any

class BackupAutomation:
    def __init__(self):
        self.s3_client = boto3.client('s3') if os.getenv('AWS_ACCESS_KEY_ID') else None
        self.backup_bucket = os.getenv('BACKUP_BUCKET', 'opstool-backups')
    
    def backup_database(self) -> Dict[str, Any]:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"db_backup_{timestamp}.sql"
            
            # Create database backup
            cmd = [
                'pg_dump',
                '-h', os.getenv('DB_HOST', 'localhost'),
                '-U', os.getenv('DB_USER', 'opstool'),
                '-d', os.getenv('DB_NAME', 'opstool'),
                '-f', backup_file
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = os.getenv('DB_PASSWORD', 'password')
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Upload to S3 if configured
                if self.s3_client:
                    s3_key = f"database/{backup_file}"
                    self.s3_client.upload_file(backup_file, self.backup_bucket, s3_key)
                    os.remove(backup_file)  # Clean up local file
                    
                    return {
                        "status": "success",
                        "backup_location": f"s3://{self.backup_bucket}/{s3_key}",
                        "timestamp": timestamp
                    }
                else:
                    return {
                        "status": "success",
                        "backup_location": f"local://{backup_file}",
                        "timestamp": timestamp
                    }
            else:
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def backup_redis(self) -> Dict[str, Any]:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"redis_backup_{timestamp}.rdb"
            
            # Create Redis backup
            cmd = [
                'redis-cli',
                '-h', os.getenv('REDIS_HOST', 'localhost'),
                '-p', os.getenv('REDIS_PORT', '6379'),
                '--rdb', backup_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if self.s3_client:
                    s3_key = f"redis/{backup_file}"
                    self.s3_client.upload_file(backup_file, self.backup_bucket, s3_key)
                    os.remove(backup_file)
                    
                    return {
                        "status": "success",
                        "backup_location": f"s3://{self.backup_bucket}/{s3_key}",
                        "timestamp": timestamp
                    }
                else:
                    return {
                        "status": "success",
                        "backup_location": f"local://{backup_file}",
                        "timestamp": timestamp
                    }
            else:
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def backup_configs(self) -> Dict[str, Any]:
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"configs_backup_{timestamp}.tar.gz"
            
            # Backup configuration files
            cmd = [
                'tar', '-czf', backup_file,
                'deployments/',
                '.env',
                'go.mod',
                'go.sum'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if self.s3_client:
                    s3_key = f"configs/{backup_file}"
                    self.s3_client.upload_file(backup_file, self.backup_bucket, s3_key)
                    os.remove(backup_file)
                    
                    return {
                        "status": "success",
                        "backup_location": f"s3://{self.backup_bucket}/{s3_key}",
                        "timestamp": timestamp
                    }
                else:
                    return {
                        "status": "success",
                        "backup_location": f"local://{backup_file}",
                        "timestamp": timestamp
                    }
            else:
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def cleanup_old_backups(self, days: int = 30) -> Dict[str, Any]:
        if not self.s3_client:
            return {"status": "skipped", "message": "S3 not configured"}
        
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.s3_client.list_objects_v2(Bucket=self.backup_bucket)
            deleted_count = 0
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    self.s3_client.delete_object(Bucket=self.backup_bucket, Key=obj['Key'])
                    deleted_count += 1
            
            return {
                "status": "success",
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    action = os.getenv("ACTION", "full")
    backup = BackupAutomation()
    
    results = {}
    
    if action in ["full", "database"]:
        results["database"] = backup.backup_database()
    
    if action in ["full", "redis"]:
        results["redis"] = backup.backup_redis()
    
    if action in ["full", "configs"]:
        results["configs"] = backup.backup_configs()
    
    if action == "cleanup":
        days = int(os.getenv("CLEANUP_DAYS", "30"))
        results["cleanup"] = backup.cleanup_old_backups(days)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()