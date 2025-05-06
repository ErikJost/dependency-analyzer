#!/usr/bin/env python3
"""
Streaming support for the MCP server.

This module provides utilities for streaming responses from long-running operations
to clients in both HTTP and stdio modes.
"""

import sys
import json
import uuid
import time
import threading
from typing import Dict, Any, Optional, Callable, Iterator, List

from structured_logging import get_logger, create_correlation_id

# Configure logging
logger = get_logger("mcp_streaming", "INFO")

class StreamingOperation:
    """Class to manage streaming operations with progress updates."""
    
    def __init__(self, operation_id: str = None, correlation_id: str = None):
        """Initialize a streaming operation."""
        self.operation_id = operation_id or str(uuid.uuid4())
        self.correlation_id = correlation_id or create_correlation_id()
        self.start_time = time.time()
        self.status = "initializing"  # initializing, running, completed, cancelled, failed
        self.progress = 0.0  # 0.0 to 1.0
        self.result = None
        self.error = None
        self.messages: List[Dict[str, Any]] = []
        self.cancelled = False
        self._lock = threading.Lock()
        self._task = None
        
        # Initialize logger with correlation ID
        self.logger = logger.with_correlation_id(self.correlation_id)
        self.logger.info(
            f"Streaming operation created: {self.operation_id}",
            operation_id=self.operation_id
        )
    
    def start_task(self, task_func: Callable, *args, **kwargs) -> None:
        """Start the task in a background thread."""
        self.status = "running"
        
        def wrapper_func():
            try:
                self.logger.info(
                    f"Starting task for operation: {self.operation_id}",
                    operation_id=self.operation_id
                )
                
                # Allow the task function to update progress
                result = task_func(self, *args, **kwargs)
                
                with self._lock:
                    if self.cancelled:
                        self.logger.info(
                            f"Task was cancelled: {self.operation_id}",
                            operation_id=self.operation_id
                        )
                        return
                    
                    self.result = result
                    self.status = "completed"
                    self.progress = 1.0
                    
                    self.logger.info(
                        f"Task completed: {self.operation_id}",
                        operation_id=self.operation_id,
                        duration=time.time() - self.start_time
                    )
            except Exception as e:
                import traceback
                
                with self._lock:
                    self.error = {
                        "message": str(e),
                        "traceback": traceback.format_exc()
                    }
                    self.status = "failed"
                    
                    self.logger.error(
                        f"Task failed: {self.operation_id} - {str(e)}",
                        operation_id=self.operation_id,
                        error=str(e),
                        traceback=traceback.format_exc()
                    )
        
        self._task = threading.Thread(target=wrapper_func)
        self._task.daemon = True
        self._task.start()
    
    def update_progress(self, progress: float, message: Optional[str] = None) -> None:
        """Update the progress of the operation."""
        if progress < 0.0 or progress > 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        with self._lock:
            if self.cancelled:
                return
            
            self.progress = progress
            
            if message:
                self.add_message(message)
                
                self.logger.debug(
                    f"Progress update: {self.operation_id} - {progress:.2f}",
                    operation_id=self.operation_id,
                    progress=progress,
                    message=message
                )
            else:
                self.logger.debug(
                    f"Progress update: {self.operation_id} - {progress:.2f}",
                    operation_id=self.operation_id,
                    progress=progress
                )
    
    def add_message(self, message: str, message_type: str = "info") -> None:
        """Add a message to the operation log."""
        with self._lock:
            if self.cancelled:
                return
            
            message_entry = {
                "timestamp": time.time(),
                "type": message_type,
                "message": message
            }
            self.messages.append(message_entry)
            
            self.logger.debug(
                f"Message added: {self.operation_id} - {message}",
                operation_id=self.operation_id,
                message_type=message_type
            )
    
    def cancel(self) -> bool:
        """Cancel the operation."""
        with self._lock:
            if self.status in ["completed", "failed"]:
                return False
            
            self.cancelled = True
            self.status = "cancelled"
            
            self.logger.info(
                f"Operation cancelled: {self.operation_id}",
                operation_id=self.operation_id,
                duration=time.time() - self.start_time
            )
            
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the operation."""
        with self._lock:
            elapsed_time = time.time() - self.start_time
            
            status = {
                "operation_id": self.operation_id,
                "correlation_id": self.correlation_id,
                "status": self.status,
                "progress": self.progress,
                "elapsed_time": elapsed_time,
                "timestamp": time.time()
            }
            
            if self.status == "completed" and self.result is not None:
                status["result"] = self.result
            
            if self.status == "failed" and self.error is not None:
                status["error"] = self.error
            
            if self.messages:
                status["messages"] = self.messages
            
            return status

class StreamingManager:
    """Manager for streaming operations."""
    
    def __init__(self):
        """Initialize the streaming manager."""
        self.operations: Dict[str, StreamingOperation] = {}
        self._lock = threading.Lock()
        self.logger = get_logger("mcp_streaming_manager", "INFO")
        
        # Clean up completed operations periodically
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start a thread to clean up old completed operations."""
        def cleanup_task():
            while True:
                time.sleep(300)  # Run every 5 minutes
                self._cleanup_old_operations()
        
        cleanup_thread = threading.Thread(target=cleanup_task)
        cleanup_thread.daemon = True
        cleanup_thread.start()
    
    def _cleanup_old_operations(self, max_age: float = 3600) -> None:
        """Clean up operations that have been completed for a while."""
        current_time = time.time()
        operations_to_remove = []
        
        with self._lock:
            for op_id, operation in self.operations.items():
                if operation.status in ["completed", "failed", "cancelled"]:
                    if current_time - operation.start_time > max_age:
                        operations_to_remove.append(op_id)
            
            for op_id in operations_to_remove:
                del self.operations[op_id]
                
                self.logger.info(
                    f"Cleaned up old operation: {op_id}",
                    operation_id=op_id
                )
    
    def create_operation(self, operation_id: Optional[str] = None, correlation_id: Optional[str] = None) -> StreamingOperation:
        """Create a new streaming operation."""
        operation = StreamingOperation(operation_id, correlation_id)
        
        with self._lock:
            self.operations[operation.operation_id] = operation
        
        self.logger.info(
            f"Created new operation: {operation.operation_id}",
            operation_id=operation.operation_id,
            correlation_id=operation.correlation_id
        )
        
        return operation
    
    def get_operation(self, operation_id: str) -> Optional[StreamingOperation]:
        """Get an operation by ID."""
        with self._lock:
            return self.operations.get(operation_id)
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an operation by ID."""
        with self._lock:
            operation = self.operations.get(operation_id)
            
            if operation:
                cancelled = operation.cancel()
                
                self.logger.info(
                    f"Attempted to cancel operation: {operation_id}",
                    operation_id=operation_id,
                    cancelled=cancelled
                )
                
                return cancelled
            
            return False
    
    def get_all_operations(self) -> List[Dict[str, Any]]:
        """Get status for all operations."""
        with self._lock:
            return [op.get_status() for op in self.operations.values()]

# Create a global streaming manager
streaming_manager = StreamingManager()

def stream_over_stdio(operation: StreamingOperation, interval: float = 0.5) -> None:
    """Stream updates for an operation over stdio."""
    last_status = {}
    
    while True:
        status = operation.get_status()
        
        # Send updates only when something has changed
        if status != last_status:
            response = {
                "streaming_update": True,
                "data": status,
                "request_id": status["operation_id"],
                "correlation_id": status["correlation_id"]
            }
            
            print(json.dumps(response), flush=True)
            last_status = status
        
        # If the operation is done, exit the streaming loop
        if status["status"] in ["completed", "failed", "cancelled"]:
            break
        
        time.sleep(interval)

def execute_streaming_operation(
    task_func: Callable, 
    params: Dict[str, Any], 
    operation_id: Optional[str] = None, 
    correlation_id: Optional[str] = None
) -> StreamingOperation:
    """
    Execute a long-running operation with streaming updates.
    
    Args:
        task_func: The function to execute
        params: Parameters to pass to the function
        operation_id: Optional operation ID
        correlation_id: Optional correlation ID
        
    Returns:
        A StreamingOperation object
    """
    # Create a streaming operation
    operation = streaming_manager.create_operation(operation_id, correlation_id)
    
    # Start the task
    operation.start_task(task_func, **params)
    
    return operation 