from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task

# ---------------------------------------------------------------------------
# Create owner
# ---------------------------------------------------------------------------
owner = Owner(
    owner_id="owner-1",
    name="Jordan",
    email="jordan@example.com",
)

# ---------------------------------------------------------------------------
# Create pets and register them with the owner
# ---------------------------------------------------------------------------
mochi = Pet(
    pet_id="pet-1",
    name="Mochi",
    species="dog",
    breed="Shiba Inu",
    date_of_birth=date(2020, 3, 15),
    weight=10.5,
    health_status="healthy",
)

luna = Pet(
    pet_id="pet-2",
    name="Luna",
    species="cat",
    breed="Domestic Shorthair",
    date_of_birth=date(2019, 7, 4),
    weight=4.2,
    health_status="healthy",
)

owner.add_pet(mochi)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Add tasks (all daily so they appear in today's schedule)
# ---------------------------------------------------------------------------
# Mochi's tasks
mochi.add_task(Task("t1", "Morning walk",        time(7, 0),  "daily"))
mochi.add_task(Task("t2", "Feed breakfast",      time(7, 30), "daily"))
mochi.add_task(Task("t3", "Evening walk",        time(17, 0), "daily"))

# Luna's tasks
luna.add_task(Task("t4", "Feed breakfast",       time(8, 0),  "daily"))
luna.add_task(Task("t5", "Administer medication",time(12, 0), "daily"))
luna.add_task(Task("t6", "Feed dinner",          time(18, 30),"daily"))

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
