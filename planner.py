import os
import json
import datetime
from typing import Dict, List, Any, Optional
import sys

class Task:
    def __init__(self, description: str, time: str = "", completed: bool = False, task_id: Optional[int] = None):
        self.id = task_id if task_id is not None else int(datetime.datetime.now().timestamp())
        self.description = description
        self.time = time
        self.completed = completed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "time": self.time,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            description=data["description"],
            time=data.get("time", ""),
            completed=data.get("completed", False),
            task_id=data.get("id")
        )


class DailyPlanner:
    def __init__(self, data_file: str = "planner_data.json"):
        self.data_file = data_file
        self.tasks: Dict[str, List[Task]] = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Load tasks from the data file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    for date, tasks in data.items():
                        self.tasks[date] = [Task.from_dict(task) for task in tasks]
            except (json.JSONDecodeError, KeyError):
                print("Error loading planner data. Starting with empty planner.")
                self.tasks = {}
    
    def save_data(self) -> None:
        """Save tasks to the data file."""
        data = {}
        for date, tasks in self.tasks.items():
            data[date] = [task.to_dict() for task in tasks]
        
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_date_key(self, date: Optional[datetime.date] = None) -> str:
        """Get string key for the provided date."""
        if date is None:
            date = datetime.date.today()
        return date.isoformat()
    
    def add_task(self, description: str, time: str = "", date: Optional[datetime.date] = None) -> None:
        """Add a new task for the specified date."""
        date_key = self.get_date_key(date)
        
        if date_key not in self.tasks:
            self.tasks[date_key] = []
        
        task = Task(description=description, time=time)
        self.tasks[date_key].append(task)
        self.save_data()
        print(f"Task added: {description}")
    
    def get_tasks(self, date: Optional[datetime.date] = None) -> List[Task]:
        """Get all tasks for the specified date."""
        date_key = self.get_date_key(date)
        return self.tasks.get(date_key, [])
    
    def complete_task(self, task_id: int, date: Optional[datetime.date] = None) -> bool:
        """Mark a task as completed."""
        date_key = self.get_date_key(date)
        
        if date_key in self.tasks:
            for task in self.tasks[date_key]:
                if task.id == task_id:
                    task.completed = not task.completed
                    status = "completed" if task.completed else "uncompleted"
                    print(f"Task '{task.description}' marked as {status}.")
                    self.save_data()
                    return True
        
        print("Task not found.")
        return False
    
    def update_task(self, task_id: int, description: str = None, time: str = None, date: Optional[datetime.date] = None) -> bool:
        """Update a task's details."""
        date_key = self.get_date_key(date)
        
        if date_key in self.tasks:
            for task in self.tasks[date_key]:
                if task.id == task_id:
                    if description:
                        task.description = description
                    if time is not None:
                        task.time = time
                    print(f"Task updated: {task.description}")
                    self.save_data()
                    return True
        
        print("Task not found.")
        return False
    
    def delete_task(self, task_id: int, date: Optional[datetime.date] = None) -> bool:
        """Delete a task."""
        date_key = self.get_date_key(date)
        
        if date_key in self.tasks:
            for i, task in enumerate(self.tasks[date_key]):
                if task.id == task_id:
                    deleted_task = self.tasks[date_key].pop(i)
                    print(f"Task deleted: {deleted_task.description}")
                    self.save_data()
                    return True
        
        print("Task not found.")
        return False
    
    def display_tasks(self, date: Optional[datetime.date] = None) -> None:
        """Display tasks for the specified date."""
        if date is None:
            date = datetime.date.today()
        
        date_key = self.get_date_key(date)
        tasks = self.tasks.get(date_key, [])
        
        date_str = date.strftime("%A, %B %d, %Y")
        print(f"\n--- Tasks for {date_str} ---")
        
        if not tasks:
            print("No tasks scheduled for today.")
            return
        
        # Sort tasks by time
        tasks.sort(key=lambda t: t.time if t.time else "23:59")
        
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.completed else " "
            time_str = f"{task.time} - " if task.time else ""
            print(f"{i}. [{status}] {time_str}{task.description} (ID: {task.id})")
    
    def display_week(self, start_date: Optional[datetime.date] = None) -> None:
        """Display tasks for the week starting from start_date."""
        if start_date is None:
            # Start from current week's Monday
            today = datetime.date.today()
            start_date = today - datetime.timedelta(days=today.weekday())
        
        print("\n--- Weekly Schedule ---")
        for i in range(7):
            current_date = start_date + datetime.timedelta(days=i)
            self.display_tasks(current_date)
            print()


