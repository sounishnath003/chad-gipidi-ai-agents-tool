import logging
import threading
import queue
from typing import Optional
from datetime import datetime

class TokenUsage:
    def __init__(self):
        self._total_tokens = 0
        self._lock = threading.Lock()
        self._queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None

    def update_usage(self, current_tokens: int):
        """Put the current token usage on the queue to be processed by the background thread."""
        self._queue.put(current_tokens)

    def get_total_tokens(self) -> int:
        """Get the total token count in a thread-safe manner."""
        with self._lock:
            return self._total_tokens

    def _process_queue(self):
        """Process token updates from the queue."""
        while True:
            try:
                current_tokens = self._queue.get_nowait()
                with self._lock:
                    self._total_tokens += current_tokens
                logging.info(f"(Tokens: current={current_tokens}, total={self._total_tokens})")
                self._queue.task_done()
            except queue.Empty:
                break

    def _run(self):
        """The main loop for the background thread."""
        while True:
            try:
                # Block until an item is available or the thread is stopped
                current_tokens = self._queue.get(timeout=1)
                with self._lock:
                    self._total_tokens += current_tokens
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"[{timestamp}] (Tokens: current={current_tokens}, total={self._total_tokens})")
                self._queue.task_done()
            except queue.Empty:
                # This allows the thread to check if it should exit
                if self._thread is None:
                    break

    def start(self):
        """Start the background thread for tracking token usage."""
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            logging.info("Token usage tracker started.")

    def stop(self):
        """Stop the background thread and log the final usage."""
        if self._thread is not None:
            # Signal the thread to stop by setting self._thread to None
            thread_to_join = self._thread
            self._thread = None
            
            # Wait for the queue to be empty
            self._queue.join()
            
            # Wait for the thread to finish
            thread_to_join.join()
            
            logging.info(f"Final total token usage for the session: {self.get_total_tokens()}")
            logging.info("Token usage tracker stopped.")
