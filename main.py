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
# Add tasks (all daily so they appear in today's schedule)
# ---------------------------------------------------------------------------
# Daisy's tasks
Daisy.add_task(Task("t1", "Morning walk",        time(7, 0),  "daily"))
Daisy.add_task(Task("t2", "Feed breakfast",      time(7, 30), "daily"))
Daisy.add_task(Task("t3", "Evening walk",        time(17, 0), "daily"))
# Dolly's tasks
Dolly.add_task(Task("t4", "Feed breakfast",       time(8, 0),  "daily"))
Dolly.add_task(Task("t5", "Administer medication",time(12, 0), "daily"))
Dolly.add_task(Task("t6", "Feed dinner",          time(18, 30),"daily"))
# ---------------------------------------------------------------------------
# Build the schedule and print it
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan()
print(f"\n🐾  Today's PawPal+ Schedule for {owner.name}\n")
print(f"{'Time':<8}  {'Pet':<8}  {'Task'}")
print("-" * 40)
for task in plan:
    # find which pet owns this task
    pet_name = next(
        (p.name for p in owner.get_pets() if task in p.tasks),
        "Unknown",
    )
    status = "✓" if task.completed else "○"
    print(f"{task.time.strftime('%H:%M'):<8}  {pet_name:<8}  {status} {task.description}")
print()

# ---------------------------------------------------------------------------
# Demonstrate: sort all tasks by time using "HH:MM" string key
# ---------------------------------------------------------------------------
print("🕐  All Tasks Sorted by Time (HH:MM)\n")
print(f"{'Time':<8}  {'Pet':<8}  {'Task'}")
print("-" * 40)
for task in scheduler.organize_by_time():
    pet_name = next(
        (p.name for p in owner.get_pets() if task in p.tasks),
        "Unknown",
    )
    status = "✓" if task.completed else "○"
    print(f"{task.time.strftime('%H:%M'):<8}  {pet_name:<8}  {status} {task.description}")
print()

# ---------------------------------------------------------------------------
# Demonstrate: filter tasks by pet name
# ---------------------------------------------------------------------------
print("🐶  Daisy's Tasks\n")
for task in scheduler.filter_tasks(pet_name="Daisy"):
    status = "✓" if task.completed else "○"
    print(f"  {task.time.strftime('%H:%M')}  {status} {task.description}")
print()

# ---------------------------------------------------------------------------
# Demonstrate: filter tasks by completion status (pending only)
# ---------------------------------------------------------------------------
print("📋  All Pending Tasks\n")
for task in scheduler.filter_tasks(completed=False):
    pet_name = next(
        (p.name for p in owner.get_pets() if task in p.tasks),
        "Unknown",
    )
    print(f"  {task.time.strftime('%H:%M')}  [{pet_name}]  {task.description}")
print()