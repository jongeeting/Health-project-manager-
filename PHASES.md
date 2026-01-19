# Development Phases
# Health Management SMS System

This document outlines all planned phases for the health management system.

---

## ✅ Phase 1: Symptom Tracking (COMPLETE)

**Status:** Fully functional and ready to deploy

### Features
- Automated check-in messages (8am, 8pm by default)
- Free-text symptom logging via SMS
- Claude API natural language parsing
- Symptom extraction (name, severity, notes)
- Trigger identification (foods, activities, stress)
- Mood and energy tracking
- Google Sheets data storage
- Friendly confirmation messages

### Data Logged
- Timestamp
- Symptoms with severity ratings
- Potential triggers
- Mood/energy notes
- Raw message text
- Summary

### User Experience
```
System: "How are you feeling today? 💙"
User: "Bad bloating, 7/10. Had dairy at lunch."
System: "Logged! bloating (7/10). Trigger: dairy. Feel better ❤️"
```

### Technical Stack
- Twilio for SMS
- Claude API for parsing
- Google Sheets for storage
- APScheduler for automated check-ins
- Flask webhook server

---

## 📋 Phase 2: Medication & Supplement Tracking

**Status:** Planned - Build after Phase 1 is working well

### Features

#### Daily Medication Adherence
- Integrated with morning check-in: "Did you take your meds?"
- Standalone logging: Text "took meds" or "meds done"
- Track multiple medications
- Timestamp each dose
- Track adherence percentage

#### Refill Management
- Track medication supply counts
- Set initial supply and daily dosage
- Auto-calculate days remaining
- Reminder 5 days before running out
- Log refill dates

#### Side Effect Tracking
- Correlate symptoms with medication timing
- Flag symptoms within 2 hours of dose
- Monthly report of potential side effects
- Pattern detection across time

### Data Added to Google Sheets
- New "Medication Log" worksheet
- Columns: Date, Time, Medications Taken, Missed Doses, Notes
- Integration with symptom tracking sheet

### User Experience
```
System: "How are you feeling? Did you take your meds?"
User: "Feeling okay. Took prenatal."
System: "Logged! Prenatal vitamin ✓. No major symptoms today."

[5 days later]
System: "You have 5 days of prenatal vitamins left - time to refill? 💊"
User: "Refilled"
System: "Great! Logged refill. You're all set! ❤️"
```

### Technical Changes
- Add medication database to Google Sheets
- Track supply counts
- Calculate refill reminders
- Enhanced Claude parser for medication mentions
- New scheduler jobs for refill reminders

---

## 🌙 Phase 3: Menstrual Cycle Tracking

**Status:** Planned

### Features

#### Cycle Tracking
- Log period start: Text "period started"
- Auto-calculate cycle day (1-28+)
- Determine cycle phase (Menstrual, Follicular, Ovulatory, Luteal)
- Average cycle length calculation

#### Symptom Correlation
- Automatically tag symptoms with cycle day and phase
- Pattern detection: "Bloating occurs 85% of luteal phase days"
- Phase-specific symptom severity tracking
- Predict symptom likelihood based on cycle phase

#### Reports
- Symptom patterns by cycle phase
- Average symptom severity per phase
- Cycle length trends
- Ovulation prediction (based on typical cycle)

### Data Added to Google Sheets
- Cycle Day column (auto-calculated)
- Cycle Phase column (auto-calculated)
- New "Cycle Tracking" worksheet with period start dates
- Enhanced reports with phase correlations

### User Experience
```
User: "period started"
System: "Logged! Starting new cycle. Day 1. ❤️"

[Symptom logging]
User: "Bloating 8/10, nausea, cramps"
System: "Logged! bloating (8/10), nausea, cramps. Menstrual day 2. Feel better ❤️"

[Monthly report]
System: "Monthly insights: Bloating averages 7.5/10 during luteal phase vs 3.2/10 during follicular phase. Pain occurs 90% of menstrual phase days."
```

### Technical Changes
- Period date tracker
- Cycle day calculator
- Phase determination logic
- Enhanced pattern detection
- Correlation analysis in reports

---

## 📅 Phase 4: Appointment Management

**Status:** Planned

### Features

#### Email Monitoring
- Monitor dedicated Gmail inbox
- Parse appointment-related emails
- Detect: appointment offers, confirmations, reschedule requests
- Extract: provider, date/time options, appointment type

#### Scheduling Workflow
- Text user with appointment options
- User replies with choice
- System drafts email response
- Text draft for approval
- Send email on confirmation
- Create Google Calendar event automatically

