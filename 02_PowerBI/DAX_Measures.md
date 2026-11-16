# DAX measures (generated from build_pbip.py, so this file always matches the model)

All measures live in the `_Measures` table. Calculated columns are on `agg_child_summary`.

## Calculated column: `agg_child_summary[Value Group]`
```DAX
VAR HiFee = agg_child_summary[billed_inr] >= MEDIAN ( agg_child_summary[billed_inr] )
VAR HiPP  = agg_child_summary[progress_points] >= MEDIAN ( agg_child_summary[progress_points] )
RETURN SWITCH ( TRUE (), HiFee && HiPP, "Thriving", NOT HiFee && HiPP, "Efficient", HiFee && NOT HiPP, "Under-served", "At-risk" )
```

## Calculated column: `agg_child_summary[Fee Tier]`
```DAX
SWITCH ( TRUE (), agg_child_summary[monthly_fee_inr] < 12000, "1 Under 12k", agg_child_summary[monthly_fee_inr] < 15000, "2 12k-15k", "3 15k and above" )
```


## Core

### Students
```DAX
Students =
DISTINCTCOUNT ( dim_child[child_id] )
```
Format: `0`

### Therapists
```DAX
Therapists =
DISTINCTCOUNT ( dim_therapist[therapist_id] )
```
Format: `0`

### Sessions Held
```DAX
Sessions Held =
CALCULATE ( COUNTROWS ( fact_session ), fact_session[is_past] = 1 )
```
Format: `#,##0`

### Sessions Attended
```DAX
Sessions Attended =
CALCULATE ( COUNTROWS ( fact_session ), fact_session[is_attended] = 1 )
```
Format: `#,##0`

### Attendance %
```DAX
Attendance % =
DIVIDE ( [Sessions Attended], [Sessions Held] )
```
Format: `0.0%`

### Avg Session Score
```DAX
Avg Session Score =
AVERAGE ( fact_session[avg_session_score] )
```
Format: `0.00`


## Value

### Progress Points
```DAX
Progress Points =
SUM ( agg_child_summary[progress_points] )
```
Format: `#,##0.0`

### Fees INR
```DAX
Fees INR =
SUM ( agg_child_summary[billed_inr] )
```
Format: `"₹"#,##0`

### League Progress Points
```DAX
League Progress Points =
CALCULATE ( [Progress Points], ALL ( agg_child_summary ), ALL ( dim_child ) )
```
Format: `#,##0.0`

### League Fees INR
```DAX
League Fees INR =
CALCULATE ( [Fees INR], ALL ( agg_child_summary ), ALL ( dim_child ) )
```
Format: `"₹"#,##0`

### Outcome Value Index
```DAX
Outcome Value Index =
DIVIDE ( DIVIDE ( [Progress Points], [League Progress Points] ), DIVIDE ( [Fees INR], [League Fees INR] ) )
```
Format: `0.00`

### Fair Value INR
```DAX
Fair Value INR =
[League Fees INR] * DIVIDE ( [Progress Points], [League Progress Points] )
```
Format: `"₹"#,##0`

### Overpay INR
```DAX
Overpay INR =
[Fees INR] - [Fair Value INR]
```
Format: `"₹"#,##0;-"₹"#,##0`

### Therapist Progress Points
```DAX
Therapist Progress Points =
SUM ( fact_child_therapist[attributed_progress_points] )
```
Format: `#,##0.0`

### Therapist Fees INR
```DAX
Therapist Fees INR =
SUM ( fact_child_therapist[attributed_fees_inr] )
```
Format: `"₹"#,##0`

### Therapist Value Index
```DAX
Therapist Value Index =
VAR LeaguePP = CALCULATE ( [Therapist Progress Points], ALL ( fact_child_therapist ), ALL ( dim_therapist ), ALL ( dim_child ) )
VAR LeagueFee = CALCULATE ( [Therapist Fees INR], ALL ( fact_child_therapist ), ALL ( dim_therapist ), ALL ( dim_child ) )
RETURN DIVIDE ( DIVIDE ( [Therapist Progress Points], LeaguePP ), DIVIDE ( [Therapist Fees INR], LeagueFee ) )
```
Format: `0.00`

### Thriving
```DAX
Thriving =
CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "Thriving" )
```
Format: `0`

### Efficient
```DAX
Efficient =
CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "Efficient" )
```
Format: `0`

### Under-served
```DAX
Under-served =
CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "Under-served" )
```
Format: `0`

### At-risk
```DAX
At-risk =
CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[Value Group] = "At-risk" )
```
Format: `0`

### Value Group Colour
```DAX
Value Group Colour =
SWITCH ( SELECTEDVALUE ( agg_child_summary[Value Group] ), "Thriving", "#5B7DB1", "Efficient", "#3BA55C", "Under-served", "#E5484D", "#8C8C8C" )
```
Format: `text (colour hex)`

### Value Index Colour
```DAX
Value Index Colour =
IF ( [Outcome Value Index] >= 1, "#3BA55C", "#E5484D" )
```
Format: `text (colour hex)`


## Clinical

### Avg Improvement pts
```DAX
Avg Improvement pts =
AVERAGE ( agg_child_summary[improvement_pts] )
```
Format: `0.0`

### Children Improved %
```DAX
Children Improved % =
DIVIDE ( CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[improvement_pts] > 0 ), COUNTROWS ( agg_child_summary ) )
```
Format: `0%`

