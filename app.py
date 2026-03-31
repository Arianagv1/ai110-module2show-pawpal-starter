import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler   


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ── Owner bootstrap (once per session) ──────────────────────────────────────
if "owner" not in st.session_state:
    st.subheader("Create your profile")
    with st.form("owner_form"):
        owner_name = st.text_input("Your name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Create profile")
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
    pet_name   = st.text_input("Pet name")
    species    = st.selectbox("Species", ["dog", "cat", "other"])
    breed      = st.text_input("Breed")
    dob        = st.date_input("Date of birth")
    weight     = st.number_input("Weight (kg)", min_value=0.1)
    health     = st.text_input("Health status", value="healthy")
    add_pet    = st.form_submit_button("Add pet")

if add_pet:
    pet = Pet(
        pet_id=f"pet-{len(owner.get_pets())+1}",
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
    selected = st.selectbox("Pet", [p.name for p in owner.get_pets()])
    pet = next(p for p in owner.get_pets() if p.name == selected)

    with st.form("add_task_form"):
        desc      = st.text_input("Task description")
        task_time = st.time_input("Scheduled time")
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        add_task  = st.form_submit_button("Add task")

    if add_task:
        task = Task(
            task_id=f"task-{len(pet.get_tasks())+1}",
            description=desc, time=task_time, frequency=frequency,
        )
        pet.add_task(task)
        st.success(f"Task '{desc}' added to {pet.name}!")
else:
    st.info("Add a pet first before scheduling tasks.")

st.divider()

# ── Build Schedule ───────────────────────────────────────────────────────────
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()
    if plan:
        st.write("Today's plan:")
        st.table([t.get_task_info() for t in plan])
    else:
        st.info("No tasks due today. Add daily tasks to see a plan.")