#### Appointment Database
- Provider name, specialty
- Appointment date/time
- Purpose/type
- Status (scheduled/completed/cancelled)
- Location
- Notes

#### Pre-Appointment Support
- 1 week reminder: "GI appointment next Thursday. Reply with your top 3 concerns"
- Collect and save concerns
- Auto-generate symptom summary for timeframe
- 1 day reminder with summary and concerns

#### Follow-up Tracking
- Post-appointment text: "How did it go? Any follow-ups needed?"
- Track: labs ordered, imaging needed, referrals
- Reminder for follow-up tasks

### Data Added
- New "Appointments" worksheet
- Google Calendar integration
- Email → SMS → Email workflow

### User Experience
```
[Email arrives from doctor's office]
System: "Dr. Smith's office - available Tuesday 3pm or Thursday 10am. Which works?"
User: "Thursday 10am"
System: "Send this? 'Thursday at 10am works, see you then'"
User: "yes"
System: "Sent! Calendar event created. Thursday 10am with Dr. Smith. ✓"

[1 week before]
System: "GI appointment next Thursday at 10am. Reply with your top 3 concerns to discuss"
User: "1. Bloating getting worse 2. Night sweats 3. Constipation"

[1 day before]
System: "Appointment tomorrow at 10am with Dr. Smith (GI). Your concerns: bloating, night sweats, constipation. Past 30 days: bloating 18x (avg 6.5/10), worse after dairy; nausea 12x; constipation 15x"
```

### Technical Changes
- Gmail API integration
- Email parsing (appointment-specific)
- Google Calendar API
- Email drafting and sending
- Multi-step conversation tracking
- Symptom summary generation

---

## 👥 Phase 5: Provider Coordination

**Status:** Planned

### Features

#### Communication Hub
- Text to email: "email Dr. Smith about pain getting worse"
- Claude drafts email based on recent symptom data
- Include relevant timeline events
- User approval before sending

#### Provider Timeline
- Track: Date, Provider, Event type
- Event types: appointment, test, diagnosis, treatment change
- Query: Text "timeline" for recent history
- Useful for new providers or specialists

#### Care Team Directory
- Provider name, specialty
- Contact info
- What they're treating
- Last visit date
- Next scheduled appointment
- Notes

#### Medical Records References
- Track test results mentioned
- Link to appointments where discussed
- Reference in future communications

### Data Added
- "Provider Directory" worksheet
- "Timeline" worksheet
- Email templates for common communications

### User Experience
```
User: "email Dr. Smith about pain getting worse"
System: "Draft email to Dr. Smith (GI):

Subject: Increasing Abdominal Pain

Hi Dr. Smith,

I wanted to update you on my symptoms since our last visit on Jan 15. My abdominal pain has increased significantly - averaging 7.5/10 over the past week compared to 4/10 previously. I've also noticed increased bloating (15 episodes in past 14 days) and the pain is worse after meals.

Would you recommend scheduling a follow-up appointment or making any changes to my current treatment plan?

Thank you,
[Your name]

Send this?"

User: "yes"
System: "Sent to Dr. Smith! I'll let you know if she replies. ❤️"
```

---

## 📊 Phase 6: Reporting & Insights

**Status:** Planned

### Features

#### Weekly Summary (Automated)
- Sent every Sunday evening
- Symptom frequency and trends
- Medication adherence rate
- Upcoming appointments
- Outstanding follow-up tasks

#### On-Demand Reports
- "report" → Past 30 days symptom summary
- "meds" → Medication adherence past week
- "appointments" → Upcoming and recent
- "timeline" → Chronological care events
- "cycle" → Current phase and typical patterns

#### Appointment Prep Packet
- "prep for Dr. Smith"
- Symptom summary since last visit
- Current medications
- Questions/concerns
- Relevant timeline events
- Test results mentioned

#### Pattern Detection
- Symptom-trigger correlations
- Cycle phase patterns
- Time-of-day patterns
- Medication effectiveness
- Monthly insights text

### Reports Generated
- Symptom frequency charts
- Severity trend graphs
- Trigger correlation analysis
- Cycle phase comparisons
- Medication adherence trends

