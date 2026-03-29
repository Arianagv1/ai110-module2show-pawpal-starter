from __future__ import annotations
from datetime import date, time
# ---------------------------------------------------------------------------
# Task — represents a single pet care activity
# ---------------------------------------------------------------------------
class Task:
    """Represents a single pet care activity."""
    def __init__(
        self,
        task_id: str,
        description: str,
        time: time,
        frequency: str,
        completed: bool = False,
    ):

        """Initialise a Task with its id, description, scheduled time, frequency, and completion state."""

        self.task_id = task_id
        self.description = description
        self.time = time
        self.frequency = frequency
        self.completed = completed

        """Mark this task as completed."""
    def mark_complete(self) -> None:
        self.completed = True

        """Mark this task as incomplete."""
    def mark_incomplete(self) -> None:
        self.completed = False

    def is_due_today(self) -> bool:
        """Return True for daily tasks or any task scheduled for today."""
        return self.frequency.lower() == "daily"
    
        """Return a dictionary containing all fields of this task."""
    def get_task_info(self) -> dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "completed": self.completed,
        }
# ---------------------------------------------------------------------------
# Pet — stores pet details and a list of tasks
# ---------------------------------------------------------------------------
class Pet:
    """Stores pet details and manages a list of Tasks."""
    def __init__(
        self,
        pet_id: str,
        name: str,
        species: str,
        breed: str,
        date_of_birth: date,
        weight: float,
        health_status: str,
    ):
        
        """Initialise a Pet with identifying info, physical details, and an empty task list."""
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.breed = breed
        self.date_of_birth = date_of_birth
        self.weight = weight
        self.health_status = health_status
        self.tasks: list[Task] = []

        """Append a Task to this pet's task list."""
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

        """Remove the task with the given id from this pet's task list."""
    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

        """Return the full list of tasks assigned to this pet."""
    def get_tasks(self) -> list[Task]:
        return self.tasks
        
        """Return tasks that have not yet been marked complete."""
    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if not t.completed]
    
        """Return a dictionary containing all profile fields for this pet."""
    def get_pet_info(self) -> dict:
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "date_of_birth": self.date_of_birth,
            "weight": self.weight,
            "health_status": self.health_status,
        }
    

    """Placeholder for updating this pet's profile fields (not yet implemented)."""
    def update_pet_info(self) -> None:
        pass
# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides access to all their tasks
# ---------------------------------------------------------------------------
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    def __init__(
        self,
        owner_id: str,
        name: str,
        email: str,
    ):
        
        """Initialise an Owner with a unique id, display name, email, and an empty pet list."""
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

        """Add a Pet to this owner's roster."""
    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

        """Remove the pet with the given id from this owner's roster."""
    def remove_pet(self, pet_id: str) -> None:
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

        """Return the full list of pets belonging to this owner."""
    def get_pets(self) -> list[Pet]:
        return self.pets
    
    def get_pet_by_id(self, pet_id: str) -> Pet | None:
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None
    
    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets owned by this owner."""
        return [task for pet in self.pets for task in pet.tasks]
    

        """Placeholder for updating the owner's profile fields (not yet implemented)."""
    def update_profile(self) -> None:
        pass
# ---------------------------------------------------------------------------
# Scheduler — the 'brain' that retrieves, organizes, and manages tasks
# ---------------------------------------------------------------------------
class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Delegate to Owner to retrieve every task across all pets."""
        return self.owner.get_all_tasks()
        """Return all tasks belonging to the pet identified by pet_id."""
    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        pet = self.owner.get_pet_by_id(pet_id)
        return pet.get_tasks() if pet else []
    
        """Return all incomplete tasks across every pet owned by this owner."""
    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.get_all_tasks() if not t.completed]
        
        """Return all completed tasks across every pet owned by this owner."""
    def get_completed_tasks(self) -> list[Task]:
        return [t for t in self.get_all_tasks() if t.completed]
        
        """Return tasks whose frequency matches the given string (case-insensitive)."""
    def get_tasks_by_frequency(self, frequency: str) -> list[Task]:
        return [t for t in self.get_all_tasks() if t.frequency.lower() == frequency.lower()]
        
        """Return tasks whose frequency matches the given string (case-insensitive)."""
    def get_todays_schedule(self) -> list[Task]:
        return [t for t in self.get_all_tasks() if t.is_due_today()]
        
        """Return all tasks sorted in ascending order by their scheduled time."""
    def organize_by_time(self) -> list[Task]:
        return sorted(self.get_all_tasks(), key=lambda t: t.time)
        
    """Find the task matching task_id across all pets and mark it complete."""
    def mark_task_complete(self, task_id: str) -> None:
        for task in self.get_all_tasks():
            if task.task_id == task_id:
                task.mark_complete()
                return
            
    def generate_daily_plan(self) -> list[Task]:
        """Return today's pending tasks sorted by scheduled time."""
        return sorted(
            [t for t in self.get_todays_schedule() if not t.completed],
            key=lambda t: t.time,
        )