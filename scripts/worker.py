import psutil
import os

class TaskWorker:
    def system_health_check(self):
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        return {"disk_usage": disk.percent}
