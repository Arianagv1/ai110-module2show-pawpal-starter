# PawPlus+ — Pet Care Scheduler

A Streamlit-based application that helps pet owners manage and schedule daily care tasks for their pets. PawPlus+ generates an organized daily plan, detects scheduling conflicts, and automatically reschedules recurring tasks so nothing falls through the cracks.

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_demoSS.png" target="_blank"><img src='/course_images/ai110/pawpal_demoSS.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## ✨ Features

### Task Management
- **Add & remove tasks** for any pet, with a description, scheduled time, and frequency (daily, weekly, or one-off)
- **Mark tasks complete or incomplete** with a single click
- **View all tasks or filter** by pet name and completion status

### Smart Scheduling Algorithms
- **Sort by time** — tasks are always displayed in ascending chronological order so the owner sees what comes next first
- **Daily plan generation** — produces today's pending tasks sorted by scheduled time, giving the owner a clean to-do list each morning
- **Recurring task auto-scheduling** — when a daily or weekly task is marked complete, a new task is automatically created for the next occurrence (tomorrow for daily, +7 days for weekly) so the schedule never goes stale
- **Conflict detection** — scans all pets' tasks and flags any two tasks scheduled at the exact same time, returning a human-readable warning per conflicting time slot

### Multi-Pet Support
- Register multiple pets under a single owner profile
- Filter and view tasks scoped to one pet or across all pets at once
- Each pet independently tracks its own task list

### Owner & Pet Profiles
- Store owner name and email
- Store pet details: name, species, breed, date of birth, weight, and health status

---

## 🗂️ Project Structure

```
ai110-module2show-pawpal-starter/
├── app.py               # Streamlit UI
├── pawpal_system.py     # Core logic: Task, Pet, Owner, Scheduler
├── test_pawpal.py       # Unit tests for scheduling behaviors
├── reflection.md        # Design reflection and UML diagrams
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🏗️ System Design

The app is built around four core classes:

| Class | Responsibility |
|---|---|
| `Task` | Represents a single care activity with time, frequency, and completion state |
| `Pet` | Stores pet profile and owns a list of Tasks |
| `Owner` | Manages a roster of Pets and aggregates all their Tasks |
| `Scheduler` | Contains all scheduling logic — filtering, sorting, conflict detection, and daily plan generation |

See [reflection.md](reflection.md) for the full UML class diagram and design decisions.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Running the Tests

```bash
python -m pytest test_pawpal.py -v
```

---

## 📋 How to Use

1. **Enter your name and email** in the Owner Profile section.
2. **Add a pet** by providing its name, species, breed, date of birth, weight, and health status.
3. **Add tasks** to any pet — give each task a description, scheduled time, and frequency.
4. **View Today's Plan** to see all pending tasks for the day, sorted by time.
5. **Mark tasks complete** as you finish them. Recurring tasks will automatically reappear for their next due date.
6. **Check for conflicts** to see if any tasks overlap in time across your pets.
