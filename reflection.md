# PawPal+ Project Reflection

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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
