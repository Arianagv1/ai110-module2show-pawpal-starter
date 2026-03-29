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
        self.task_id = task_id
        self.description = description
        self.time = time
        self.frequency = frequency
        self.completed = completed

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        self.completed = False

    def is_due_today(self) -> bool:
        """Return True for daily tasks or any task scheduled for today."""
        return self.frequency.lower() == "daily"

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
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.breed = breed
        self.date_of_birth = date_of_birth
        self.weight = weight
        self.health_status = health_status
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if not t.completed]

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
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

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

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        pet = self.owner.get_pet_by_id(pet_id)
        return pet.get_tasks() if pet else []

    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.get_all_tasks() if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        return [t for t in self.get_all_tasks() if t.completed]

    def get_tasks_by_frequency(self, frequency: str) -> list[Task]:
        return [t for t in self.get_all_tasks() if t.frequency.lower() == frequency.lower()]

    def get_todays_schedule(self) -> list[Task]:
        return [t for t in self.get_all_tasks() if t.is_due_today()]

    def organize_by_time(self) -> list[Task]:
        return sorted(self.get_all_tasks(), key=lambda t: t.time)

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