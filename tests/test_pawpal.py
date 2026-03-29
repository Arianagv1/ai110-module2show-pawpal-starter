from datetime import date, time
from pawpal_system import Pet, Task

def test_mark_complete():
    """mark_complete() should set task.completed from False to True."""
    task = Task("t1", "Morning walk", time(7, 0), "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True

def test_add_task_increases_count():
    """Adding a task to a pet should increase that pet's task count by one."""
    pet = Pet("p1", "Daisy", "dog", "Shihtzu", date(2020, 3, 15), 10.5, "healthy")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("t2", "Feed breakfast", time(8, 0), "daily"))
    assert len(pet.get_tasks()) == 1