def parse_date(date_str: str) -> datetime.date:
    """Parse date from string in format YYYY-MM-DD."""
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return datetime.date.today()


def print_help() -> None:
    """Print help information."""
    print("\nDaily Planner Commands:")
    print("  add <description> [time] [date]    Add a new task")
    print("  list [date]                        List tasks for a date (default: today)")
    print("  week [start_date]                  Display weekly schedule")
    print("  complete <task_id>                 Mark a task as completed/uncompleted")
    print("  update <task_id> <description>     Update task description")
    print("  time <task_id> <time>              Update task time (format: HH:MM)")
    print("  delete <task_id>                   Delete a task")
    print("  help                               Show this help message")
    print("  exit                               Exit the planner")
    print("\nDates should be in format YYYY-MM-DD")
    print("Times should be in 24-hour format HH:MM")


def main() -> None:
    planner = DailyPlanner()
    
    print("=== Daily Planner ===")
    print("Type 'help' for a list of commands.")
    
    # Show today's tasks on startup
    planner.display_tasks()
    
    while True:
        try:
            user_input = input("\nPlanner> ").strip()
            
            if not user_input:
                continue
                
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == "exit":
                print("Goodbye!")
                break
                
            elif command == "help":
                print_help()
                
            elif command == "add":
                if len(parts) < 2:
                    print("Usage: add <description> [time] [date]")
                    continue
                
                description = " ".join(parts[1:])
                time = ""
                date = None
                
                # Check if the last part is a date
                if len(parts) >= 3 and "-" in parts[-1] and parts[-1].count("-") == 2:
                    date = parse_date(parts[-1])
                    description = " ".join(parts[1:-1])
                
                # Check if there's a time (format HH:MM)
                for i, part in enumerate(parts[1:], 1):
                    if ":" in part and len(part) == 5 and part[2] == ":":
                        try:
                            # Validate time format
                            hour, minute = map(int, part.split(":"))
                            if 0 <= hour <= 23 and 0 <= minute <= 59:
                                time = part
                                description = " ".join(parts[1:i] + parts[i+1:])
                                if date is not None:
                                    description = " ".join(description.split()[:-1])
                                break
                        except ValueError:
                            pass
                
                planner.add_task(description, time, date)
                
            elif command == "list":
                date = None
                if len(parts) > 1:
                    date = parse_date(parts[1])
                planner.display_tasks(date)
                
            elif command == "week":
                start_date = None
                if len(parts) > 1:
                    start_date = parse_date(parts[1])
                planner.display_week(start_date)
                
            elif command == "complete":
                if len(parts) != 2:
                    print("Usage: complete <task_id>")
                    continue
                try:
                    task_id = int(parts[1])
                    planner.complete_task(task_id)
                except ValueError:
                    print("Task ID must be a number.")
                
            elif command == "update":
                if len(parts) < 3:
                    print("Usage: update <task_id> <new description>")
                    continue
                try:
                    task_id = int(parts[1])
                    description = " ".join(parts[2:])
                    planner.update_task(task_id, description=description)
                except ValueError:
                    print("Task ID must be a number.")
                
            elif command == "time":
                if len(parts) != 3:
                    print("Usage: time <task_id> <time>")
                    continue
                try:
                    task_id = int(parts[1])
                    time = parts[2]
                    planner.update_task(task_id, time=time)
                except ValueError:
                    print("Task ID must be a number.")
                
            elif command == "delete":
                if len(parts) != 2:
                    print("Usage: delete <task_id>")
                    continue
                try:
                    task_id = int(parts[1])
                    planner.delete_task(task_id)
                except ValueError:
                    print("Task ID must be a number.")
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting planner...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()