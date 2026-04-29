"""
Pet care knowledge base — seed data for the vector database
"""

PET_CARE_DOCUMENTS = [
    # Dog care
    {
        "id": "dog_exercise_001",
        "category": "exercise",
        "species": "dog",
        "content": """
        Dogs need daily exercise. General guidelines:
        - Small breeds (under 25 lbs): 30 minutes daily
        - Medium breeds (25-50 lbs): 45-60 minutes daily
        - Large breeds (50+ lbs): 60-90 minutes daily
        - Puppies: 5 minutes per month of age, 2-3 times daily
        - Senior dogs (7+ years): 20-30 minutes daily, low-impact
        Exercise prevents obesity, behavioral issues, and anxiety.
        """
    },
    {
        "id": "dog_feeding_001",
        "category": "feeding",
        "species": "dog",
        "content": """
        Dog feeding guidelines:
        - Adult dogs: 1-2 meals per day
        - Puppies (under 6 months): 3-4 meals per day
        - Senior dogs: 2 meals per day
        - Feed at consistent times daily
        - Measure portions based on weight and activity level
        - Fresh water always available
        Common feeding times: 8 AM and 6 PM
        """
    },
    {
        "id": "golden_retriever_breed_001",
        "category": "breed_specific",
        "species": "dog",
        "breed": "golden_retriever",
        "content": """
        Golden Retriever care:
        - Exercise: 60+ minutes daily (high energy breed)
        - Grooming: Brush 3-4 times weekly, bathe monthly
        - Health concerns: Hip dysplasia, ear infections (floppy ears)
        - Training: Highly intelligent, responds well to positive reinforcement
        - Temperament: Friendly, good with families
        - Age to maturity: 18-24 months
        """
    },
    # Cat care
    {
        "id": "cat_feeding_001",
        "category": "feeding",
        "species": "cat",
        "content": """
        Cat feeding guidelines:
        - Adult cats: 1-2 meals per day
        - Kittens: 3-4 meals per day
        - Senior cats (10+ years): 1-2 meals per day
        - Portion size: 200-250 calories for average adult cat
        - Feed at consistent times to prevent begging
        - Wet food mixed with dry is ideal
        - Always provide fresh water
        """
    },
    {
        "id": "cat_health_001",
        "category": "health",
        "species": "cat",
        "content": """
        Common cat health issues:
        - Lethargy: Check hydration, appetite, temperature. Vet if persists 24+ hours
        - Vomiting: Could be hairballs, diet change, or illness. Monitor frequency
        - Litter box issues: Stress, UTI, or health problem. Change food/litter
        - Ear infections: Floppy-eared breeds prone. Clean ears weekly
        - Diabetes: More common in overweight cats. Watch for excessive thirst
        """
    },
    # General health
    {
        "id": "vaccination_schedule_001",
        "category": "health",
        "content": """
        Pet vaccination timeline:
        - Age 6-8 weeks: First vaccines (DHPP for dogs, FVRCP for cats)
        - Age 10-12 weeks: Second vaccine round
        - Age 14-16 weeks: Third vaccine round, Rabies
        - Age 1 year: First adult booster
        - Age 2+ years: Boosters every 1-3 years depending on vaccine
        Schedule vet checkup immediately after getting a new pet.
        """
    },
    {
        "id": "conflict_resolution_001",
        "category": "scheduling",
        "content": """
        Optimal pet scheduling practices:
        - Feed dogs before walks (15-30 min after eating is best for activity)
        - Don't feed cats during times they might vomit from excitement
        - Schedule quiet time after training/exercise (20-30 minutes cool down)
        - Multi-pet feeding: Separate locations prevent fighting
        - Exercise timing: Dogs more receptive early morning or evening
        """
    }
]