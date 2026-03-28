from __future__ import annotations
from dataclasses import dataclass
from datetime import date, time


# ---------------------------------------------------------------------------
# Data classes — simple value objects used across the system
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    breed: str
    date_of_birth: date
    weight: float
    health_status: str

    def get_pet_info(self) -> "Pet":
        pass

    def update_pet_info(self) -> None:
        pass

    def delete_pet(self) -> None:
        pass


@dataclass
class User:
    user_id: str
    name: str
    email: str

    def create_account(self) -> None:
        pass

    def update_profile(self) -> None:
        pass

    def delete_account(self) -> None:
        pass

    def get_notifications(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Core activity classes
# ---------------------------------------------------------------------------

class Medications:
    def __init__(
        self,
        medication_id: str,
        med_name: str,
        dosage: str,
        frequency: str,
        start_date: date,
        end_date: date,
        refill_date: date,
    ):
        self.medication_id = medication_id
        self.med_name = med_name
        self.dosage = dosage
        self.frequency = frequency
        self.start_date = start_date
        self.end_date = end_date
        self.refill_date = refill_date

    def which_med(self) -> str:
        pass

    def when_med(self) -> date:
        pass

    def which_pet_med(self) -> Pet:
        pass

    def did_get_med(self) -> bool:
        pass

    def log_medication_given(self) -> None:
        pass

    def set_reminder(self) -> None:
        pass


class Walks:
    def __init__(
        self,
        walk_id: str,
        date: date,
        time: time,
        duration: int,
        distance: float,
        location: str,
    ):
        self.walk_id = walk_id
        self.date = date
        self.time = time
        self.duration = duration
        self.distance = distance
        self.location = location

    def when_walk(self) -> date:
        pass

    def where_walk(self) -> str:
        pass

    def did_walk(self) -> bool:
        pass

    def which_pet(self) -> Pet:
        pass

    def walk_duration(self) -> int:
        pass

    def walk_distance(self) -> float:
        pass

    def log_walk(self) -> None:
        pass

    def track_route(self) -> None:
        pass


class Feedings:
    def __init__(
        self,
        feeding_id: str,
        feed_type: str,
        brand: str,
        portion_size: float,
        time: time,
        date: date,
    ):
        self.feeding_id = feeding_id
        self.feed_type = feed_type
        self.brand = brand
        self.portion_size = portion_size
        self.time = time
        self.date = date

    def did_feed(self) -> bool:
        pass

    def which_feed(self) -> str:
        pass

    def which_pet(self) -> Pet:
        pass

    def did_pet_eat(self) -> bool:
        pass

    def feeding_time(self) -> time:
        pass

    def log_feeding(self) -> None:
        pass

    def track_nutrition(self) -> None:
        pass


class Appointments:
    def __init__(
        self,
        appointment_id: str,
        date: date,
        time: time,
        location: str,
        vet_name: str,
        reason: str,
        notes: str,
        next_appt_date: date,
    ):
        self.appointment_id = appointment_id
        self.date = date
        self.time = time
        self.location = location
        self.vet_name = vet_name
        self.reason = reason
        self.notes = notes
        self.next_appt_date = next_appt_date

    def did_go(self) -> bool:
        pass

    def where_appt(self) -> str:
        pass

    def when_appt(self) -> date:
        pass

    def reason_appt(self) -> str:
        pass

    def which_pet(self) -> Pet:
        pass

    def get_vet_name(self) -> str:
        pass

    def appt_notes(self) -> str:
        pass

    def next_appt(self) -> date:
        pass

    def schedule_appointment(self) -> None:
        pass

    def set_reminder(self) -> None:
        pass

    def update_notes(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Supporting classes
# ---------------------------------------------------------------------------

class HealthRecord:
    def __init__(
        self,
        record_id: str,
        date: date,
        record_type: str,
        details: str,
        created_date: date,
    ):
        self.record_id = record_id
        self.date = date
        self.record_type = record_type
        self.details = details
        self.created_date = created_date

    def get_health_history(self) -> list["HealthRecord"]:
        pass

    def add_health_record(self) -> None:
        pass

    def generate_report(self) -> None:
        pass


class Reminder:
    def __init__(
        self,
        reminder_id: str,
        type: str,
        time: time,
        frequency: str,
        is_active: bool,
    ):
        self.reminder_id = reminder_id
        self.type = type
        self.time = time
        self.frequency = frequency
        self.is_active = is_active

    def create_reminder(self) -> None:
        pass

    def delete_reminder(self) -> None:
        pass

    def send_notification(self) -> None:
        pass


class Dashboard:
    def get_upcoming_reminders(self) -> list[Reminder]:
        pass

    def get_todays_tasks(self) -> None:
        pass

    def get_health_summary(self) -> None:
        pass

    def get_activity_summary(self) -> None:
        pass

    def display_weekly_report(self) -> None:
        pass