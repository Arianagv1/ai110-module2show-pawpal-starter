"""
RAG-powered assistant for intelligent pet care workflows.
Implements three key use cases:
1. Intelligent task suggestions
2. Health monitoring and alerts
3. Conflict resolution with context
"""

import re
from datetime import date, time
from typing import Optional
from pawpal_system import Task, Pet, Owner, Scheduler
from rag_system import VectorDatabaseManager


class RAGAssistant:
    """Intelligent pet care assistant powered by RAG."""

    def __init__(self, rag_db: VectorDatabaseManager):
        self.rag_db = rag_db

    # ───────────────────────────────────────────────────────────────────────
    # USE CASE 1: INTELLIGENT TASK SUGGESTIONS
    # ───────────────────────────────────────────────────────────────────────

    def get_task_suggestions(
        self,
        pet: Pet,
        existing_tasks: list[Task] = None
    ) -> list[dict]:
        """
        Generate smart task suggestions based on pet profile using RAG.

        Args:
            pet: Pet object with profile info (species, breed, age, etc.)
            existing_tasks: List of tasks already assigned to this pet

        Returns:
            List of suggested tasks with description, recommended time, and frequency
        """
        if existing_tasks is None:
            existing_tasks = []

        today = date.today()
        age_days = (today - pet.date_of_birth).days
        age_years = age_days // 365

        query = f"""
        I have a {age_years}-year-old {pet.breed} {pet.species}
        weighing {pet.weight}kg with {pet.health_status} health status.
        What daily care tasks should I schedule?
        """

        search_results = self.rag_db.search(query, species=pet.species, top_k=5)

        existing_descriptions = [t.description.lower() for t in existing_tasks]

        suggestions = []

        for result in search_results:
            doc_content = result["content"]
            category = result["metadata"].get("category", "general")

            if category == "feeding":
                suggestions.append(self._parse_feeding_suggestion(
                    pet, doc_content, existing_descriptions
                ))
            elif category == "exercise":
                suggestions.append(self._parse_exercise_suggestion(
                    pet, doc_content, existing_descriptions
                ))
            elif category == "breed_specific":
                suggestions.extend(self._parse_breed_suggestion(
                    pet, doc_content, existing_descriptions
                ))
            elif category == "health":
                suggestions.append(self._parse_health_suggestion(
                    pet, doc_content, existing_descriptions
                ))

        return [s for s in suggestions if s is not None]

    def _parse_feeding_suggestion(
        self,
        pet: Pet,
        content: str,
        existing_descriptions: list[str]
    ) -> Optional[dict]:
        """Parse feeding guidelines from knowledge base."""
        age_months = (date.today() - pet.date_of_birth).days // 30

        if "puppy" in content.lower() and age_months < 6:
            if "feeding" not in " ".join(existing_descriptions):
                return {
                    "description": "Puppy feeding - 3-4 meals daily",
                    "recommended_time": time(8, 0),
                    "frequency": "daily",
                    "reasoning": "Puppies under 6 months need frequent meals",
                    "source_category": "feeding"
                }

        if pet.species.lower() == "dog" and "feeding" in content.lower():
            if "dog feed" not in " ".join(existing_descriptions):
                return {
                    "description": "Dog feeding - twice daily",
                    "recommended_time": time(18, 0),
                    "frequency": "daily",
                    "reasoning": "Adult dogs typically fed at consistent times",
                    "source_category": "feeding"
                }

        return None

    def _parse_exercise_suggestion(
        self,
        pet: Pet,
        content: str,
        existing_descriptions: list[str]
    ) -> Optional[dict]:
        """Parse exercise recommendations from knowledge base."""
        if pet.species.lower() == "dog":
            if "exercise" not in " ".join(existing_descriptions):
                if pet.weight > 50:
                    return {
                        "description": "Large breed exercise - 60+ minutes activity",
                        "recommended_time": time(7, 0),
                        "frequency": "daily",
                        "reasoning": f"Large breeds ({pet.weight}kg) need substantial exercise",
                        "source_category": "exercise"
                    }
                else:
                    return {
                        "description": "Dog exercise - 30-45 minutes walk",
                        "recommended_time": time(17, 30),
                        "frequency": "daily",
                        "reasoning": "Daily exercise prevents obesity and behavioral issues",
                        "source_category": "exercise"
                    }

        return None

    def _parse_breed_suggestion(
        self,
        pet: Pet,
        content: str,
        existing_descriptions: list[str]
    ) -> list[dict]:
        """Parse breed-specific care from knowledge base."""
        suggestions = []
        breed_lower = pet.breed.lower()
        content_lower = content.lower()

        if "golden" in breed_lower and "retriever" in breed_lower:
            if "grooming" not in " ".join(existing_descriptions):
                suggestions.append({
                    "description": "Golden Retriever grooming - brush coat",
                    "recommended_time": time(10, 0),
                    "frequency": "weekly",
                    "reasoning": "Golden Retrievers need regular grooming 3-4x weekly",
                    "source_category": "breed_specific"
                })
            if "ear" in content_lower:
                suggestions.append({
                    "description": "Golden Retriever ear check",
                    "recommended_time": time(10, 0),
                    "frequency": "weekly",
                    "reasoning": "Prone to ear infections due to floppy ears",
                    "source_category": "breed_specific"
                })

        return suggestions

    def _parse_health_suggestion(
        self,
        pet: Pet,
        content: str,
        existing_descriptions: list[str]
    ) -> Optional[dict]:
        """Parse health/wellness recommendations from knowledge base."""
        if "vaccination" in content.lower():
            if "vet" not in " ".join(existing_descriptions):
                return {
                    "description": "Veterinary checkup and vaccination",
                    "recommended_time": time(9, 0),
                    "frequency": "once",
                    "reasoning": "Annual/scheduled vet visits ensure pet health",
                    "source_category": "health"
                }

        return None

    def create_task_from_suggestion(self, pet: Pet, suggestion: dict) -> Task:
        """Convert a suggestion dict into an actual Task object."""
        task_id = f"{pet.pet_id}-suggested-{len(pet.get_tasks()) + 1}"
        return Task(
            task_id=task_id,
            description=suggestion["description"],
            time=suggestion["recommended_time"],
            frequency=suggestion["frequency"],
        )

    # ───────────────────────────────────────────────────────────────────────
    # USE CASE 2: HEALTH MONITORING & ALERTS
    # ───────────────────────────────────────────────────────────────────────

    def analyze_health_concern(self, pet: Pet, concern: str) -> dict:
        """
        Analyze a health concern using RAG to provide guidance.

        Args:
            pet: Pet object with profile info
            concern: Description of health concern (e.g., "Max seems lethargic")

        Returns:
            Dict with assessment, recommended actions, and urgency level
        """
        query = f"""
        {pet.name} is a {pet.species} with the following concern: {concern}
        Pet details: {pet.breed} breed, {pet.weight}kg,
        current health status: {pet.health_status}

        What should I do about this?
        """

        health_results = self.rag_db.search(query, species=pet.species, top_k=5)
        return self._analyze_health_results(pet, concern, health_results)

    def _analyze_health_results(
        self,
        pet: Pet,
        concern: str,
        search_results: list[dict]
    ) -> dict:
        """Synthesize health search results into actionable guidance."""
        concern_lower = concern.lower()
        urgency = "monitor"
        recommended_actions = []
        warning_signs = []

        if any(word in concern_lower for word in ["lethargic", "lethargy", "tired", "sluggish"]):
            urgency = "moderate"
            recommended_actions = [
                "✓ Check water intake and bowl access",
                "✓ Monitor body temperature",
                "✓ Observe eating patterns",
                "✓ Contact vet if persists >24 hours"
            ]
            warning_signs = [
                "🚨 Loss of appetite",
                "🚨 Increased panting",
                "🚨 Unusual behavior changes"
            ]

        elif any(word in concern_lower for word in ["vomiting", "vomit", "nausea"]):
            urgency = "high"
            recommended_actions = [
                "✓ Withhold food for 2-4 hours",
                "✓ Offer small amounts of water",
                "✓ Note frequency and appearance",
                "✓ Contact vet immediately if frequent"
            ]
            warning_signs = [
                "🚨 Vomiting > 3 times/day",
                "🚨 Blood in vomit",
                "🚨 Lethargy accompanying vomiting"
            ]

        elif any(word in concern_lower for word in ["ear", "infection", "itch", "scratching"]):
            urgency = "low"
            recommended_actions = [
                "✓ Inspect ears for redness/discharge",
                "✓ Gently clean outer ear",
                "✓ Avoid water getting in ears",
                "✓ Schedule vet if persists >1 week"
            ]
            warning_signs = [
                "🚨 Foul odor from ears",
                "🚨 Thick discharge",
                "🚨 Head shaking/pain when touched"
            ]

        urgency_color = {
            "low": "🟢",
            "moderate": "🟡",
            "high": "🔴",
            "monitor": "⚪",
        }

        breed_concerns = self._extract_breed_concerns(pet, search_results)

        return {
            "pet_name": pet.name,
            "concern": concern,
            "urgency": urgency,
            "urgency_color": urgency_color[urgency],
            "recommended_actions": recommended_actions,
            "warning_signs": warning_signs,
            "breed_specific_risks": breed_concerns,
            "knowledge_base_references": [r["id"] for r in search_results[:3]]
        }

    def _extract_breed_concerns(
        self,
        pet: Pet,
        search_results: list[dict]
    ) -> list[str]:
        """Extract breed-specific health risks from search results."""
        concerns = []

        for result in search_results:
            if result["metadata"].get("category") in ("breed_specific", "health"):
                for line in result["content"].split("\n"):
                    line = line.strip().lstrip("- ")
                    if any(kw in line.lower() for kw in ["health concern", "dysplasia", "infection", "diabetes", "disease"]):
                        if line:
                            concerns.append(line)

        return concerns

    def check_health_status_changes(self, pet: Pet, new_status: str) -> dict:
        """
        Monitor for changes in pet's health status and alert accordingly.

        Args:
            pet: Pet object
            new_status: New health status description

        Returns:
            Alert dict with changes and recommendations
        """
        old_status = pet.health_status.lower()
        new_status_lower = new_status.lower()
        changes_detected = old_status != new_status_lower

        alert = {
            "status_changed": changes_detected,
            "previous_status": pet.health_status,
            "new_status": new_status,
            "timestamp": str(date.today()),
            "alert_level": "none"
        }

        if changes_detected:
            if "sick" in new_status_lower or "ill" in new_status_lower:
                alert["alert_level"] = "high"
                alert["message"] = "⚠️ Health status change detected: Pet may be unwell"
                alert["next_steps"] = [
                    "Monitor closely for 24 hours",
                    "Contact vet if symptoms persist",
                    "Increase observation frequency"
                ]
            elif "improving" in new_status_lower or "better" in new_status_lower:
                alert["alert_level"] = "info"
                alert["message"] = "✅ Positive health status change detected"
                alert["next_steps"] = [
                    "Continue current care routine",
                    "Schedule follow-up vet visit if recommended"
                ]
            else:
                alert["alert_level"] = "info"
                alert["message"] = "ℹ️ Health status updated"

        return alert

    # ───────────────────────────────────────────────────────────────────────
    # USE CASE 3: CONFLICT RESOLUTION WITH CONTEXT
    # ───────────────────────────────────────────────────────────────────────

    def resolve_scheduling_conflicts(self, owner: Owner, scheduler: Scheduler) -> dict:
        """
        Intelligently resolve scheduling conflicts with contextual suggestions.

        Args:
            owner: Owner object with all pets
            scheduler: Scheduler with conflict detection capability

        Returns:
            Dict with conflicts and smart resolution suggestions
        """
        basic_conflicts = scheduler.detect_conflicts()

        if not basic_conflicts:
            return {
                "has_conflicts": False,
                "message": "✅ No scheduling conflicts detected!",
                "conflicts": []
            }

        conflict_analysis = [
            self._analyze_single_conflict(owner, msg) for msg in basic_conflicts
        ]

        return {
            "has_conflicts": True,
            "conflict_count": len(conflict_analysis),
            "conflicts": conflict_analysis,
            "message": f"⚠️ Found {len(conflict_analysis)} scheduling conflict(s)"
        }

    def _analyze_single_conflict(self, owner: Owner, conflict_msg: str) -> dict:
        """Analyze a single conflict and suggest resolutions."""
        time_match = re.search(r"(\d{2}):(\d{2})", conflict_msg)
        conflict_time = None
        if time_match:
            conflict_time = time(int(time_match.group(1)), int(time_match.group(2)))

        conflicting_tasks = []
        for pet in owner.get_pets():
            for task in pet.get_tasks():
                if task.time == conflict_time:
                    conflicting_tasks.append({
                        "pet_name": pet.name,
                        "task_description": task.description,
                        "current_time": task.time.strftime("%H:%M"),
                        "task_frequency": task.frequency
                    })

        context_query = f"""
        I have multiple pets with conflicting tasks at the same time.
        Tasks: {[t['task_description'] for t in conflicting_tasks]}
        Pets: {[t['pet_name'] for t in conflicting_tasks]}

        What's the best way to reschedule these to avoid conflicts
        while maintaining optimal pet care?
        """

        context_results = self.rag_db.search(context_query, top_k=3)

        resolutions = self._generate_resolutions(conflicting_tasks, conflict_time, context_results)

        return {
            "conflict_time": conflict_time.strftime("%H:%M") if conflict_time else "unknown",
            "conflicting_tasks": conflicting_tasks,
            "original_message": conflict_msg,
            "suggested_resolutions": resolutions,
            "reasoning": self._get_resolution_reasoning(conflicting_tasks)
        }

    def _generate_resolutions(
        self,
        tasks: list[dict],
        conflict_time: time,
        context_results: list[dict]
    ) -> list[dict]:
        """Generate smart resolution suggestions."""
        resolutions = []
        task_types = [t["task_description"].lower() for t in tasks]

        has_feeding = any("feed" in t for t in task_types)
        has_exercise = any("walk" in t or "exercise" in t for t in task_types)

        if has_feeding and has_exercise and conflict_time:
            total_minutes = conflict_time.hour * 60 + conflict_time.minute + 30
            shifted_time = time(total_minutes // 60 % 24, total_minutes % 60)
            resolutions.append({
                "option": 1,
                "title": "Separate Feeding & Exercise",
                "description": "Move exercise 30 minutes after feeding (prevents digestive issues)",
                "suggested_times": {
                    "feeding": conflict_time.strftime("%H:%M"),
                    "exercise": shifted_time.strftime("%H:%M"),
                },
                "reasoning": "Dogs should rest 15-30 min after eating before exercise",
                "priority": "high"
            })

        resolutions.append({
            "option": 2,
            "title": "Prioritize by Task Type",
            "description": "Move quieter/maintenance tasks earlier",
            "suggested_times": {
                "morning_slot": "07:00",
                "afternoon_slot": "14:00",
                "evening_slot": "18:00"
            },
            "reasoning": "Spread tasks across the day for better pet management",
            "priority": "medium"
        })

        resolutions.append({
            "option": 3,
            "title": "Separate by Pet Location",
            "description": "Do tasks in different spaces simultaneously",
            "suggested_approach": "Schedule both tasks but in different locations/rooms",
            "reasoning": "If pets are in different spaces, simultaneous tasks won't cause conflicts",
            "priority": "low"
        })

        return resolutions

    def _get_resolution_reasoning(self, tasks: list[dict]) -> str:
        """Provide context-specific reasoning for conflict resolution."""
        task_types = [t["task_description"] for t in tasks]
        pets = [t["pet_name"] for t in tasks]

        reasoning = f"Conflicting tasks at same time: {', '.join(task_types)} for pets: {', '.join(pets)}. "

        if len(tasks) > 1:
            if any("feed" in t.lower() for t in task_types):
                reasoning += "Feeding is involved—ensure pets don't distract each other. "
            if any("walk" in t.lower() or "exercise" in t.lower() for t in task_types):
                reasoning += "Exercise requires attention—best done serially. "

        return reasoning

    def suggest_conflict_avoidance_schedule(self, owner: Owner) -> dict:
        """
        Proactively suggest an optimized daily schedule to avoid conflicts.

        Args:
            owner: Owner object with all pets

        Returns:
            Optimized schedule with time slots for each pet
        """
        all_tasks = owner.get_all_tasks()
        if not all_tasks:
            return {"message": "No tasks to schedule yet"}

        schedule = {
            "morning":   {"start": "07:00", "tasks": [], "duration_minutes": 60},
            "midday":    {"start": "12:00", "tasks": [], "duration_minutes": 60},
            "afternoon": {"start": "15:00", "tasks": [], "duration_minutes": 60},
            "evening":   {"start": "18:00", "tasks": [], "duration_minutes": 90},
        }

        for pet in owner.get_pets():
            for task in pet.get_tasks():
                desc = task.description.lower()
                if "feed" in desc:
                    if len(schedule["morning"]["tasks"]) < 2:
                        schedule["morning"]["tasks"].append({
                            "pet": pet.name, "task": task.description, "time": "08:00"
                        })
                elif "exercise" in desc or "walk" in desc:
                    if len(schedule["evening"]["tasks"]) < 2:
                        schedule["evening"]["tasks"].append({
                            "pet": pet.name, "task": task.description, "time": "18:30"
                        })
                else:
                    if len(schedule["afternoon"]["tasks"]) < 2:
                        schedule["afternoon"]["tasks"].append({
                            "pet": pet.name, "task": task.description, "time": "15:00"
                        })

        return {
            "optimized_schedule": schedule,
            "note": "This schedule separates conflicting tasks and respects pet care best practices",
            "tips": [
                "Exercise dogs at least 30 minutes after feeding",
                "Group similar tasks together for efficiency",
                "Leave buffer time between intense activities",
                "Adjust times based on your personal schedule"
            ]
        }
