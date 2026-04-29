# app_rag_integration.py - Add to your app.py
"""
Integration examples for RAG assistant in Streamlit UI
"""
import streamlit as st
from datetime import time, date
from pawpal_system import Task, Pet, Owner, Scheduler
from rag_system import VectorDatabaseManager
from rag_assistant import RAGAssistant


# Initialize RAG system (add after existing initialization)
if "rag_db" not in st.session_state:
    st.session_state["rag_db"] = VectorDatabaseManager()
    st.session_state["rag_db"].initialize_knowledge_base()

if "rag_assistant" not in st.session_state:
    st.session_state["rag_assistant"] = RAGAssistant(st.session_state["rag_db"])
# ──────────────────────────────────────────────────────────────────────────────
# USE CASE 1: INTELLIGENT TASK SUGGESTIONS
# ──────────────────────────────────────────────────────────────────────────────

def show_task_suggestions():
    """Display intelligent task suggestions for a selected pet."""
    st.subheader("💡 AI Task Suggestions")
    
    owner: Owner = st.session_state["owner"]
    assistant: RAGAssistant = st.session_state["rag_assistant"]
    
    if not owner.get_pets():
        st.info("Add a pet first to get task suggestions.")
        return
    
    # Pet selection
    selected_pet_name = st.selectbox(
        "Get suggestions for which pet?",
        [p.name for p in owner.get_pets()],
        key="suggest_pet_select"
    )
    pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)
    
    if st.button("🤖 Generate Task Suggestions"):
        with st.spinner("Analyzing pet profile and knowledge base..."):
            # Get suggestions from RAG
            suggestions = assistant.get_task_suggestions(
                pet,
                existing_tasks=pet.get_tasks()
            )
        
        if suggestions:
            st.success(f"Found {len(suggestions)} suggested tasks!")
            
            # Display suggestions
            for i, suggestion in enumerate(suggestions):
                with st.expander(f"📋 {suggestion['description']}", expanded=(i==0)):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Time:** {suggestion['recommended_time'].strftime('%H:%M')}")
                    with col2:
                        st.write(f"**Frequency:** {suggestion['frequency'].capitalize()}")
                    with col3:
                        st.write(f"**Category:** {suggestion['source_category']}")
                    
                    st.info(f"**Why:** {suggestion['reasoning']}")
                    
                    # Add to pet button
                    if st.button(f"➕ Add this task", key=f"add_suggestion_{i}"):
                        task = assistant.create_task_from_suggestion(pet, suggestion)
                        pet.add_task(task)
                        st.success(f"✅ Added '{task.description}' to {pet.name}!")
                        st.rerun()
        else:
            st.warning("No new suggestions found. Your pet's schedule looks complete!")


# ──────────────────────────────────────────────────────────────────────────────
# USE CASE 2: HEALTH MONITORING & ALERTS
# ──────────────────────────────────────────────────────────────────────────────

def show_health_monitoring():
    """Health concern analysis and monitoring."""
    st.subheader("🏥 Pet Health Monitor")
    
    owner: Owner = st.session_state["owner"]
    assistant: RAGAssistant = st.session_state["rag_assistant"]
    
    if not owner.get_pets():
        st.info("Add a pet first to use health monitoring.")
        return
    
    # Pet selection
    pet_name = st.selectbox(
        "Monitor which pet?",
        [p.name for p in owner.get_pets()],
        key="health_pet_select"
    )
    pet = next(p for p in owner.get_pets() if p.name == pet_name)
    
    # Display current health status
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Health Status", pet.health_status)
    
    with col2:
        new_status = st.text_input(
            "Update health status if needed",
            value=pet.health_status,
            key="health_status_input"
        )
        if new_status != pet.health_status and st.button("Update Status"):
            status_alert = assistant.check_health_status_changes(pet, new_status)
            
            if status_alert["status_changed"]:
                if status_alert["alert_level"] == "high":
                    st.error(status_alert["message"])
                elif status_alert["alert_level"] == "info":
                    st.info(status_alert["message"])
                
                with st.expander("View Recommendations"):
                    for step in status_alert["next_steps"]:
                        st.write(f"• {step}")
            
            pet.health_status = new_status
    
    st.divider()
    
    # Health concern analysis
    st.markdown("#### Report a Health Concern")
    concern = st.text_area(
        "Describe any health concerns:",
        placeholder="e.g., 'Max seems lethargic today' or 'I noticed some scratching'",
        key="health_concern_input"
    )
    
    if st.button("🔍 Analyze Concern"):
        with st.spinner("Searching knowledge base and analyzing concern..."):
            analysis = assistant.analyze_health_concern(pet, concern)
        
        # Display analysis
        st.markdown(f"#### Analysis for {pet.name}")
        
        # Urgency alert
        urgency_emoji = analysis["urgency_color"]
        st.warning(f"{urgency_emoji} **Urgency Level: {analysis['urgency'].upper()}**")
        
        # Recommended actions
        st.markdown("**Recommended Actions:**")
        for action in analysis["recommended_actions"]:
            st.write(action)
        
        # Warning signs
        if analysis["warning_signs"]:
            st.markdown("**Watch for These Warning Signs:**")
            for sign in analysis["warning_signs"]:
                st.write(sign)
        
        # Breed-specific risks
        if analysis["breed_specific_risks"]:
            with st.expander("📍 Breed-Specific Health Risks"):
                for risk in analysis["breed_specific_risks"]:
                    st.write(f"• {risk}")


