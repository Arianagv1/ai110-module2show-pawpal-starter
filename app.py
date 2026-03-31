import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.divider()


# ── Owner bootstrap (once per session) ──────────────────────────────────────
if "owner" not in st.session_state:
    st.subheader("Create your profile")
    with st.form("owner_form"):
        owner_name = st.text_input("Your name")
        email      = st.text_input("Email")
        submitted  = st.form_submit_button("Create profile")
    if submitted:
        st.session_state["owner"] = Owner(
            owner_id="owner-1", name=owner_name, email=email
        )
        st.rerun()
    st.stop()

owner: Owner = st.session_state["owner"]
st.success(f"Welcome back, {owner.name}!")
st.divider()


# ── Add a Pet ────────────────────────────────────────────────────────────────
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name")
    species  = st.selectbox("Species", ["dog", "cat", "other"])
    breed    = st.text_input("Breed")
    dob      = st.date_input("Date of birth")
    weight   = st.number_input("Weight (kg)", min_value=0.1)
    health   = st.text_input("Health status", value="healthy")
    add_pet  = st.form_submit_button("Add pet")

if add_pet:
    pet = Pet(
        pet_id=f"pet-{len(owner.get_pets()) + 1}",
        name=pet_name, species=species, breed=breed,
        date_of_birth=dob, weight=weight, health_status=health,
    )
    owner.add_pet(pet)
    st.success(f"{pet_name} added!")

if owner.get_pets():
    st.table([p.get_pet_info() for p in owner.get_pets()])

st.divider()


# ── Add a Task to a Pet ──────────────────────────────────────────────────────
st.subheader("Add a Task")
if owner.get_pets():
    selected_pet_name = st.selectbox("Pet", [p.name for p in owner.get_pets()], key="task_pet_select")
    pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)

    with st.form("add_task_form"):
        desc      = st.text_input("Task description")
        task_time = st.time_input("Scheduled time")
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        add_task  = st.form_submit_button("Add task")

    if add_task:
        task = Task(
            task_id=f"{pet.pet_id}-task-{len(pet.get_tasks()) + 1}",
            description=desc, time=task_time, frequency=frequency,
        )
        pet.add_task(task)
        st.success(f"Task '{desc}' added to {pet.name}!")
else:
    st.info("Add a pet first before scheduling tasks.")

st.divider()


# ── Schedule & Conflict Detection ────────────────────────────────────────────
st.subheader("Today's Schedule")

if not owner.get_pets() or not any(owner.get_all_tasks()):
    st.info("Add pets and tasks to build a schedule.")
else:
    scheduler = Scheduler(owner)

    # ── Conflict warnings ────────────────────────────────────────────────────
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.error(
            f"**{len(conflicts)} scheduling conflict(s) detected** — "
            "two or more tasks overlap at the same time. "
            "Edit a task's scheduled time to resolve."
        )
        for warning in conflicts:
            # Strip the emoji already in the string and re-display in a
            # Streamlit warning box so the owner sees the full detail.
            st.warning(warning)
    else:
        st.success("No scheduling conflicts — your plan looks clear!")

    st.write("")  # breathing room

    # ── Summary metrics ──────────────────────────────────────────────────────
    all_tasks     = scheduler.get_all_tasks()
    pending       = scheduler.get_pending_tasks()
    completed     = scheduler.get_completed_tasks()
    todays_plan   = scheduler.generate_daily_plan()   # sorted, pending, due today

    col1, col2, col3 = st.columns(3)
    col1.metric("Total tasks",     len(all_tasks))
    col2.metric("Pending today",   len(todays_plan))
    col3.metric("Completed",       len(completed))

    st.write("")

    # ── Today's pending plan (sorted by time) ───────────────────────────────
    st.markdown("#### Pending tasks for today")
    if todays_plan:
        st.table([
            {
                "Time":        t.time.strftime("%H:%M"),
                "Pet":         next(
                                   p.name for p in owner.get_pets()
                                   if any(x.task_id == t.task_id for x in p.get_tasks())
                               ),
                "Task":        t.description,
                "Frequency":   t.frequency.capitalize(),
                "Status":      "✅ Done" if t.completed else "⏳ Pending",
            }
            for t in todays_plan
        ])
    else:
        st.info("All of today's tasks are complete — great work!")

    st.divider()

    # ── Filter all tasks ─────────────────────────────────────────────────────
    st.markdown("#### Filter all tasks")
    col_a, col_b = st.columns(2)
    with col_a:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + [p.name for p in owner.get_pets()],
        )
    with col_b:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed"],
        )

    completed_arg = {"All": None, "Pending": False, "Completed": True}[status_filter]
    pet_name_arg  = None if pet_filter == "All pets" else pet_filter

    filtered = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_name_arg)

    if filtered:
        # Sort the filtered results by time for a tidy display
        filtered_sorted = sorted(filtered, key=lambda t: t.time)
        st.table([
            {
                "Time":      t.time.strftime("%H:%M"),
                "Task":      t.description,
                "Frequency": t.frequency.capitalize(),
                "Due date":  t.due_date.strftime("%Y-%m-%d") if t.due_date else "—",
                "Status":    "✅ Done" if t.completed else "⏳ Pending",
            }
            for t in filtered_sorted
        ])
    else:
        st.info("No tasks match the selected filters.")

    st.divider()

    # ── Mark a task complete ─────────────────────────────────────────────────
    st.markdown("#### Mark a task complete")
    pending_tasks = scheduler.get_pending_tasks()
    if pending_tasks:
        pending_sorted = sorted(pending_tasks, key=lambda t: t.time)
        task_options   = {
            f"{t.time.strftime('%H:%M')} — {t.description} ({t.task_id})": t.task_id
            for t in pending_sorted
        }
        chosen_label = st.selectbox("Select task to complete", list(task_options))
        if st.button("Mark complete"):
            scheduler.mark_task_complete(task_options[chosen_label])
            st.success("Task marked complete! The next occurrence has been scheduled.")
            st.rerun()
    else:
        st.success("All tasks are already marked complete!")
