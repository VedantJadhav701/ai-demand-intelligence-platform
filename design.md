# AI Demand Intelligence — Frontend Design Specification

## 1. Product Identity

Product name:

AI Demand Intelligence

Product type:

Production-oriented demand forecasting and business intelligence platform.

Frontend stack:

- Next.js
- React
- TypeScript
- Tailwind CSS
- Recharts or another lightweight charting library
- Lucide React icons

Deployment:

- Vercel

Backend:

- FastAPI
- Render

ML infrastructure:

- MLflow Model Registry
- CatBoost forecasting models
- SHAP explainability

---

# 2. Product Goal

The frontend should allow a non-technical business user to:

1. Upload historical sales data.
2. Understand dataset quality.
3. Explore demand patterns.
4. Select a store/product.
5. Generate demand forecasts.
6. Understand why a prediction was made.
7. Compare model performance.
8. Monitor model health.
9. Eventually interact with an AI Demand Analyst.

The frontend is NOT an ML notebook UI.

It should present complex ML outputs as clear business decisions and insights.

---

# 3. Core UX Principle

The user should never need to understand:

- lag features
- rolling features
- CatBoost
- MLflow
- SHAP mathematics
- model registry
- API endpoints

The frontend translates technical ML infrastructure into business language.

Example:

DO NOT display:

> `rolling_mean_7 = 153.42`

Instead display:

> **Recent 7-day demand trend**
> Demand has increased 12.4% over the recent period.

Technical details can exist in expandable advanced sections.

---

# 4. Visual Direction

Design style:

## Cinematic Data Intelligence

The interface should feel like a serious AI/ML analytics product.

Characteristics:

- dark-first interface
- high contrast
- restrained use of accent colors
- spacious layouts
- strong typography
- subtle borders
- subtle gradients
- analytical charts
- compact metric cards
- minimal glass effects
- no excessive animations
- no generic "AI SaaS" appearance

Avoid:

- excessive rounded cards
- excessive gradients
- neon everywhere
- excessive glassmorphism
- unnecessary 3D
- animated backgrounds
- oversized illustrations
- cluttered dashboards

The product should look closer to:

> modern quantitative analytics platform

than:

> generic chatbot SaaS.

---

# 5. Theme

Primary theme:

Dark.

Background hierarchy:

