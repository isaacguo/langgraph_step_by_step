from typing import Any, Dict, Optional, Iterator
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

class CheckpointManager:
    def __init__(self, db_path: str = "checkpoints.sqlite"):
        self.db_path = db_path
        self._init_db()
        self.checkpointer = SqliteSaver(self.conn)

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

    def get_checkpointer(self) -> BaseCheckpointSaver:
        return self.checkpointer

    def list_checkpoints(self, thread_id: str):
        """
        List all checkpoints for a thread.
        """
        return self.checkpointer.list({"configurable": {"thread_id": thread_id}})

    def get_latest_checkpoint(self, thread_id: str):
        """
        Get the latest checkpoint for a thread.
        """
        return self.checkpointer.get({"configurable": {"thread_id": thread_id}})
