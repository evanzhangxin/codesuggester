#!/usr/bin/env python3
"""
Complex example Python file for testing advanced code suggestions.
This file contains complex Python constructs including decorators, context managers,
generators, and advanced type hints.
"""

import asyncio
import contextlib
import functools
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any, Dict, List, Optional, Union, Callable, Iterator, 
    Generic, TypeVar, Protocol, AsyncIterator
)


# Type variables and protocols
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class Serializable(Protocol):
    """Protocol for serializable objects."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """Create object from dictionary."""
        ...


class Status(Enum):
    """Status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task data class with various field types."""
    id: str
    name: str
    status: Status = Status.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'metadata': self.metadata,
            'dependencies': self.dependencies,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            status=Status(data.get('status', Status.PENDING.value)),
            metadata=data.get('metadata', {}),
            dependencies=data.get('dependencies', []),
            created_at=data.get('created_at')
        )


class BaseProcessor(ABC, Generic[T]):
    """Abstract base processor class."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__class__.__name__}.{name}")
    
    @abstractmethod
    async def process(self, item: T) -> T:
        """Process an item."""
        pass
    
    @abstractmethod
    def validate(self, item: T) -> bool:
        """Validate an item."""
        pass


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
                    continue
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry failed without exception")
        return wrapper
    return decorator


@contextlib.asynccontextmanager
async def database_transaction():
    """Async context manager for database transactions."""
    transaction = None
    try:
        # Begin transaction
        transaction = "mock_transaction"
        yield transaction
        # Commit transaction
        print("Transaction committed")
    except Exception:
        # Rollback transaction
        if transaction:
            print("Transaction rolled back")
        raise
    finally:
        # Cleanup
        if transaction:
            print("Transaction cleanup")


class TaskProcessor(BaseProcessor[Task]):
    """Concrete task processor implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name)
        self.config = config
        self.processed_count = 0
    
    async def process(self, item: Task) -> Task:
        """Process a task asynchronously."""
        self.logger.info(f"Processing task {item.id}")
        
        # Simulate processing
        await asyncio.sleep(0.1)
        
        item.status = Status.PROCESSING
        
        # Some complex processing logic
        if item.metadata.get('simulate_error'):
            raise ValueError(f"Simulated error for task {item.id}")
        
        # Update task
        item.status = Status.COMPLETED
        item.metadata['processed_by'] = self.name
        item.metadata['processed_at'] = asyncio.get_event_loop().time()
        
        self.processed_count += 1
        return item
    
    def validate(self, item: Task) -> bool:
        """Validate a task."""
        return (
            item.id is not None and
            item.name is not None and
            isinstance(item.metadata, dict)
        )
    
    async def process_batch(self, tasks: List[Task]) -> List[Task]:
        """Process multiple tasks concurrently."""
        async def process_single(task: Task) -> Task:
            if not self.validate(task):
                raise ValueError(f"Invalid task: {task}")
            return await self.process(task)
        
        # Process tasks concurrently
        results = await asyncio.gather(
            *[process_single(task) for task in tasks],
            return_exceptions=True
        )
        
        # Filter out exceptions and return successful results
        processed_tasks = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Task processing failed: {result}")
            else:
                processed_tasks.append(result)
        
        return processed_tasks


class TaskManager:
    """Task manager with advanced features."""
    
    def __init__(self, processor: TaskProcessor):
        self.processor = processor
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
    
    def add_task(self, task: Task) -> None:
        """Add a task to the manager."""
        self.tasks[task.id] = task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[Status] = None) -> List[Task]:
        """List tasks, optionally filtered by status."""
        if status is None:
            return list(self.tasks.values())
        return [task for task in self.tasks.values() if task.status == status]
    
    async def process_tasks(self) -> None:
        """Process all pending tasks."""
        pending_tasks = self.list_tasks(Status.PENDING)
        
        if not pending_tasks:
            return
        
        async with database_transaction():
            processed_tasks = await self.processor.process_batch(pending_tasks)
            
            # Update tasks in storage
            for task in processed_tasks:
                self.tasks[task.id] = task
    
    @retry(max_attempts=3, delay=0.5)
    async def save_to_file(self, file_path: Path) -> None:
        """Save tasks to file with retry logic."""
        task_data = {
            'tasks': [task.to_dict() for task in self.tasks.values()],
            'metadata': {
                'total_tasks': len(self.tasks),
                'processor_name': self.processor.name,
                'processed_count': self.processor.processed_count
            }
        }
        
        # Write to file asynchronously
        with open(file_path, 'w') as f:
            json.dump(task_data, f, indent=2)
    
    @classmethod
    async def load_from_file(cls, file_path: Path, processor: TaskProcessor) -> 'TaskManager':
        """Load tasks from file."""
        manager = cls(processor)
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            for task_dict in data.get('tasks', []):
                task = Task.from_dict(task_dict)
                manager.add_task(task)
        
        return manager
    
    def task_generator(self, status: Optional[Status] = None) -> Iterator[Task]:
        """Generator for iterating over tasks."""
        for task in self.tasks.values():
            if status is None or task.status == status:
                yield task
    
    async def async_task_generator(self, status: Optional[Status] = None) -> AsyncIterator[Task]:
        """Async generator for iterating over tasks."""
        for task in self.task_generator(status):
            # Simulate async operation
            await asyncio.sleep(0.01)
            yield task


async def main():
    """Main async function demonstrating usage."""
    # Create processor and manager
    config = {'max_concurrent': 10, 'timeout': 30}
    processor = TaskProcessor("main_processor", config)
    manager = TaskManager(processor)
    
    # Create sample tasks
    sample_tasks = [
        Task(id=f"task_{i}", name=f"Sample Task {i}")
        for i in range(5)
    ]
    
    # Add tasks to manager
    for task in sample_tasks:
        manager.add_task(task)
    
    # Process tasks
    await manager.process_tasks()
    
    # Save results
    output_path = Path("task_results.json")
    await manager.save_to_file(output_path)
    
    # Display results
    completed_tasks = manager.list_tasks(Status.COMPLETED)
    print(f"Processed {len(completed_tasks)} tasks successfully")
    
    # Demonstrate async generator
    print("Task details:")
    async for task in manager.async_task_generator(Status.COMPLETED):
        print(f"  {task.id}: {task.name} ({task.status.value})")


def sync_main():
    """Synchronous main function."""
    print("Starting task processing demo...")
    asyncio.run(main())
    print("Demo completed!")


if __name__ == "__main__":
    sync_main()