```text
App background
    ↓
#08090B

Primary surface
    ↓
#101216

Secondary surface
    ↓
#15181D

Elevated surface
    ↓
#1B1F26

Borders should be subtle.

Use:

rgba(255,255,255,0.08)

for default borders.

Primary text:

#F5F7FA

Secondary text:

#9AA2B1

Muted text:

#626A78

Accent:

Use one primary accent consistently.

Recommended:

Electric Blue

Supporting semantic colors:

Success → Green
Warning → Amber
Danger → Red
Info → Blue

Do not use semantic colors decoratively.

Use them only for meaning.

6. Typography

Use:

Inter

or:

Geist

Primary font:

Geist preferred if available.

Typography hierarchy:

Page title:
32–40px

Section title:
20–24px

Card title:
14–16px

Metric:
28–40px

Body:
14–16px

Metadata:
12–13px

Use font-weight strategically.

Do not make everything bold.

7. Application Layout

Desktop layout:

┌─────────────────────────────────────────────────────────────┐
│ Top Bar                                                     │
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│ Sidebar       │              Main Content                    │
│               │                                             │
│ Navigation    │                                             │
│               │                                             │
│               │                                             │
│               │                                             │
└───────────────┴─────────────────────────────────────────────┘

Sidebar width:

240–260px

Main content:

max-width: 1440px

Centered within available space.

8. Sidebar

Sidebar navigation:

AI Demand Intelligence

Overview

DATA
  Datasets
  Data Quality
  EDA

FORECASTING
  Forecast
  Products
  Stores

ANALYTICS
  Explainability
  Model Performance

MONITORING
  Model Health

AI
  AI Analyst

SYSTEM
  Settings

Use icons.

Example:

Overview        LayoutDashboard
Datasets        Database
Data Quality    ShieldCheck
EDA             ChartSpline
Forecast        TrendingUp
Products        Package
Stores          Store
Explainability  Sparkles
Model           Cpu
Monitoring      Activity
AI Analyst      Bot
Settings        Settings
9. Sidebar Behavior

Desktop:

persistent

Tablet:

collapsible

Mobile:

hidden by default
accessible through menu button

Sidebar should display:

Environment
● Production

at the bottom.

This is useful for communicating that the application is connected to the production API.

10. Top Bar

Top bar:

┌────────────────────────────────────────────────────────────┐
│ ☰   AI Demand Intelligence        Dataset ▼   ● Healthy    │
└────────────────────────────────────────────────────────────┘

Include:

breadcrumb
active dataset
backend status
optional user menu

Backend status:

● API Healthy

Do not expose raw Render URLs in the normal UI.

11. Page 1 — Landing Page

Route:

/

Purpose:

Introduce the product and allow the user to begin.

Hero:

AI Demand Intelligence

Forecast demand.
Understand the drivers.
Make better inventory decisions.

Supporting text:

Turn historical sales data into explainable demand forecasts
and actionable business insights.

Primary CTA:

Upload Sales Data

Secondary CTA:

View Demo Dataset
12. Landing Page Visual

Hero structure:

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│       AI DEMAND INTELLIGENCE                                │
│                                                             │
│       Forecast demand.                                      │
│       Understand the drivers.                               │
│       Make better decisions.                                │
│                                                             │
│       [ Upload Sales Data ]   [ Explore Demo ]              │
│                                                             │
│                         ┌─────────────────────┐              │
│                         │ Forecast            │              │
│                         │                     │              │
│                         │ 194 units           │              │
│                         │ ↑ 12.4%             │              │
│                         │                     │              │
│                         │       ╱╲            │              │
│                         │  ╱───╯  ╰──╲       │              │
│                         └─────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

The right-side visualization is decorative/product preview only.

Do not make it interactive.

13. Page 2 — Dataset Upload

Route:

/datasets

Primary purpose:

Upload and validate data.

Main component:

┌──────────────────────────────────────────┐
│ Upload Sales Dataset                     │
│                                          │
│      ┌────────────────────────┐          │
│      │                        │          │
│      │   Drop CSV / Excel     │          │
│      │                        │          │
│      │   or Browse Files      │          │
│      │                        │          │
│      └────────────────────────┘          │
│                                          │
│ Required:                                │
│ date • store_id • product_id • units_sold│
└──────────────────────────────────────────┘

Show:

supported formats
maximum file size
required columns
optional columns
14. Upload Processing

After upload:

Uploading
    ↓
Validating
    ↓
Profiling
    ↓
Ready

Show progress.

Example:

✓ File uploaded
✓ Schema validated
✓ 125,420 rows processed
✓ 42 stores detected
✓ 318 products detected

Dataset ready

If validation fails:

Dataset validation failed

Missing required column:
units_sold

[ View Validation Details ]

Never simply display:

Error 500.

15. Dataset Summary

After successful upload:

Dataset Overview

Rows          125,420
Stores        42
Products      318
Date Range    Jan 2025 — Aug 2026

Data Quality
████████████████████ 98.8%

Missing values     1.2%
Duplicate rows     0

Use metric cards.

16. Data Quality Page

Route:

/data-quality

Sections:

Data Health
Overall Health
98.8% Healthy
Missing Values

Table:

Column             Missing
price              0.3%
promotion          0.0%
discount           0.7%
inventory          1.1%
Data Issues

Use severity:

✓ No critical issues

⚠ inventory contains 1.1% missing values

✓ No duplicate rows
17. EDA Page

Route:

/eda

Purpose:

Give users a high-level understanding of their sales data.

Do NOT expose every statistical calculation.

Sections:

Demand Overview
Trend
Seasonality
Store Performance
Product Performance
Promotion Impact
Price Relationship
18. EDA Dashboard

Top metrics:

Total Units
Total Revenue*
Average Daily Demand
Demand Volatility

If revenue is target-derived and not independently valid for forecasting, label it as historical descriptive revenue.

Do not imply that revenue is used by the forecasting model.

19. Demand Trend Chart

Large chart:

Demand
  │
  │              ╭────╮
  │        ╭─────╯    ╰───╮
  │   ╭────╯              ╰──
  │───╯
  └────────────────────────────
             Time

Controls:

Daily | Weekly | Monthly

Optional:

7-day moving average
20. Seasonality

Display:

Day-of-week demand

Mon  ███████
Tue  █████████
Wed  ████████
Thu  ██████████
Fri  ███████████
Sat  █████████████
Sun  █████████

Highlight:

Peak: Saturday
Lowest: Monday
21. Store Performance

Table:

Store       Demand       Growth       Status
Store 17    194,200      +18.4%       ↑
Store 12    181,400      +12.1%       ↑
Store 03    98,100       -4.2%        ↓

Allow:

sorting
search
filtering
22. Product Performance

Table:

Product      Units Sold      Growth      Category
Product A    120,400         +22.1%      Electronics
Product B    98,200          +11.3%      Home
Product C    72,100          -2.1%       Grocery

Clicking a product should open its detail view.

23. Forecast Page

Route:

/forecast

This is the primary product page.

Top section:

Demand Forecast

Controls:

Store
[ Store 17 ▼ ]

Product
[ Product A ▼ ]

Forecast Horizon
[ 7 Days ▼ ]

[ Generate Forecast ]
24. Forecast Input Philosophy

The user selects:

store
product
horizon

The system automatically generates:

lag features
rolling features
temporal features
historical statistics

Do NOT expose engineered features to the user.

25. Optional Future Business Inputs

If required by the model, provide:

Future assumptions

Price       [ Auto ]
Promotion   [ None ▼ ]
Discount    [ 0% ]
Holiday     [ Auto ]

Default:

Auto

The user should only modify these when they understand their business scenario.

26. Forecast Result

After prediction:

┌─────────────────────────────────────────────────────────────┐
│ Forecast — Store 17 / Product A                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Expected Demand                                             │
│                                                             │
│ 194 units                                                    │
│ ↑ 28.5% vs previous period                                  │
│                                                             │
│ Model             CatBoost                                  │
│ Horizon           7 days                                    │
│ WAPE              11.27%                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
27. Forecast Chart

Main chart:

Actual
───────────────╮
               ╰────╮
                    ╰───

Forecast
                    ───╮
                       ╰────╮
                            ╰──

                    Today
                      │
                      │
                      ▼

Use:

historical actuals
forecast line
forecast boundary
clear "Today" marker

Do not display prediction intervals unless the backend actually provides them.

28. Forecast Summary

Below chart:

Forecast Summary

Expected demand        194 units
Change vs previous     +28.5%
Forecast horizon       7 days
Model                  CatBoost
Model WAPE             11.27%

CTA:

[ Explain This Forecast ]
29. Explainability Page

Route:

/explainability

or open from forecast.

Headline:

Why did the model predict 194 units?
30. SHAP Explanation

Primary visualization:

Prediction Drivers

Promotion           ███████████ +31%
Lag-7 Demand        ████████    +22%
Weekend             ██████      +15%
Seasonality         █████       +12%
Price               ██           -6%

Positive drivers:

↑

Negative drivers:

↓

Do not use color alone to communicate direction.

Include labels.

31. Explanation Text

Until the SLM exists, generate deterministic template-based explanations.

Example:

The forecast is primarily influenced by recent demand,
promotion activity, and weekly seasonality.

Promotion is the strongest positive contributor.

Price partially offsets the predicted increase.

This is NOT the SLM.

Phase 8 can replace/augment this with the AI Analyst.

32. Advanced Explanation

Expandable section:

Technical Details ▼

Shows:

Feature
Value
SHAP contribution
Direction

Example:

promotion
Value: 1
SHAP: +0.31
Direction: Positive

Technical users can inspect this without overwhelming normal users.

33. Model Performance Page

Route:

/models

Headline:

Model Performance

Top cards:

Production Model
CatBoost

Best WAPE
11.27%

Horizons
4

Model Status
Healthy
34. Model Performance Table
Horizon   Model       CV WAPE    Test WAPE    Source
1 day     CatBoost    11.83%     10.46%       Optuna
7 days    CatBoost    11.27%     10.13%       Optuna
14 days   CatBoost    11.42%     10.17%       Baseline
30 days   CatBoost    11.98%     11.61%       Optuna

This table should come from the backend.

Never hardcode these values.

35. Model Information Drawer

Clicking a model:

CatBoost — 7 Day Forecast

Registry:
demand-catboost-h7

Alias:
production

Selection:
Phase 4 Optuna

CV WAPE:
11.27%

Test WAPE:
10.13%

Feature Version:
phase4_v1

This provides transparency without cluttering the main UI.

36. Monitoring Page

Route:

/monitoring

This page should initially show:

Model Health

● Healthy

Since Phase 7 is not implemented yet, do NOT fabricate drift values.

Display:

Monitoring infrastructure
Coming online in the next release.

Once Phase 7 exists, this page will contain:

PSI
KS
prediction drift
residual drift
model accuracy over time
health status
37. AI Analyst Page

Route:

/analyst

This page is reserved for Phase 8.

Design it now but do not implement the SLM yet.

UI:

┌────────────────────────────────────────────────────────────┐
│ AI Demand Analyst                                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Ask questions about your demand data.                     │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Which products are likely to stock out next month?    │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                            │
│ Suggestions:                                               │
│                                                            │
│ • Why is demand increasing?                                │
│ • Compare Store 17 and Store 12                            │
│ • Which products have highest demand growth?               │
│ • Is the current model performing well?                   │
│                                                            │
│                         [ Ask Analyst ]                    │
└────────────────────────────────────────────────────────────┘

Do not make this page pretend to have an AI backend before Phase 8.

38. AI Analyst Conversation Design

When implemented:

USER

Which stores should increase inventory next month?

AI ANALYST

I analyzed forecasted demand and current inventory.

3 stores have elevated inventory risk.

Store 17
Projected demand: 12,400
Inventory: 9,800
Risk: High

Store 12
Projected demand: 9,100
Inventory: 7,900
Risk: Medium

Include:

Sources / Analysis
Forecast
Inventory
Model explanation

This makes the agent auditable.

39. Inventory Risk

Eventually add:

/risks

Dashboard:

Inventory Risk

HIGH      8 products
MEDIUM   17 products
LOW     293 products

Table:

Product     Forecast     Inventory    Shortage    Risk
Product A   2,240        1,820        420         HIGH
Product C   1,440        1,210        230         MEDIUM

Only implement when inventory calculations exist in the backend.

40. Navigation Flow

Recommended user journey:

Landing
   │
   ▼
Upload Dataset
   │
   ▼
Dataset Summary
   │
   ▼
Data Quality
   │
   ▼
EDA
   │
   ▼
Forecast
   │
   ├──────────────┐
   ▼              ▼
Explain       Model Performance
   │
   └──────────────┐
                  ▼
             AI Analyst

The user should always be able to return to:

Forecast

from any analytics page.

41. Empty States

Never show blank screens.

Example:

No dataset loaded

Upload a sales dataset to begin forecasting.

[ Upload Dataset ]

Forecast:

No forecast generated yet.

Select a store, product and horizon.

[ Configure Forecast ]

AI Analyst:

AI Analyst is not available yet.

The forecasting and explainability systems
are already available.
42. Loading States

Use skeletons instead of blocking spinners where possible.

Forecast:

Generating forecast...

Loading model
██████████░░░

Preparing features
████████████░

Calculating prediction
██████████████

For normal API calls:

Generating...

with subtle animation.

43. Error States

Example:

Forecast unavailable

The production model could not be reached.

Error:
MODEL_SERVICE_UNAVAILABLE

[ Retry ]

Do not expose:

Traceback...
FileNotFoundError...
MLflow internal path...
44. API Health Indicator

Top bar:

● API Healthy

States:

Green:
API Healthy

Amber:
API Degraded

Red:
API Unavailable

This should come from:

GET /health

Do not infer health from frontend loading state.

45. Responsive Design

Desktop:

Primary target.

Tablet:

Sidebar collapses.

Mobile:

Use:

Bottom navigation

or hamburger menu.

Forecast cards should stack vertically.

Charts should remain readable.

Tables should become horizontally scrollable rather than breaking layouts.

46. Accessibility

Required:

keyboard navigation
semantic HTML
accessible buttons
visible focus states
aria labels for icon-only buttons
sufficient contrast
do not rely exclusively on color
charts should have textual summaries

Example:

Instead of only:

green arrow

show:

↑ +28.5%
47. Animation

Use animation sparingly.

Allowed:

page fade-in
card entrance
chart transition
button loading
sidebar transition
skeleton shimmer

Avoid:

constant moving backgrounds
excessive parallax
animated charts that distract from data
large transitions between every page

Animation duration:

150–300ms
48. Charts

Charts must be:

readable
responsive
interactive where useful
tooltip-enabled
properly labeled

Avoid:

3D charts
pie charts when a bar chart communicates better
excessive colors
decorative chart elements

Recommended charts:

Line:
Demand over time

Bar:
Store/product comparison

Horizontal bar:
SHAP drivers

Area:
Demand trend

Heatmap:
Correlation
49. Dashboard Home

Route:

/dashboard

The dashboard should summarize the entire system.

Top:

Good morning

Demand Intelligence Overview

Metric cards:

Total Demand
1.24M units

Forecast Accuracy
11.27% WAPE

Active Stores
42

Products
318

Then:

Demand Trend
─────────────────────────────

Forecast Performance
─────────────────────────────

Top Growing Products
─────────────────────────────

Inventory Risk
─────────────────────────────
50. Dashboard Priority

Information hierarchy:

Business outcome
Forecast
Risk
Explanation
Model performance
Technical details

Do not put MLflow information above business metrics.

51. User Input Model

The user should primarily provide:

Dataset
CSV / Excel
Forecast configuration
Store
Product
Horizon

Optional:

Future price
Promotion
Discount
Holiday

Only if supported by the model.

The user should NOT manually provide:

lag_1
lag_7
lag_14
lag_28
rolling_mean_7
rolling_std_28
day_of_week

The backend generates these automatically.

52. Frontend API Configuration

Use:

NEXT_PUBLIC_API_URL=https://<render-backend-url>

Local:

NEXT_PUBLIC_API_URL=http://localhost:8000

Production:

NEXT_PUBLIC_API_URL=https://your-api.onrender.com

Never hardcode the API URL in components.

Create:

src/lib/api.ts

as the central API client.

53. API Client Structure

Recommended:

src/lib/
├── api.ts
├── types.ts
└── constants.ts

Example API methods:

getHealth()
getModels()
getMetrics()
generateForecast()
generateBatchForecast()
explainForecast()

Do not make direct fetch() calls throughout individual components.

54. Component Architecture

Recommended:

src/components/
├── layout/
│   ├── Sidebar.tsx
│   ├── Topbar.tsx
│   └── PageContainer.tsx
│
├── dashboard/
│   ├── MetricCard.tsx
│   ├── DemandChart.tsx
│   └── PerformanceCard.tsx
│
├── forecast/
│   ├── ForecastForm.tsx
│   ├── ForecastResult.tsx
│   ├── ForecastChart.tsx
│   └── ForecastSummary.tsx
│
├── explainability/
│   ├── ShapChart.tsx
│   └── FeatureContribution.tsx
│
├── datasets/
│   ├── UploadZone.tsx
│   ├── DatasetSummary.tsx
│   └── ValidationReport.tsx
│
├── models/
│   ├── ModelTable.tsx
│   └── ModelDetails.tsx
│
└── common/
    ├── Button.tsx
    ├── Card.tsx
    ├── Badge.tsx
    ├── Skeleton.tsx
    └── EmptyState.tsx

Use reusable components.

55. State Management

Avoid introducing a heavy state management library initially.

Use:

React state
React Query / TanStack Query for API/server state

Use server state for:

models
metrics
health
forecast results

Do not duplicate API data unnecessarily in multiple global stores.

56. Data Upload State

Maintain:

idle
uploading
validating
processing
ready
error

UI should reflect the current state.

57. Forecast State

Maintain:

idle
loading
success
error

Do not show stale forecast results as if they correspond to a new request.

Display the selected:

store
product
horizon

alongside the result.

58. Security

Never expose:

MLflow credentials
backend secrets
registry credentials
API keys

Only NEXT_PUBLIC_* variables are exposed to the browser.

The frontend should communicate only with the public FastAPI endpoints.

59. Performance

Optimize:

chart rendering
large tables
dataset lists
unnecessary API calls

Use pagination for large datasets.

Do not load the entire sales dataset into the browser.

The browser should never receive the complete raw dataset unless specifically required.

60. SEO

Landing page should have:

Title:

AI Demand Intelligence — Explainable Demand Forecasting

Description:

Forecast demand, understand prediction drivers, and turn sales data
into actionable business insights.

Dashboard pages can be application-focused and need not prioritize SEO.

61. Production Deployment

Frontend:

GitHub
   ↓
Vercel
   ↓
Next.js

Backend:

GitHub
   ↓
Render
   ↓
Docker
   ↓
FastAPI

Communication:

Vercel
   │
   │ HTTPS
   ▼
Render FastAPI

Environment:

Vercel:
NEXT_PUBLIC_API_URL

Render:
MLFLOW_TRACKING_URI
MLFLOW_EXPERIMENT_NAME
MODEL_REGISTRY_PREFIX
ALLOWED_ORIGINS
ENVIRONMENT
62. Phase Implementation Boundary

The frontend implementation should be staged.

Phase 6 frontend readiness

Only establish:

API contract
CORS
response schemas
frontend environment variable convention
Phase 9

Actually build:

dashboard
dataset upload UI
forecast UI
model performance UI
explainability UI
monitoring UI
Phase 8

Build:

AI Analyst UI
chat interface
tool execution visualization

Do not prematurely implement AI functionality.

63. Final Product Navigation

Final navigation:

OVERVIEW
Dashboard

DATA
Datasets
Data Quality
EDA

FORECASTING
Forecast
Products
Stores

ANALYTICS
Explainability
Model Performance

MONITORING
Model Health

AI
AI Analyst

SYSTEM
Settings
64. Final Design Principle

The product should answer these questions immediately:

What is going to happen?

Forecast.

Why is it happening?

Explainability.

What should I do?

Business insights / AI Analyst.

Can I trust the model?

Model performance + monitoring.

Is the system healthy?

System/model health.

The user should never need to understand the underlying implementation to use the product.

65. Definition of a Successful UI

A successful frontend should allow a new user to:

Open the website.
Understand what the product does within 10 seconds.
Upload a dataset.
Understand whether the dataset is valid.
Select a store.
Select a product.
Select a forecast horizon.
Generate a forecast.
Understand the result.
See why the model produced it.
Inspect model reliability.
Eventually ask natural-language questions.

The experience should feel like:

DATA
  ↓
UNDERSTAND
  ↓
FORECAST
  ↓
EXPLAIN
  ↓
DECIDE

not:

Upload CSV
↓
Run ML model
↓
Show random charts
66. Final UI Architecture
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │   VERCEL    │
                    │   Next.js   │
                    └──────┬──────┘
                           │
                    HTTPS REST API
                           │
                           ▼
                    ┌─────────────┐
                    │   RENDER    │
                    │   FastAPI   │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Forecast       SHAP        Analytics
             │             │
             └─────────────┼─────────────┘
                           ▼
                     MLflow Registry
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
           H1 Model       H7 Model      H14/H30
                           │
                           ▼
                     Production

Future:

                    FastAPI
                       │
                ┌──────┴──────┐
                ▼             ▼
             ML/SHAP       AI Analyst
                              │
                              ▼
                             SLM
                              │
                         Tool Calling
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
            Forecast      Inventory       Analytics

The frontend should therefore be built as a business intelligence application with an AI layer, not as a chatbot with some charts attached.


### Recommended implementation order

When you give this to Antigravity, **don't ask it to build the entire frontend at once**. Use:

```text
Frontend Phase A → Design system + layout
Frontend Phase B → Dataset + EDA
Frontend Phase C → Forecast + charts
Frontend Phase D → Explainability + model performance
Frontend Phase E → Monitoring
Frontend Phase F → AI Analyst
Frontend Phase G → Production Vercel deployment