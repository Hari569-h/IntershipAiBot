import json
import os
from typing import Set

class JobCache:
    def __init__(self, cache_file="job_cache.json"):
        self.cache_file = cache_file
        self.jobs = set()
        self._load()

    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    self.jobs = set(json.load(f))
            except Exception:
                self.jobs = set()

    def add(self, job_id: str):
        self.jobs.add(job_id)
        self._save()

    def exists(self, job_id: str) -> bool:
        return job_id in self.jobs

    def _save(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(list(self.jobs), f)
        except Exception:
            pass