### User Experience
```
[Sunday evening]
System: "Weekly Summary:

Symptoms this week:
- Bloating: 4x (avg 6/10)
- Nausea: 2x
- Pain: 3x (avg 5/10)

Medications: 6/7 days (85%)

Upcoming:
- Dr. Smith (GI) - Thu Jan 25, 10am
- Lab work needed (ordered by Dr. Jones)

Triggers noticed: Pain 2x higher after dairy"

---

User: "prep for Dr. Smith"
System: "Appointment Prep - Dr. Smith (GI) - Thu 10am

Since last visit (Dec 15):
- Bloating: 18x (avg 6.5/10), worse after dairy
- Nausea: 12x
- Constipation: 15x
- Night sweats: 8x

Your questions:
1. Bloating getting worse
2. Night sweats
3. Constipation

Recent timeline:
- Dec 20: Ultrasound (awaiting results)
- Jan 5: Started probiotics
- Jan 10: Bloating increased to 8/10

Current meds: Prenatal vitamin (daily)

Ready to discuss! Good luck at your appointment! ❤️"
```

---

## 💰 Phase 7: Insurance & Admin Tracking

**Status:** Planned (Final Phase)

### Features

#### Claims Monitoring
- Log claim submission: "submitted claim for ultrasound $450"
- Track claim status
- Reminder 2 weeks later: "Has insurance processed your claim?"
- Log: claim date, amount, provider, status, amount paid

#### Spending Tracker
- Running total of out-of-pocket spending
- Track toward deductible
- Track toward out-of-pocket maximum
- Monthly spending summary
- Year-end summary

#### Insurance Information
- Store: Insurance company, policy number, group number
- Deductible amount and progress
- Out-of-pocket max and progress
- Coverage details

### Data Added
- "Insurance Claims" worksheet
- "Healthcare Spending" worksheet
- Deductible/OOP tracking

### User Experience
```
User: "submitted claim for ultrasound $450"
System: "Logged! Claim for $450 (ultrasound). I'll check in about this in 2 weeks. ✓"

[2 weeks later]
System: "Has insurance processed your ultrasound claim ($450)?"
User: "yes, they paid $360"
System: "Great! Logged. Your out-of-pocket: $90. Year-to-date spending: $1,245. $755 toward your $2,000 deductible. ✓"

[End of month]
System: "January Healthcare Spending:
Total billed: $1,200
Insurance paid: $850
You paid: $350

Progress:
Deductible: $1,245/$2,000 (62%)
Out-of-pocket max: $1,245/$5,000 (25%)"
```

---

## Development Approach

### For Each Phase:

1. **Design**
   - Review requirements
   - Design data schema
   - Plan user interactions
   - Identify API needs

2. **Build**
   - Create new modules
   - Update existing modules
   - Add database/sheet columns
   - Write tests

3. **Test**
   - Unit test each component
   - Integration testing
   - User acceptance testing
   - Debugging

4. **Deploy**
   - Update production environment
   - Database migrations
   - Monitor for issues

5. **Iterate**
   - Use for 1-2 weeks
   - Gather feedback
   - Make improvements
   - Move to next phase when ready

### Recommended Pace

- **Phase 1:** Use for 2-4 weeks to validate concept
- **Phase 2:** Add when medication adherence becomes important
- **Phase 3:** Add when cycle tracking would be valuable
- **Phase 4:** Add when managing multiple appointments
- **Phase 5:** Add when coordinating multiple providers
- **Phase 6:** Add when you want deeper insights
- **Phase 7:** Add if insurance tracking becomes important

**Don't rush!** Each phase adds complexity. Make sure previous phase is working well before adding more.

---

## Phase Independence

Some phases can be built independently:
- Phase 2 (Medications) doesn't require Phase 3 (Cycle)
- Phase 6 (Reports) can be added anytime
- Phase 7 (Insurance) is fully independent

Others have dependencies:
- Phase 3 (Cycle) enhances Phase 1 symptom data
- Phase 6 (Reports) benefits from Phases 1-3 data
- Phase 5 (Provider coordination) uses Phase 4 appointment data

---

## Maintenance & Updates

Between phases:
- Monitor API costs
- Review data quality
- Fix any bugs found
- Optimize performance
- Add small quality-of-life improvements

---

## Long-term Vision

Eventually this system will:
- Provide comprehensive health tracking via text
- Reduce cognitive load for health management
- Identify patterns you wouldn't notice manually
- Coordinate care across providers
- Track all health-related admin tasks
- Generate insights for better health outcomes

All while being:
- ADHD-friendly (low friction, automated prompts)
- Privacy-first (your data in your Google Sheet)
- Customizable (adjust to your needs)
- Reliable (runs 24/7 in the cloud)

---

## Your Pace, Your System

This is YOUR health management system. Build phases as you need them, skip ones you don't, and customize to fit your life.

Start with Phase 1, use it until it feels natural, then decide what to build next!
