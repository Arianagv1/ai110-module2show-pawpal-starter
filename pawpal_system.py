from __future__ import annotations
from collections import defaultdict
from datetime import date, time, timedelta
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
        due_date: date | None = None,
    ):

        self.task_id = task_id
        self.description = description
        self.time = time
        self.frequency = frequency
        self.completed = completed
        self.due_date = due_date  # explicit calendar date for the next occurrence (None = unscheduled)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.completed = False

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today.
        When a specific due_date has been set (e.g. after auto-rescheduling),
        the task is due only on that exact calendar date.  Otherwise fall back
        to the old behaviour: daily tasks are always considered due today.
        """
        if self.due_date is not None:
            return self.due_date == date.today()
        return self.frequency.lower() == "daily"

    def get_task_info(self) -> dict:
        """Return a dictionary containing all fields of this task."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "completed": self.completed,
            "due_date": self.due_date,
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
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return the full list of tasks assigned to this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that have not yet been marked complete."""
        return [t for t in self.tasks if not t.completed]

    def get_pet_info(self) -> dict:
        """Return a dictionary containing all profile fields for this pet."""
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
        """Placeholder for updating this pet's profile fields (not yet implemented)."""
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
        """Add a Pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given id from this owner's roster."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Return the full list of pets belonging to this owner."""
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
        """Placeholder for updating the owner's profile fields (not yet implemented)."""
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
        """Return all tasks belonging to the pet identified by pet_id."""
        pet = self.owner.get_pet_by_id(pet_id)
        return pet.get_tasks() if pet else []

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks across every pet owned by this owner."""
        return [t for t in self.get_all_tasks() if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all completed tasks across every pet owned by this owner."""
        return [t for t in self.get_all_tasks() if t.completed]

    def get_tasks_by_frequency(self, frequency: str) -> list[Task]:
        """Return tasks whose frequency matches the given string (case-insensitive)."""
        return [t for t in self.get_all_tasks() if t.frequency.lower() == frequency.lower()]

    def get_todays_schedule(self) -> list[Task]:
        """Return all tasks due today."""
        return [t for t in self.get_all_tasks() if t.is_due_today()]

    def organize_by_time(self) -> list[Task]:
        """Return all tasks sorted in ascending order by their scheduled time."""
        return sorted(self.get_all_tasks(), key=lambda t: t.time)
    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Filter tasks by completion status and/or pet name.

        Parameters
        ----------
        completed : bool | None
            If True, return only completed tasks.
            If False, return only pending tasks.
            If None (default), do not filter by completion status.
        pet_name : str | None
            If provided, return only tasks belonging to the pet with this name
            (case-insensitive).  If None (default), include tasks for all pets.
        """
        return [
            task
            for pet in self.owner.get_pets()
            if pet_name is None or pet.name.lower() == pet_name.lower()
            for task in pet.get_tasks()
            if completed is None or task.completed == completed
        ]
        
    def mark_task_complete(self, task_id: str) -> None:
        """Find the task matching task_id across all pets and mark it complete.

        For tasks with frequency "daily" or "weekly" a new Task is automatically
        created and added to the same pet, representing the next occurrence:
        * daily  → due_date = today + 1 day   (timedelta(days=1))
        * weekly → due_date = today + 7 days  (timedelta(weeks=1))
        The new task's id is derived as  "<original_id>_<YYYYMMDD>"  where the
        date is the computed next-occurrence date.
        """
        all_pet_tasks = (
            (pet, task)
            for pet in self.owner.get_pets()
            for task in pet.get_tasks()
        )
        pet, task = next(
            ((p, t) for p, t in all_pet_tasks if t.task_id == task_id),
            (None, None),
        )
        if task is None:
            return
        task.mark_complete()
        delta = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}.get(task.frequency.lower())
        if delta is None:
            return  # one-off task — no recurrence needed
        next_date = date.today() + delta
        pet.add_task(Task(
            f"{task.task_id}_{next_date.strftime('%Y%m%d')}",
            task.description,
            task.time,
            task.frequency,
            due_date=next_date,
        ))

    def detect_conflicts(self) -> list[str]:
        """Detect tasks scheduled at the same time across all pets.

        Returns a (possibly empty) list of human-readable warning strings —
        one per conflicting time slot.  An empty list means the schedule is clean.
        """
        time_map: defaultdict[time, list[tuple[str, Task]]] = defaultdict(list)
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                time_map[task.time].append((pet.name, task))
        return [
            f"⚠️  Conflict at {slot.strftime('%H:%M')}: "
            + ", ".join(f"{name} → {t.description}" for name, t in entries)
            for slot, entries in sorted(time_map.items())
            if len(entries) > 1
        ]

    def generate_daily_plan(self) -> list[Task]:
        """Return today's pending tasks sorted by scheduled time."""
        return sorted(
            [t for t in self.get_todays_schedule() if not t.completed],
            key=lambda t: t.time,
        )