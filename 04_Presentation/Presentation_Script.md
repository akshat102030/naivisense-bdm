# NaiviSense Therapy Outcome Value: Presentation Script

Target length about 10 minutes. 50 children · 8 therapists · May–Nov 2026 · synthetic data.

## 0 Introduction and the one idea · 1:15
**SHOW:** Home page: title, five KPI cards, six question cards.

Good morning, sir. Our project is NaiviSense Therapy Outcome Value Intelligence. A therapy centre bills families every month, but the fee does not say how much a child actually progressed. Our question: which therapy spend earned its price?
We built a synthetic centre of 50 children and 8 therapists from the NaiviSense MongoDB data model: 6,024 sessions, ₹4,188,500 of fees, May to November 2026.
The whole dashboard rests on one idea. First, Progress Points: one score for clinical change, session quality and goals: 10 times the assessment gain, 20 times the session-score gain, 5 per goal completed. Then the Outcome Value Index: what share of the centre's progress did this child get, compared with the share of the centre's fees they paid? 1.0 is fair value. Above 1 the family got more than they paid for; below 1, less.
The six cards are our six business questions, and each one is a page.

## 1 Therapy: therapist and therapy-type efficiency · 1:00
**SHOW:** The therapist value-index bars (dashed line = 1.0), then the scorecard table.

Q1: who gives the most progress per rupee? Fees are similar across therapy types, so differences come from delivery. OT is at 1.05 and speech at 1.02; behaviour and special education sit just below 1.
Between therapists the spread is wider: Kavya Iyer leads at 1.19, Amit Joshi trails at 0.88. We share each child's progress and fees between therapists by their share of attended sessions.

**So what:** Coach low-index therapists using the routines of high-index peers.

## 2 Value Map · 1:15
**SHOW:** The scatter. Point to the dashed median lines and the four corners. Hover one dot.

Q2: which children are getting value? Every dot is a child. Fees paid run left to right; progress points bottom to top. The dashed lines are the median fee and median progress, which split children into four groups.
Thriving: high fee, high progress, 20 children. Efficient: low fee, high progress, 5. Under-served: high fee, low progress, 5. At-risk: low fee, low progress, 20.

**So what:** Keep Thriving and Efficient plans; review Under-served and re-engage At-risk before they drop out.

## 3 At-Risk: who to call · 0:50
**SHOW:** The three lists: churn-risk, Under-served, Efficient.

This page names the children. 9 are at churn risk: attendance below 70 percent, or a red clinical band with little gain, or two failed payments. 12 are still in the red band, although 22 children moved to a better band. Right-click any child to drill through to a profile with score history, goals and alerts.

**So what:** Call the churn-risk families this week.

## 4 Drivers: attendance and parent involvement · 1:15
**SHOW:** Attendance-vs-improvement scatter with the dashed trend, then value index by involvement.

Q3: what drives progress? Attendance and improvement go together, r = +0.46. Monthly fee level barely does, r = +0.23.
The clearest lever is parent involvement. High-involvement families get 1.31 times fair value, low-involvement 0.71. They attend 91% against 72%, and improve 13.2 points against 5.4.
By fee tier the index barely moves, 0.97 to 1.05. Paying more neither buys nor loses value per rupee.

**So what:** Spend effort on parent coaching and attendance recovery, not on higher-priced plans.

## 5 Domains · 0:45
**SHOW:** The domain-gain bar chart.

Q4: which domains improve fastest? visual perception gains 13.1 points and attention 11.4. The slowest are emotional regulation at 8.5 and imitation at 8.6.

**So what:** Add targeted therapy blocks for the slowest domains.

## 6 Alerts · 0:50
**SHOW:** Hours-to-acknowledge by severity.

Q5: are safety alerts handled in time? Of 133 alerts, 5 are open. High-severity alerts are acknowledged in 1.6 hours and every one within 4 hours. Medium and low alerts wait about 16.1 hours, and only about 6% are acknowledged within 4 hours.

**So what:** Triage works for severe cases; set a same-day target for routine alerts.

## 7 Revenue · 0:50
**SHOW:** Billed vs collected by month, then the outstanding list.

Q6: where does revenue leak? We billed ₹4,188,500 and collected ₹3,295,000, 79%. 18 payments failed and ₹785,500 is outstanding. The gap is not concentrated in low-involvement families: collection is 81% for low and 75% for high.

**So what:** Automate retries and reminders for every family.

## 8 Methodology, data and architecture · 0:50
**SHOW:** Methodology page, then the architecture figure or Model view.

The data come from the NaiviSense MongoDB model. We generate 50 synthetic children with a fixed seed and store them twice: a raw layer exactly as the app saves it, and a processed star schema with dimensions and facts. Power BI reads the processed layer; all 53 measures are written in DAX.
Data flow in one line: app collections, raw layer, processing script, processed layer in MongoDB and CSV, Power BI model, dashboard.
Our own check: a separate Python script recomputes every number from the processed files, and the centre value index is exactly 1.0.

## 9 Conclusion · 0:40
**SHOW:** Back to Home.

Three lessons for a therapy centre. One: parent involvement and attendance move value more than price does. Two: severe cases and routine alerts are where the centre under-serves today. Three: judge plans by progress per rupee, not by fee. Thank you, sir. We are happy to take questions.

## Likely questions: short answers

**Why not just use the assessment score?** Scores, session quality and goals measure different things. Progress Points combine them on one scale so children with different baselines can be compared.

**Why compare with the centre's own totals?** Shares of centre progress and centre fees remove the effect of the overall scale, so the index is a fair relative measure and averages exactly 1.0.

**Is this real data?** No. It is synthetic, generated from the app's data model with designed relationships, so the findings demonstrate the method. The same pipeline can run on real collections.

**Why are the weights 10, 20 and 5?** They are a modelling choice that balances clinical change, session quality and goals; they should be agreed with clinicians, and the index is easy to recompute with different weights.

**Why MongoDB, and why two layers?** The app already stores data in MongoDB. The raw layer is the audit copy; the processed layer is flat and analysis-ready, which Power BI needs.

**Limitations?** Synthetic data, seven months, therapist attribution proportional to sessions rather than causal, and small subgroups such as Cerebral Palsy (2 children).

**Did you check the DAX in Power BI?** The numbers are verified by an independent Python script; the QA page in the report carries the expected values for the final check in Desktop.
