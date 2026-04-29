# PawPal+ Project Reflection

---

## 6. Reflection and Ethics: Thinking Critically About My AI

### Limitations and Biases in the System

PawPal+'s RAG system retrieves answers from a knowledge base I wrote, which means its "knowledge" is only as complete and unbiased as what I put into it. Right now the knowledge base covers dogs and cats, and within dogs it has breed-specific guidance for Golden Retrievers and German Shepherds only. An owner with a Dachshund, a Persian cat, or a rabbit would get generic responses or no breed-specific suggestions at all — the system would silently fall back to general guidelines without warning the user that it lacks specific knowledge for their pet.

The health concern analysis has a more serious bias: it only recognizes three symptom categories (lethargy, vomiting, ear issues). Any concern that doesn't contain those exact keywords — "my dog isn't acting like himself," "she's been hiding under the bed," "he's drinking a lot of water" — returns a `"monitor"` urgency with no recommended actions. The system appears to respond but gives the user nothing useful. That's a form of false confidence: the app looks like it analyzed the concern when it actually didn't.

There is also a weight-based bias in the exercise suggestions. The system classifies dogs over 50 kg as "large breed" needing 60+ minutes of exercise, and all others as needing 30–45 minutes. A 6 kg Chihuahua and a 40 kg Labrador get the same suggestion, which is incorrect. Weight alone is a poor proxy for exercise needs — breed energy level, age, and health status all matter more.

---

### Could the System Be Misused, and How Would I Prevent It?

The most realistic misuse is over-reliance. A user who types "my cat is vomiting blood" and receives a `"monitor"` urgency (because the keyword matching only catches "vomiting," not the severity context) might delay going to a vet. The system was never designed to replace veterinary advice, but nothing in the current UI makes that boundary explicit.

To prevent this I would add a persistent disclaimer on the health monitoring tab — something like "This tool is not a substitute for professional veterinary advice. If your pet is in distress, contact a vet immediately." I would also add a hard override: any concern containing words like "blood," "seizure," "not breathing," or "unconscious" should immediately return a `"high"` urgency with a single action — call a vet now — regardless of what the knowledge base returns.

A secondary misuse risk is data privacy. The app stores pet names, health statuses, and owner emails in Streamlit session state, which resets on refresh but could be logged by a deployed server. If this app were hosted publicly, I would not collect real personal information without a clear privacy policy and proper data storage practices.

---

### What Surprised Me While Testing Reliability

The biggest surprise was how confidently the system returns a result even when it has no real information to give. When I tested a health concern like "Whiskers has been hiding under the bed," the system returned an urgency color, an empty recommended actions list, and no warning signs — formatted exactly like a real response. There was no indication to the user that nothing matched. I had assumed an AI system would either give a good answer or say it didn't know. I did not expect it to give a well-formatted non-answer that looked authoritative.

The duplicate suggestion logic also behaved unexpectedly. The deduplication check looks for whether an existing task description is contained in the suggestion description using substring matching. In testing, a pet with an existing task called "Feeding" caused the system to suppress a suggestion called "Dog feeding - twice daily" because `"feeding"` appeared in both strings. That's overly aggressive — the existing task was one word, the suggestion was a full scheduled recommendation. The filter intended to help ended up silently removing valid suggestions.

---

### AI Collaboration: One Helpful Suggestion, One Flawed One

**Helpful:** When the conflict resolution UI crashed with `StreamlitAPIException: Expanders may not be nested inside other expanders`, Claude identified the root cause immediately — Streamlit's layout engine does not allow an `st.expander` inside another `st.expander` — and suggested replacing the inner expanders with `st.container(border=True)`. This was genuinely useful because the error message alone didn't make it obvious what the fix should be, and the suggestion preserved the visual structure of the UI without requiring a redesign.

**Flawed:** Early in the project, the AI suggested `chroma-client==0.4.0` as the ChromaDB package name in `requirements.txt`. This package does not exist on PyPI — the correct name is `chromadb`. Running `pip install -r requirements.txt` failed immediately with `No matching distribution found`. The AI had either hallucinated the package name or confused it with an internal or deprecated alias. This was a good reminder that AI suggestions about specific library names and version numbers should always be verified against the actual package index (pypi.org) before trusting them, especially for newer or rapidly changing libraries like ChromaDB.

---

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
There are three core actions a user should be able to perform: seeing today's daily plan, adding pets, and scheduling medications or grooming appointments. 


