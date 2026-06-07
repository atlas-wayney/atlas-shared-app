from pydantic_settings import BaseSettings


class AtlasLoggingSettings(BaseSettings):

    # loguru settings for application logging
    level: str = "INFO"
    log_file: str = "logs/app.log"
    rotation: str = "100 MB"
    retention: str = "10 days"
    backtrace: bool = True
    diagnose: bool = True
    format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | PID:{process} | req:{extra[request_id]} | user:{extra[user_id]} | client:{extra[client_id]} | {file}:{line} | {message}"

    # logging settings for workflow execution logs
    workflow_log_file: str = "logs/workflow.log"
    workflow_log_level: str = "INFO"
    workflow_log_max_bytes: int = 100 * 1024 * 1024  # 100 MB
    workflow_log_backup_count: int = 10
    workflow_log_format: str = "%(asctime)s | %(levelname)-8s | PID:%(process)d | %(name)s:%(funcName)s:%(lineno)d | %(message)s"