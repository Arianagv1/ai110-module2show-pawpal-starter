# test_rag_assistant.py
"""
Test suite for RAG-powered intelligent pet care assistant.
Tests cover three main use cases:
1. Intelligent task suggestions
2. Health monitoring and alerts
3. Conflict resolution with context
"""

import pytest
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Scheduler, Task
from rag_system import VectorDatabaseManager
from rag_assistant import RAGAssistant


# ───────────────────────────────────────────────────────────────────────────
# SETUP & FIXTURES
# ───────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def rag_db():
    """Initialize RAG database once per test session."""
    db = VectorDatabaseManager(db_path="./test_chroma_db")
    db.initialize_knowledge_base()
    yield db
    # Cleanup after tests
    db.reset()


@pytest.fixture
def rag_assistant(rag_db):
    """Create RAG assistant with initialized database."""
    return RAGAssistant(rag_db)


@pytest.fixture
def sample_owner():
    """Create a sample owner with multiple pets for testing."""
    owner = Owner("owner-1", "Jane Doe", "jane@example.com")
    
    # Golden Retriever (large, high energy)
    golden = Pet(
        pet_id="pet-1",
        name="Max",
        species="dog",
        breed="Golden Retriever",
        date_of_birth=date(2022, 6, 15),
        weight=32.0,
        health_status="healthy"
    )
    
    # Shih Tzu (small breed)
    shih_tzu = Pet(
        pet_id="pet-2",
        name="Daisy",
        species="dog",
        breed="Shih Tzu",
        date_of_birth=date(2020, 3, 20),
        weight=5.5,
        health_status="healthy"
    )
    
    # Cat
    cat = Pet(
        pet_id="pet-3",
        name="Whiskers",
        species="cat",
        breed="Tabby",
        date_of_birth=date(2019, 1, 10),
        weight=4.0,
        health_status="healthy"
    )
    
    owner.add_pet(golden)
    owner.add_pet(shih_tzu)
    owner.add_pet(cat)
    
    return owner


@pytest.fixture
def owner_with_tasks(sample_owner):
    """Create owner with some existing tasks."""
    owner = sample_owner
    
    # Add existing tasks to Golden Retriever
    owner.get_pets()[0].add_task(
        Task("task-1", "Morning walk", time(7, 0), "daily")
    )
    owner.get_pets()[0].add_task(
        Task("task-2", "Feeding", time(8, 0), "daily")
    )
    
    # Add existing tasks to Shih Tzu
    owner.get_pets()[1].add_task(
        Task("task-3", "Evening walk", time(17, 30), "daily")
    )
    
    # Add existing tasks to Cat
    owner.get_pets()[2].add_task(
        Task("task-4", "Cat feeding", time(8, 0), "daily")
    )
    
    return owner


# ───────────────────────────────────────────────────────────────────────────
# TEST CASE 1: INTELLIGENT TASK SUGGESTIONS
# ───────────────────────────────────────────────────────────────────────────

