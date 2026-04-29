from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Scheduler, Task

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

# ---------------------------------------------------------------------------
# Helpers shared by recurrence tests
# ---------------------------------------------------------------------------
def _make_scheduler(frequency: str) -> tuple:
    """Return (scheduler, pet, original_task) wired up with one task."""
    owner = Owner("o1", "Test Owner", "owner@example.com")
    pet = Pet("p1", "Daisy", "dog", "Shihtzu", date(2020, 3, 15), 10.5, "healthy")
    initial_task = Task("t1", "Morning walk", time(7, 0), frequency)
    pet.add_task(initial_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    return scheduler, pet, initial_task

def test_daily_task_creates_next_occurrence():
    """Completing a daily task should auto-add a new task due tomorrow."""
    scheduler, pet, original = _make_scheduler("daily")
    scheduler.mark_task_complete("t1")
    assert original.completed is True
    assert len(pet.get_tasks()) == 2  # original + one new task
    next_task = pet.get_tasks()[1]
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.description == original.description
    assert next_task.time == original.time
    assert next_task.frequency == original.frequency

def test_weekly_task_creates_next_occurrence():
    """Completing a weekly task should auto-add a new task due in 7 days."""
    scheduler, pet, original = _make_scheduler("weekly")
    scheduler.mark_task_complete("t1")
    assert original.completed is True
    assert len(pet.get_tasks()) == 2
    next_task = pet.get_tasks()[1]
    assert next_task.due_date == date.today() + timedelta(weeks=1)

def test_once_task_does_not_recur():
    """Completing a one-off ('once') task should NOT create a next occurrence."""
    scheduler, pet, original = _make_scheduler("once")
    scheduler.mark_task_complete("t1")
    assert original.completed is True
    assert len(pet.get_tasks()) == 1  # no new task added

def test_recurring_task_id_contains_next_date():
    """The auto-created task id should encode the next due date (YYYYMMDD)."""
    scheduler, pet, _ = _make_scheduler("daily")
    scheduler.mark_task_complete("t1")
    expected_date_str = (date.today() + timedelta(days=1)).strftime("%Y%m%d")
    next_task = pet.get_tasks()[1]
    assert expected_date_str in next_task.task_id

def test_due_date_field_in_task_info():
    """get_task_info() should include the due_date key."""
    task = Task("t1", "Morning walk", time(7, 0), "daily", due_date=date(2026, 4, 1))
    info = task.get_task_info()
    assert "due_date" in info
    assert info["due_date"] == date(2026, 4, 1)

def test_is_due_today_with_due_date():
    """is_due_today() should use due_date when it is set."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    task_today = Task("t1", "Walk", time(7, 0), "daily", due_date=today)
    task_tomorrow = Task("t2", "Walk", time(7, 0), "daily", due_date=tomorrow)
    assert task_today.is_due_today() is True
    assert task_tomorrow.is_due_today() is False

def test_is_due_today_without_due_date_daily():
    """is_due_today() without due_date should return True for daily frequency."""
    task = Task("t1", "Walk", time(7, 0), "daily")
    assert task.is_due_today() is True



# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------
def _make_owner_with_pets(*pets):
    """Helper: create an Owner with the given Pet objects and return a Scheduler."""
    owner = Owner("o99", "Test", "t@example.com")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)

def test_detect_conflicts_no_conflicts():
    """detect_conflicts() returns an empty list when all task times are unique."""
    pet = Pet("p1", "Daisy", "dog", "Shihtzu", date(2020, 3, 15), 10.5, "healthy")
    pet.add_task(Task("t1", "Walk",      time(7,  0), "daily"))
    pet.add_task(Task("t2", "Breakfast", time(8,  0), "daily"))
    pet.add_task(Task("t3", "Dinner",    time(18, 0), "daily"))
    scheduler = _make_owner_with_pets(pet)
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_same_pet():
    """detect_conflicts() flags two tasks for the same pet at the same time."""
    pet = Pet("p1", "Daisy", "dog", "Shihtzu", date(2020, 3, 15), 10.5, "healthy")
    pet.add_task(Task("t1", "Walk",    time(7, 0), "daily"))
    pet.add_task(Task("t2", "Bath",    time(7, 0), "weekly"))  # same time as t1
    scheduler = _make_owner_with_pets(pet)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "07:00" in warnings[0]
    assert "Daisy" in warnings[0]

def test_detect_conflicts_cross_pet():
    """detect_conflicts() flags tasks from different pets at the same time."""
    pet1 = Pet("p1", "Daisy", "dog", "Shihtzu",      date(2020, 3, 15), 10.5, "healthy")
    pet2 = Pet("p2", "Dolly", "cat", "Orange Tabby",  date(2019, 7,  4), 15.2, "healthy")
    pet1.add_task(Task("t1", "Morning walk",    time(8, 0), "daily"))
    pet2.add_task(Task("t2", "Feed breakfast",  time(8, 0), "daily"))  # same slot
    scheduler = _make_owner_with_pets(pet1, pet2)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Daisy" in warnings[0]
    assert "Dolly" in warnings[0]

def test_detect_conflicts_multiple_slots():
    """detect_conflicts() reports every conflicting time slot, not just the first."""
    pet = Pet("p1", "Daisy", "dog", "Shihtzu", date(2020, 3, 15), 10.5, "healthy")
    pet.add_task(Task("t1", "Walk A",   time(7,  0), "daily"))
    pet.add_task(Task("t2", "Walk B",   time(7,  0), "daily"))  # conflict 1
    pet.add_task(Task("t3", "Bath A",   time(17, 0), "weekly"))
    pet.add_task(Task("t4", "Bath B",   time(17, 0), "weekly"))  # conflict 2
    scheduler = _make_owner_with_pets(pet)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 2
    assert any("07:00" in w for w in warnings)
    assert any("17:00" in w for w in warnings)
    
def test_detect_conflicts_returns_list_of_strings():
    """detect_conflicts() always returns a list (never raises, never returns None)."""
    owner = Owner("o1", "Empty", "e@example.com")
    scheduler = Scheduler(owner)
    result = scheduler.detect_conflicts()
    assert isinstance(result, list)
    assert result == []


# ---------------------------------------------------------------------------
# filter_tasks tests
# ---------------------------------------------------------------------------
def _make_filter_scheduler() -> Scheduler:
    """Return a Scheduler with two pets, each holding one complete and one pending task."""
    owner = Owner("o1", "Test Owner", "owner@example.com")

    daisy = Pet("p1", "Daisy", "dog", "Shih Tzu", date(2020, 3, 15), 10.5, "healthy")
    daisy.add_task(Task("d1", "Morning walk",   time(7,  0), "daily"))   # pending
    daisy.add_task(Task("d2", "Evening walk",   time(18, 0), "daily"))   # will be completed

    dolly = Pet("p2", "Dolly", "cat", "Tabby", date(2019, 7, 4), 4.2, "healthy")
    dolly.add_task(Task("c1", "Feed breakfast", time(8,  0), "daily"))   # pending
    dolly.add_task(Task("c2", "Brush fur",      time(17, 0), "weekly"))  # will be completed

    daisy.get_tasks()[1].mark_complete()   # d2 → completed
    dolly.get_tasks()[1].mark_complete()   # c2 → completed

    owner.add_pet(daisy)
    owner.add_pet(dolly)
    return Scheduler(owner)


def test_filter_tasks_no_filters_returns_all():
    """filter_tasks() with no arguments should return every task across all pets."""
    scheduler = _make_filter_scheduler()
    result = scheduler.filter_tasks()
    assert len(result) == 4


def test_filter_tasks_completed_true():
    """filter_tasks(completed=True) should return only completed tasks."""
    scheduler = _make_filter_scheduler()
    result = scheduler.filter_tasks(completed=True)
    assert len(result) == 2
    assert all(t.completed is True for t in result)


def test_filter_tasks_completed_false():
    """filter_tasks(completed=False) should return only pending tasks."""
    scheduler = _make_filter_scheduler()
    result = scheduler.filter_tasks(completed=False)
    assert len(result) == 2
    assert all(t.completed is False for t in result)


def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) should return only tasks for that pet."""
    scheduler = _make_filter_scheduler()
    result = scheduler.filter_tasks(pet_name="Daisy")
    assert len(result) == 2
    assert all(t.task_id.startswith("d") for t in result)


def test_filter_tasks_by_pet_name_case_insensitive():
    """pet_name matching should be case-insensitive."""
    scheduler = _make_filter_scheduler()
    assert scheduler.filter_tasks(pet_name="daisy") == scheduler.filter_tasks(pet_name="Daisy")


def test_filter_tasks_combined_completed_and_pet_name():
    """filter_tasks(completed=True, pet_name=...) should apply both filters."""
    scheduler = _make_filter_scheduler()
    result = scheduler.filter_tasks(completed=True, pet_name="Daisy")
    assert len(result) == 1
    assert result[0].task_id == "d2"


def test_filter_tasks_unknown_pet_name_returns_empty():
    """filter_tasks() with a pet name that doesn't exist should return an empty list."""
    scheduler = _make_filter_scheduler()
    result = scheduler.filter_tasks(pet_name="Ghost")
    assert result == []


# ---------------------------------------------------------------------------
# Edge-case tests for mark_task_complete and get_pet_by_id
# ---------------------------------------------------------------------------
def test_mark_task_complete_unknown_id_does_nothing():
    """mark_task_complete() with a non-existent task_id should not raise or alter state."""
    scheduler, pet, _ = _make_scheduler("daily")
    original_count = len(pet.get_tasks())
    scheduler.mark_task_complete("does_not_exist")
    assert len(pet.get_tasks()) == original_count  # no new task appended


def test_get_pet_by_id_returns_none_for_missing_id():
    """get_pet_by_id() should return None when no pet matches the given id."""
    owner = Owner("o1", "Test Owner", "owner@example.com")
    owner.add_pet(Pet("p1", "Daisy", "dog", "Shih Tzu", date(2020, 3, 15), 10.5, "healthy"))
    assert owner.get_pet_by_id("does_not_exist") is None


def test_get_pet_by_id_returns_correct_pet():
    """get_pet_by_id() should return the matching Pet object."""
    owner = Owner("o1", "Test Owner", "owner@example.com")
    pet = Pet("p1", "Daisy", "dog", "Shih Tzu", date(2020, 3, 15), 10.5, "healthy")
    owner.add_pet(pet)
    assert owner.get_pet_by_id("p1") is pet


    