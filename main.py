from datetime import date, time
from pawpal_system import Owner, Pet, Scheduler, Task
# ---------------------------------------------------------------------------
# Create owner
# ---------------------------------------------------------------------------
owner = Owner(
    owner_id="Ariana_1",
    name="Ariana",
    email="Ariana@example.com",
)
# ---------------------------------------------------------------------------
# Create pets and register them with the owner
# ---------------------------------------------------------------------------
Daisy = Pet(
    pet_id="pet_1",
    name="Daisy",
    species="dog",
    breed="Shihtzu",
    date_of_birth=date(2020, 3, 15),
    weight=16.5,
    health_status="healthy",
)
Dolly = Pet(
    pet_id="pet_2",
    name="Dolly",
    species="cat",
    breed="Orange Tabby",
    date_of_birth=date(2019, 7, 4),
    weight=15.2,
    health_status="healthy",
)
owner.add_pet(Daisy)
owner.add_pet(Dolly)
# ---------------------------------------------------------------------------
# Add tasks OUT OF ORDER on purpose so the sort demo is visibly meaningful.
# Insertion order:  17:00 → 18:30 → 07:00 → 12:00 → 08:00 → 07:30
# ---------------------------------------------------------------------------
Daisy.add_task(Task("t3", "Evening walk",          time(17, 0),  "daily"))  # 17:00
Dolly.add_task(Task("t6", "Feed dinner",            time(18, 30), "daily"))  # 18:30
Daisy.add_task(Task("t1", "Morning walk",           time(7, 0),   "daily"))  # 07:00
Dolly.add_task(Task("t5", "Administer medication",  time(12, 0),  "daily"))  # 12:00
Dolly.add_task(Task("t4", "Feed breakfast",         time(8, 0),   "daily"))  # 08:00
Daisy.add_task(Task("t2", "Feed breakfast",         time(7, 30),  "daily"))  # 07:30
# ---------------------------------------------------------------------------
# Build the scheduler, then mark one task complete so the
# completed / pending filter demos return distinct results.
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)
scheduler.mark_task_complete("t1")  # Daisy's Morning walk is already done


def _pet_name(task):
    """Helper: look up which pet owns a task."""
    return next((p.name for p in owner.get_pets() if task in p.tasks), "Unknown")


# ---------------------------------------------------------------------------
# Section 1 — Tasks in insertion order (no sorting applied)
# ---------------------------------------------------------------------------
print(f"\n📝  Tasks in Insertion Order for {owner.name}\n")
print(f"{'Time':<8}  {'Pet':<10}  {'Status':<8}  Task")
print("-" * 52)
for task in scheduler.get_all_tasks():
    status = "✓ done" if task.completed else "○ todo"
    print(f"{task.time.strftime('%H:%M'):<8}  {_pet_name(task):<10}  {status:<8}  {task.description}")
print()

# ---------------------------------------------------------------------------
# Section 2 — All tasks sorted by time using the HH:MM lambda key
# ---------------------------------------------------------------------------
print("🕐  All Tasks Sorted by Time  (key=lambda t: t.time.strftime('%H:%M'))\n")
print(f"{'Time':<8}  {'Pet':<10}  {'Status':<8}  Task")
print("-" * 52)
for task in scheduler.organize_by_time():
    status = "✓ done" if task.completed else "○ todo"
    print(f"{task.time.strftime('%H:%M'):<8}  {_pet_name(task):<10}  {status:<8}  {task.description}")
print()

# ---------------------------------------------------------------------------
# Section 3 — filter_tasks(pet_name="Daisy")
# ---------------------------------------------------------------------------
print("🐶  Filter — Daisy's Tasks Only\n")
print(f"{'Time':<8}  {'Status':<8}  Task")
print("-" * 36)
for task in scheduler.filter_tasks(pet_name="Daisy"):
    status = "✓ done" if task.completed else "○ todo"
    print(f"{task.time.strftime('%H:%M'):<8}  {status:<8}  {task.description}")
print()

# ---------------------------------------------------------------------------
# Section 4 — filter_tasks(completed=True)
# ---------------------------------------------------------------------------
print("✅  Filter — Completed Tasks Only\n")
completed_tasks = scheduler.filter_tasks(completed=True)
if completed_tasks:
    print(f"{'Time':<8}  {'Pet':<10}  Task")
    print("-" * 36)
    for task in completed_tasks:
        print(f"{task.time.strftime('%H:%M'):<8}  {_pet_name(task):<10}  {task.description}")
else:
    print("  (none)")
print()

# ---------------------------------------------------------------------------
# Section 5 — filter_tasks(completed=False)
# ---------------------------------------------------------------------------
print("📋  Filter — Pending Tasks Only\n")
print(f"{'Time':<8}  {'Pet':<10}  Task")
print("-" * 36)
for task in scheduler.filter_tasks(completed=False):
    print(f"{task.time.strftime('%H:%M'):<8}  {_pet_name(task):<10}  {task.description}")
print()