from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

JOB_STORE: List[Dict[str, Any]] = []


def add_job(
    scenario_type: str = "shorten",
    status: str = "completed",
    progress: int = 100,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    logs: Optional[List[str]] = None,
) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "scenario_type": scenario_type,
        "status": status,
        "progress": int(progress),
        "created_at": now,
        "started_at": now if status != "pending" else None,
        "completed_at": now if status in {"completed", "failed"} else None,
        "result": result,
        "error": error,
        "logs": logs or [],
    }
    JOB_STORE.append(job)
    return job


def list_jobs() -> List[Dict[str, Any]]:
    return [
        {
            "job_id": job["job_id"],
            "scenario_type": job["scenario_type"],
            "status": job["status"],
            "progress": job["progress"],
            "created_at": job["created_at"],
            "started_at": job.get("started_at"),
            "completed_at": job.get("completed_at"),
            "result": job.get("result"),
            "error": job.get("error"),
            "logs": job.get("logs", []),
        }
        for job in JOB_STORE
    ]


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    for job in JOB_STORE:
        if job["job_id"] == job_id:
            return {
                "job_id": job["job_id"],
                "scenario_type": job["scenario_type"],
                "status": job["status"],
                "progress": job["progress"],
                "created_at": job["created_at"],
                "started_at": job.get("started_at"),
                "completed_at": job.get("completed_at"),
                "result": job.get("result"),
                "error": job.get("error"),
                "logs": job.get("logs", []),
            }
    return None


def add_log(job_id: str, message: str) -> None:
    for job in JOB_STORE:
        if job["job_id"] == job_id:
            job.setdefault("logs", []).append(f"[{datetime.utcnow().isoformat()}] {message}")
            return