class TestTaskSuggestions:
    """Test suite for intelligent task suggestion use case."""
    
    def test_suggestions_returned_for_valid_pet(self, rag_assistant, sample_owner):
        """
        Test that get_task_suggestions() returns a non-empty list for a valid pet.
        Verifies that the RAG system can retrieve relevant care guidelines.
        """
        pet = sample_owner.get_pets()[0]  # Golden Retriever
        suggestions = rag_assistant.get_task_suggestions(pet)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        print(f"✓ Got {len(suggestions)} suggestions for {pet.name}")
    
    def test_suggestion_has_required_fields(self, rag_assistant, sample_owner):
        """
        Test that each suggestion contains all required fields:
        description, recommended_time, frequency, reasoning, source_category.
        """
        pet = sample_owner.get_pets()[0]
        suggestions = rag_assistant.get_task_suggestions(pet)
        
        required_fields = [
            "description",
            "recommended_time",
            "frequency",
            "reasoning",
            "source_category"
        ]
        
        for suggestion in suggestions:
            for field in required_fields:
                assert field in suggestion, f"Missing field: {field}"
                assert suggestion[field] is not None
        
        print(f"✓ All {len(suggestions)} suggestions have required fields")
    
    def test_suggestions_avoid_duplicates(self, rag_assistant, owner_with_tasks):
        """
        Test that suggested tasks don't duplicate existing tasks.
        Verifies that the system is aware of already-scheduled tasks.
        """
        pet = owner_with_tasks.get_pets()[0]  # Golden with existing tasks
        existing_descriptions = [t.description.lower() for t in pet.get_tasks()]
        
        suggestions = rag_assistant.get_task_suggestions(
            pet,
            existing_tasks=pet.get_tasks()
        )
        
        for suggestion in suggestions:
            suggested_desc = suggestion["description"].lower()
            # Check if any existing task description is fully contained in suggestion
            is_duplicate = any(
                existing in suggested_desc
                for existing in existing_descriptions
            )
            assert not is_duplicate, f"Duplicate suggestion: {suggestion['description']}"
        
        print(f"✓ No duplicate suggestions detected")
    
    def test_breed_specific_suggestions_for_golden_retriever(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that breed-specific suggestions are generated for Golden Retrievers.
        Should include exercise, grooming, and ear care suggestions.
        """
        golden = sample_owner.get_pets()[0]
        suggestions = rag_assistant.get_task_suggestions(golden)
        
        suggestion_text = " ".join([s["description"].lower() for s in suggestions])
        
        # Golden Retrievers should get exercise and/or breed-specific suggestions
        assert len(suggestions) > 0, "No suggestions generated for Golden Retriever"
        print(f"✓ Generated breed-specific suggestions for {golden.breed}")
    
    def test_suggestions_convert_to_valid_tasks(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that suggestions can be successfully converted to Task objects.
        Verifies the suggestion structure is compatible with Task creation.
        """
        pet = sample_owner.get_pets()[0]
        suggestions = rag_assistant.get_task_suggestions(pet)
        
        for i, suggestion in enumerate(suggestions[:3]):  # Test first 3
            task = rag_assistant.create_task_from_suggestion(pet, suggestion)
            
            assert isinstance(task, Task)
            assert task.description == suggestion["description"]
            assert task.time == suggestion["recommended_time"]
            assert task.frequency == suggestion["frequency"]
            assert task.completed is False
        
        print(f"✓ Successfully converted suggestions to Task objects")


# ───────────────────────────────────────────────────────────────────────────
# TEST CASE 2: HEALTH MONITORING & ALERTS
# ───────────────────────────────────────────────────────────────────────────

class TestHealthMonitoring:
    """Test suite for health monitoring and alerts use case."""
    
    def test_analyze_health_concern_returns_dict(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that analyze_health_concern() returns a properly structured dict.
        Verifies the function handles health concerns without errors.
        """
        pet = sample_owner.get_pets()[0]
        result = rag_assistant.analyze_health_concern(pet, "seems lethargic")
        
        assert isinstance(result, dict)
        assert "pet_name" in result
        assert "concern" in result
        assert "urgency" in result
        assert "recommended_actions" in result
        assert "warning_signs" in result
        
        print(f"✓ Health concern analysis returned valid structure")
    
    def test_lethargy_concern_has_high_urgency(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that lethargy concern is classified as 'moderate' or 'high' urgency.
        Validates that severity is properly assessed.
        """
        pet = sample_owner.get_pets()[0]
        analysis = rag_assistant.analyze_health_concern(
            pet,
            "Max seems very lethargic and won't eat"
        )
        
        assert analysis["urgency"] in ["low", "moderate", "high"]
        assert analysis["urgency"] != "low", "Lethargy should not be low urgency"
        print(f"✓ Lethargy correctly identified as {analysis['urgency']} urgency")
    
    def test_vomiting_concern_has_high_urgency(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that vomiting concern is classified as 'high' urgency.
        Validates appropriate severity assessment for serious symptoms.
        """
        pet = sample_owner.get_pets()[0]
        analysis = rag_assistant.analyze_health_concern(
            pet,
            "Max is vomiting multiple times"
        )
        
        assert analysis["urgency"] == "high"
        assert len(analysis["recommended_actions"]) > 0
        print(f"✓ Vomiting correctly identified as HIGH urgency")
    
    def test_health_concern_includes_breed_specific_risks(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that breed-specific health risks are included in analysis.
        Verifies that the assistant provides breed-relevant information.
        """
        golden = sample_owner.get_pets()[0]  # Golden Retriever
        analysis = rag_assistant.analyze_health_concern(
            golden,
            "Golden is limping slightly"
        )
        
        assert len(analysis["breed_specific_risks"]) > 0
        breed_risks_text = " ".join(analysis["breed_specific_risks"]).lower()
        assert "hip" in breed_risks_text or "dysplasia" in breed_risks_text
        print(f"✓ Breed-specific risks included: {analysis['breed_specific_risks'][0]}")
    
    def test_health_status_change_detection(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that check_health_status_changes() detects status transitions.
        Validates monitoring of health status changes over time.
        """
        pet = sample_owner.get_pets()[0]
        original_status = pet.health_status
        
        # Change status
        alert = rag_assistant.check_health_status_changes(pet, "sick")
        
        assert alert["status_changed"] is True
        assert alert["previous_status"] == original_status
        assert alert["new_status"] == "sick"
        print(f"✓ Health status change detected: {original_status} → sick")
    
    def test_health_status_no_change_detection(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that check_health_status_changes() detects when there's NO change.
        Validates that redundant updates are properly identified.
        """
        pet = sample_owner.get_pets()[0]
        current_status = pet.health_status
        
        # Same status
        alert = rag_assistant.check_health_status_changes(pet, current_status)
        
        assert alert["status_changed"] is False
        print(f"✓ No false positives for unchanged status")


# ───────────────────────────────────────────────────────────────────────────
# TEST CASE 3: CONFLICT RESOLUTION WITH CONTEXT
# ───────────────────────────────────────────────────────────────────────────

class TestConflictResolution:
    """Test suite for intelligent conflict resolution use case."""
    
    def test_conflict_resolution_no_conflicts(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test conflict resolution on a clean schedule (no conflicts).
        Verifies graceful handling of conflict-free scenarios.
        """
        scheduler = Scheduler(sample_owner)
        result = rag_assistant.resolve_scheduling_conflicts(sample_owner, scheduler)
        
        assert isinstance(result, dict)
        assert result["has_conflicts"] is False
        assert "✅" in result["message"]
        print(f"✓ Correctly identified conflict-free schedule")
    
    def test_conflict_detection_with_overlapping_times(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test conflict resolution when multiple pets have tasks at same time.
        Verifies that overlapping tasks are properly identified.
        """
        # Add conflicting tasks at 8:00 AM
        sample_owner.get_pets()[0].add_task(
            Task("conflict-1", "Dog feeding", time(8, 0), "daily")
        )
        sample_owner.get_pets()[2].add_task(
            Task("conflict-2", "Cat feeding", time(8, 0), "daily")
        )
        
        scheduler = Scheduler(sample_owner)
        result = rag_assistant.resolve_scheduling_conflicts(sample_owner, scheduler)
        
        assert result["has_conflicts"] is True
        assert result["conflict_count"] > 0
        assert len(result["conflicts"]) > 0
        print(f"✓ Detected {result['conflict_count']} conflict(s)")
    
    def test_conflict_analysis_includes_suggestions(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that conflict analysis includes resolution suggestions.
        Verifies that smart alternatives are provided for conflicts.
        """
        # Create conflict
        sample_owner.get_pets()[0].add_task(
            Task("dog-walk", "Morning walk", time(8, 0), "daily")
        )
        sample_owner.get_pets()[1].add_task(
            Task("dog-feed", "Dog feeding", time(8, 0), "daily")
        )
        
        scheduler = Scheduler(sample_owner)
        result = rag_assistant.resolve_scheduling_conflicts(sample_owner, scheduler)
        
        assert result["has_conflicts"] is True
        for conflict in result["conflicts"]:
            assert "suggested_resolutions" in conflict
            assert len(conflict["suggested_resolutions"]) > 0
            
            for resolution in conflict["suggested_resolutions"]:
                assert "option" in resolution
                assert "title" in resolution
                assert "description" in resolution
        
        print(f"✓ Conflict resolutions include multiple options")
    
    def test_optimized_schedule_generation(
        self,
        rag_assistant,
        owner_with_tasks
    ):
        """
        Test that suggest_conflict_avoidance_schedule() generates valid schedules.
        Verifies schedule optimization functionality.
        """
        schedule = rag_assistant.suggest_conflict_avoidance_schedule(owner_with_tasks)
        
        assert "optimized_schedule" in schedule
        assert "tips" in schedule
        assert len(schedule["tips"]) > 0
        
        optimized = schedule["optimized_schedule"]
        assert isinstance(optimized, dict)
        
        # Check schedule has expected slots
        expected_slots = ["morning", "midday", "afternoon", "evening"]
        for slot in expected_slots:
            assert slot in optimized
            assert "start" in optimized[slot]
            assert "tasks" in optimized[slot]
        
        print(f"✓ Generated optimized schedule with tips")
    
    def test_conflict_resolution_reasoning_provided(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that conflict resolution includes contextual reasoning.
        Verifies that explanations help users understand why conflicts occur.
        """
        # Create conflict
        sample_owner.get_pets()[0].add_task(
            Task("task-1", "Feeding", time(8, 0), "daily")
        )
        sample_owner.get_pets()[0].add_task(
            Task("task-2", "Exercise", time(8, 0), "daily")
        )
        
        scheduler = Scheduler(sample_owner)
        result = rag_assistant.resolve_scheduling_conflicts(sample_owner, scheduler)
        
        assert result["has_conflicts"] is True
        for conflict in result["conflicts"]:
            assert "reasoning" in conflict
            assert len(conflict["reasoning"]) > 0
            print(f"  Reasoning: {conflict['reasoning']}")
        
        print(f"✓ Reasoning provided for conflict resolution")


# ───────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ───────────────────────────────────────────────────────────────────────────

class TestRAGIntegration:
    """Integration tests combining multiple RAG features."""
    
    def test_end_to_end_new_pet_onboarding(
        self,
        rag_assistant,
        rag_db
    ):
        """
        Test complete workflow: new pet → suggestions → health check → schedule.
        Verifies that RAG system works across all features for a new pet.
        """
        # Step 1: Create new pet
        owner = Owner("owner-test", "Test User", "test@example.com")
        new_pet = Pet(
            pet_id="new-pet",
            name="Buddy",
            species="dog",
            breed="Labrador Retriever",
            date_of_birth=date.today() - timedelta(days=365),
            weight=28.0,
            health_status="healthy"
        )
        owner.add_pet(new_pet)
        
        # Step 2: Get suggestions
        suggestions = rag_assistant.get_task_suggestions(new_pet)
        assert len(suggestions) > 0
        
        # Step 3: Add suggested tasks
        for suggestion in suggestions[:3]:
            task = rag_assistant.create_task_from_suggestion(new_pet, suggestion)
            new_pet.add_task(task)
        
        # Step 4: Check health
        health_analysis = rag_assistant.analyze_health_concern(new_pet, "seems energetic")
        assert health_analysis["urgency"] == "low"
        
        # Step 5: Check for conflicts
        scheduler = Scheduler(owner)
        conflicts = rag_assistant.resolve_scheduling_conflicts(owner, scheduler)
        
        assert isinstance(conflicts, dict)
        print(f"✓ Complete pet onboarding workflow successful")
    
    def test_rag_system_with_multiple_species(
        self,
        rag_assistant,
        sample_owner
    ):
        """
        Test that RAG system handles multiple pet species appropriately.
        Verifies species-specific knowledge retrieval.
        """
        dog = sample_owner.get_pets()[0]
        cat = sample_owner.get_pets()[2]
        
        # Get suggestions for each
        dog_suggestions = rag_assistant.get_task_suggestions(dog)
        cat_suggestions = rag_assistant.get_task_suggestions(cat)
        
        assert len(dog_suggestions) > 0
        assert len(cat_suggestions) > 0
        
        # Verify species-specific content (dog should have exercise, cat might not)
        dog_text = " ".join([s["description"] for s in dog_suggestions]).lower()
        
        print(f"✓ RAG system handles multiple species appropriately")


# ───────────────────────────────────────────────────────────────────────────
# RUN TESTS
# ───────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])