- What classes did you include, and what responsibilities did you assign to each?

The first class I designed is called Pet. It should describe the pet's necessary details like name, species, breed, and update/deleting methods. The next class I designed is called User. The owner can create their account login/contact details, along with methods to get their pet's info and notifications. The next class I designed is called Medications. This class is in charge of recording specific frequencies, dosages, reminders, and which pets received their medications. The next class I implemented is called Walks. This class will help owners track the durations, distances, locations, and dates for when they've walked their pets. The next important class I designed is called Feedings. This class should track the brand of food, the dates/logs of feeding times, and which pet(s) ate what food. The next important class I implemented is called appointments. This class tracked the reasons for visits, locations and dates, and necessary appointment reminders. In addition, I also designed the class HealthRecord, so that Owners can easily get a report on their pet's health. Finally, I decided to make the app more robust by adding a Reminder and Dashboard class, which will help with notifications for walks/feeds, etc and for owners to get a clear display of their todo tasks for ease of access.


**b. Design changes**

- Did your design change during implementation?
Yes

- If yes, describe at least one change and why you made it.
Copilot analyzed that there are missing relationships between certain classes. To begin with, the Pet class should be represeted in Activity classes, so a missing pet_id attribute is needed for the constructor (examples: dashboard, reminders, healthRecord). Next, the User class needs to be accountable for their Pet class, which could break accountability and multi-user support. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

My schedular only considers time right now as a constraint, but adding more constraints would be interesting! Like adding a preference for walks instead of feeding for example for conflicting tasks.

- How did you decide which constraints mattered most?

To me, schedular had to prioritize events which had time conflicts, since this would probably be more common, and using preferences/priority could be solutions to this problem. Fortunately, the AI suggested to do warnings, which with more implementation I think a priority algorithm would be very interesting.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My schedular currently uses a linear search for every task lookup. For a robust app, this tradeoff is code simplicity over raw performance. This tradeoff is reasonable since this project is an introduction in using these algorithms. 
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used copilot and claude!

- What kinds of prompts or questions were most helpful?

Following the prompts from the codepath's instructions gave me clear directions for what the app's next step was. I appreciated having step by step guidance, and it definetly helped navigate creating this project from ground up independently. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

I did not like a couple of the first skeletons that the AI gave me from my UML. 

- How did you evaluate or verify what the AI suggested?

I realized that my UML had a lot of unecessary functions, some of which felt redundant with others in the same class and could actually result in bottlenecks down the line. I verified the owner-pet relationships, pet identification with task and schedular classes, as these bottlenecks, for which claude helped me navigate using a different constructor and added getter methods. 
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
My first test began to make sure that mark_complete() actually changes the task's status. The next test was to verify that adding a task to a Pet increases the pet's task count. The next test was to make sure that the schedular appropriately handles recurring tasks. The following test was also related to schedular, and verified that tasks with conflicting times were handled appropriately. Finally, my last test suite deals with the filter_tasks function which previously did not handle edge cases with mark_test_complete() where pets with a bad ID could crash, or with get_pet_by_ID() could have a missing ID.

- Why were these tests important?

All of these tests are important because they deal with the true purpose of this app. To ensure that the functionality of pawpal+ works, it is important to consider that owners can see their pet's tasks being added to their todo lists for readability, clarity, and so that the app feels useful. In addition, adding test cases for task conflicts, edge cases like bad IDs/missing IDs, case sensitivity, etc ensure that this app has few bugs upon launch.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am 5 stars confident! I have 24 tests in my test suite that all pass. If I had more time, I think exploring the priority feature for time conflicts in the schedular would be exciting to see in action!

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
Looking at the streamlit app, I am very satisfied with the simplicity and the straightforwardness of the application. I think it accomplishes its goals clearly, and I learned a lot about how to implement three kinds of algorithms, UML diagrams, and prompt engineering.
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had more time, I would add the priority/preference constraints for schedular. Seeing schedular manage my tasks with time conflicts was interesting, however, I think adding more constraints would make the app feel more robust and easier to work with for real-world problems. I think a little more UI to make the app feel engaging would have been interesting too.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned the value of identifying the right level of abstraction early. Building a Scheduler class that handles all the logic — sorting, filtering, conflict detection, recurrence — kept Pet and Task simple and reusable. Separating what data is from what the system does with it made everything easier to test and extend.