# ──────────────────────────────────────────────────────────────────────────────
# USE CASE 3: CONFLICT RESOLUTION WITH CONTEXT
# ──────────────────────────────────────────────────────────────────────────────

def show_conflict_resolution():
    """Intelligent conflict resolution and schedule optimization."""
    st.subheader("⚠️ Schedule Conflict Resolution")
    
    owner: Owner = st.session_state["owner"]
    scheduler = Scheduler(owner)
    assistant: RAGAssistant = st.session_state["rag_assistant"]
    
    if not owner.get_pets() or not any(owner.get_all_tasks()):
        st.info("Add pets and tasks to check for scheduling conflicts.")
        return
    
    # Analyze conflicts
    conflict_analysis = assistant.resolve_scheduling_conflicts(owner, scheduler)
    
    if not conflict_analysis["has_conflicts"]:
        st.success(conflict_analysis["message"])
        return
    
    # Display conflicts
    st.error(f"🚨 {conflict_analysis['message']}")
    
    for i, conflict in enumerate(conflict_analysis["conflicts"]):
        with st.expander(
            f"Conflict at {conflict['conflict_time']}: {len(conflict['conflicting_tasks'])} tasks",
            expanded=(i == 0)
        ):
            # Show conflicting tasks
            st.markdown("**Conflicting Tasks:**")
            for task in conflict["conflicting_tasks"]:
                st.write(
                    f"• **{task['pet_name']}**: {task['task_description']} "
                    f"({task['task_frequency']})"
                )
            
            st.info(f"**Why this matters:** {conflict['reasoning']}")
            
            # Show resolutions
            st.markdown("**Suggested Resolutions:**")
            for resolution in conflict["suggested_resolutions"]:
                with st.container(border=True):
                    st.markdown(f"**Option {resolution['option']}: {resolution['title']}** — Priority: {resolution['priority'].upper()}")
                    st.write(resolution['description'])
                    st.write(f"**Reasoning:** {resolution['reasoning']}")

                    if "suggested_times" in resolution:
                        st.markdown("**Suggested Times:**")
                        for key, value in resolution['suggested_times'].items():
                            st.write(f"• {key}: {value}")
    
    st.divider()
    
    # Proactive schedule optimization
    st.markdown("#### Optimize Your Daily Schedule")
    if st.button("🗓️ Generate Conflict-Free Schedule"):
        with st.spinner("Building optimal schedule..."):
            optimized = assistant.suggest_conflict_avoidance_schedule(owner)
        
        if "optimized_schedule" in optimized:
            st.success("✅ Optimized schedule created!")
            
            schedule = optimized["optimized_schedule"]
            for slot_name, slot_data in schedule.items():
                if slot_data["tasks"]:
                    st.markdown(f"### {slot_name.title()} ({slot_data['start']})")
                    for task in slot_data["tasks"]:
                        st.write(f"• **{task['pet']}**: {task['task']} @ {task['time']}")
            
            st.info("**Tips for Success:**")
            for tip in optimized.get("tips", []):
                st.write(f"• {tip}")
                
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

st.divider()

# ── RAG-Powered Features ─────────────────────────────────────────────────────
st.subheader("🤖 AI-Powered Features")
tab1, tab2, tab3 = st.tabs(["💡 Task Suggestions", "🏥 Health Monitor", "⚠️ Conflict Resolution"])

with tab1:
    show_task_suggestions()

with tab2:
    show_health_monitoring()

with tab3:
    show_conflict_resolution()