### Avg Overall Score
```DAX
Avg Overall Score =
AVERAGE ( fact_assessment[overall_score_pct] )
```
Format: `0.0`

### Latest Overall Score
```DAX
Latest Overall Score =
AVERAGE ( agg_child_summary[latest_overall_score] )
```
Format: `0.0`

### Red-Risk Children
```DAX
Red-Risk Children =
CALCULATE ( COUNTROWS ( agg_child_summary ), agg_child_summary[latest_risk] = "red" )
```
Format: `0`

### Risk Improved Children
```DAX
Risk Improved Children =
SUM ( agg_child_summary[risk_improved] )
```
Format: `0`

### Churn-Risk Children
```DAX
Churn-Risk Children =
SUM ( agg_child_summary[churn_risk] )
```
Format: `0`

### Churn-Risk %
```DAX
Churn-Risk % =
DIVIDE ( [Churn-Risk Children], COUNTROWS ( agg_child_summary ) )
```
Format: `0%`

### Domain Score
```DAX
Domain Score =
AVERAGE ( fact_assessment_domain[score] )
```
Format: `0.0`

### Domain Gain pts
```DAX
Domain Gain pts =
CALCULATE ( AVERAGE ( fact_assessment_domain[score] ), fact_assessment_domain[is_latest] = 1 ) - CALCULATE ( AVERAGE ( fact_assessment_domain[score] ), fact_assessment_domain[is_initial] = 1 )
```
Format: `0.0`

### Domain Latest Score
```DAX
Domain Latest Score =
CALCULATE ( AVERAGE ( fact_assessment_domain[score] ), fact_assessment_domain[is_latest] = 1 )
```
Format: `0.0`

### Goal Completion %
```DAX
Goal Completion % =
DIVIDE ( SUM ( fact_goal[is_completed] ), COUNTROWS ( fact_goal ) )
```
Format: `0%`

### Home Tasks per Week
```DAX
Home Tasks per Week =
AVERAGE ( fact_home_engagement_weekly[home_tasks_logged] )
```
Format: `0.0`

### Meals Logged per Week
```DAX
Meals Logged per Week =
AVERAGE ( fact_home_engagement_weekly[meals_logged] )
```
Format: `0.0`


## Alerts

### Alerts Raised
```DAX
Alerts Raised =
COUNTROWS ( fact_alert )
```
Format: `0`

### Open Alerts
```DAX
Open Alerts =
SUM ( fact_alert[is_open] )
```
Format: `0`

### High Severity Alerts
```DAX
High Severity Alerts =
CALCULATE ( COUNTROWS ( fact_alert ), fact_alert[severity] = "high" )
```
Format: `0`

### Avg Hrs to Acknowledge
```DAX
Avg Hrs to Acknowledge =
AVERAGE ( fact_alert[hours_to_acknowledge] )
```
Format: `0.0`

### Avg Hrs to Resolve
```DAX
Avg Hrs to Resolve =
AVERAGE ( fact_alert[hours_to_resolve] )
```
Format: `0.0`

### Acknowledged within 4h %
```DAX
Acknowledged within 4h % =
DIVIDE ( CALCULATE ( COUNTROWS ( fact_alert ), fact_alert[hours_to_acknowledge] <= 4, NOT ( ISBLANK ( fact_alert[hours_to_acknowledge] ) ) ), CALCULATE ( COUNTROWS ( fact_alert ), NOT ( ISBLANK ( fact_alert[hours_to_acknowledge] ) ) ) )
```
Format: `0%`


## Revenue

### Billed INR
```DAX
Billed INR =
CALCULATE ( SUM ( fact_payment[amount_inr] ), fact_payment[payment_type] = "subscription" )
```
Format: `"₹"#,##0`

### Collected INR
```DAX
Collected INR =
CALCULATE ( SUM ( fact_payment[paid_amount_inr] ), fact_payment[payment_type] = "subscription" )
```
Format: `"₹"#,##0`

### Outstanding INR
```DAX
Outstanding INR =
CALCULATE ( SUM ( fact_payment[outstanding_inr] ), fact_payment[payment_type] = "subscription" )
```
Format: `"₹"#,##0`

### Collection %
```DAX
Collection % =
DIVIDE ( [Collected INR], [Billed INR] )
```
Format: `0.0%`

### Failed Payments
```DAX
Failed Payments =
CALCULATE ( COUNTROWS ( fact_payment ), fact_payment[status] = "failed", fact_payment[payment_type] = "subscription" )
```
Format: `0`

### Payment Count
```DAX
Payment Count =
CALCULATE ( COUNTROWS ( fact_payment ), fact_payment[payment_type] = "subscription" )
```
Format: `0`


## QA

### League Value Index Check
```DAX
League Value Index Check =
CALCULATE ( [Outcome Value Index], ALL ( dim_child ), ALL ( agg_child_summary ) )
```
Format: `0.000`

### Sessions Rows
```DAX
Sessions Rows =
COUNTROWS ( fact_session )
```
Format: `#,##0`

### Assessment Rows
```DAX
Assessment Rows =
COUNTROWS ( fact_assessment )
```
Format: `#,##0`

### Payment Rows
```DAX
Payment Rows =
COUNTROWS ( fact_payment )
```
Format: `#,##0`

### Alert Rows
```DAX
Alert Rows =
COUNTROWS ( fact_alert )
```
Format: `#,##0`
