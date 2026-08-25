# AI Demand Intelligence & Forecasting Platform

## 1. Project Overview

Build a production-oriented AI Demand Intelligence platform that combines:

- Data Science
- Time-Series Forecasting
- Machine Learning
- Explainable AI
- MLOps
- Model Monitoring
- Small Language Model (SLM)
- Tool-using / agentic analytics
- REST API
- Interactive web dashboard

The system should allow a business user to upload historical sales data, configure a forecasting task, generate demand forecasts, understand the reasons behind predictions, identify inventory risks, monitor model health, and interact with the system using natural language.

The SLM is NOT the primary numerical forecasting model.

The forecasting models perform numerical prediction.

The SLM acts as an intelligent analytics and explanation layer that interprets structured outputs and calls deterministic analytics/forecasting tools.

---

# 2. Core Product Concept

The user-facing workflow is:

User\
→ Upload sales data\
→ Validate data\
→ Configure forecast\
→ Generate forecast\
→ View forecast\
→ Understand forecast\
→ Check inventory/business risks\
→ Ask natural-language questions\
→ Receive analytical recommendations

The backend workflow is:

Raw Data\
→ Validation\
→ EDA\
→ Feature Engineering\
→ Time-Series Split\
→ Baseline Models\
→ ML Models\
→ Walk-Forward Evaluation\
→ Hyperparameter Optimization\
→ Best Model Selection\
→ MLflow Tracking\
→ Model Registry\
→ Prediction\
→ SHAP Explanation\
→ Drift Monitoring\
→ API\
→ SLM Analyst\
→ Dashboard

---

# 3. Main Design Principle

Separate deterministic computation from language generation.

## Numerical / analytical responsibilities

These must be performed by deterministic code:

- Data validation
- Aggregations
- Feature engineering
- Forecasting
- Metrics
- Statistical tests
- Inventory calculations
- Drift calculations
- SHAP values
- Model comparisons

## SLM responsibilities

The SLM can:

- Understand natural-language questions
- Select appropriate tools
- Interpret structured analytical results
- Explain predictions
- Summarize trends
- Compare stores/products
- Generate business-oriented recommendations
- Generate reports
- Ask clarification questions when required

The SLM must NOT invent numerical results.

If a number is required, the SLM must obtain it from a tool or structured backend result.

---

# 4. Target Users

## Business User

Needs:

- Demand forecast
- Sales trends
- Inventory risk
- Product/store comparison
- Business recommendations
- Natural-language analytics

## Data Scientist

Needs:

- EDA
- Feature engineering
- Model benchmarking
- Error analysis
- SHAP explanations
- Experiment comparison

## ML Engineer

Needs:

- Reproducible pipelines
- MLflow
- Model registry
- API
- Docker
- Monitoring
- Drift detection
- Retraining capability

---

# 5. Dataset Requirements

The system should initially support tabular sales datasets.

Expected minimum columns:

- date
- store\_id
- product\_id
- units\_sold

Optional columns:

- revenue
- price
- discount
- promotion
- holiday
- store\_type
- product\_category
- inventory
- region

The system must NOT assume that every optional column exists.

Create a data schema and automatically determine which features are available.

The system should produce a clear validation report when required columns are missing.

---

# 6. Data Validation

Implement validation before EDA or training.

Validate:

- Required columns
- Data types
- Date parsing
- Duplicate records
- Missing values
- Negative sales
- Invalid prices
- Invalid discounts
- Invalid categorical values
- Date continuity
- Store/product identifiers
- Numerical ranges

Use a validation layer that can be reused by training and inference.

Do not silently modify invalid data.

Record all transformations.

---

# 7. Exploratory Data Analysis

Build a reusable EDA pipeline.

Analyze:

## Data quality

- Missing values
- Duplicate rows
- Invalid values
- Cardinality

## Distribution

- Sales distribution
- Revenue distribution
- Price distribution
- Discount distribution

## Time-series behavior

- Trend
- Seasonality
- Weekly patterns
- Monthly patterns
- Yearly patterns
- Demand volatility

## Business segmentation

- Store segmentation
- Product segmentation
- Product category segmentation
- High/low-volume products
- High/low-revenue stores

## Relationships

- Correlation analysis
- Price vs demand
- Promotion vs demand
- Discount vs demand
- Holiday vs demand

## Decomposition

Where appropriate:

- Trend
- Seasonal component
- Residual component

EDA outputs should be reproducible.

---

# 8. Feature Engineering

Create a configurable feature engineering pipeline.

Required temporal features:

- day\_of\_week
- day\_of\_month
- week\_of\_year
- month
- quarter
- year
- is\_weekend
- is\_month\_start
- is\_month\_end

Required lag features:

- lag\_1
- lag\_7
- lag\_14
- lag\_28

Required rolling features:

- rolling\_mean\_7
- rolling\_mean\_14
- rolling\_mean\_28
- rolling\_std\_7
- rolling\_std\_28

Optional:

- rolling\_min
- rolling\_max
- exponentially weighted mean
- price\_change
- discount\_change
- promotion indicators

Categorical features:

- store\_type
- product\_category
- store\_id
- product\_id

CRITICAL:

Avoid target leakage.

All lag and rolling features must only use information available before the prediction timestamp.

Never calculate features using future observations.

---

# 9. Forecasting Problem Definition

Initially implement supervised multi-step demand forecasting using engineered temporal features.

Primary target:

units\_sold

The architecture should later support:

- revenue forecasting
- product-level forecasting
- store-level forecasting
- aggregated forecasting

Initial forecast horizons:

- 7 days
- 14 days
- 30 days

Make the horizon configurable.

---

# 10. Baseline Models

Always establish baselines before advanced models.

Implement:

1. Naive Forecast
2. Seasonal Naive Forecast

Example:

Naive:\
prediction[t] = actual[t-1]

Seasonal Naive:\
prediction[t] = actual[t-7]

The baselines must appear in the model leaderboard.

---

# 11. Machine Learning Models

Implement the following models where compatible with the dataset:

1. Linear Regression
2. Random Forest
3. XGBoost
4. LightGBM
5. CatBoost

Primary models of interest:

- LightGBM
- CatBoost
- XGBoost

Do not add deep learning until the classical ML benchmark is complete.

---

# 12. Deep Learning

Deep learning is optional.

Possible future models:

- LSTM
- N-BEATS
- Temporal Fusion Transformer

Do not implement these during the initial MVP.

Only add them after establishing a strong classical ML baseline.

---

# 13. Time-Series Evaluation

NEVER use a random train/test split.

Use chronological splitting.

Example:

## Training

## Validation

## Test

Use walk-forward / rolling-origin validation.

Possible structure:

Fold 1:\
Train → Validation

Fold 2:\
Train + previous validation → Validation

Fold 3:\
Train + previous observations → Validation

The exact implementation should avoid future information leaking into earlier folds.

---

# 14. Evaluation Metrics

Calculate:

- MAE
- RMSE
- MAPE
- sMAPE
- WAPE

Be careful with MAPE when actual demand contains zeros.

If necessary, use an epsilon or exclude undefined observations while reporting the handling explicitly.

For business interpretation, prioritize:

- MAE
- WAPE
- sMAPE

The final leaderboard should contain:

| Model | MAE | RMSE | MAPE | sMAPE | WAPE | Training Time | Inference Time |
| ----- | --: | ---: | ---: | ----: | ---: | ------------: | -------------: |

---

# 15. Model Selection

Do not automatically select the model solely using one metric.

Primary selection metric:

WAPE

Secondary metrics:

MAE\
sMAPE\
RMSE

Also consider:

- inference latency
- training cost
- model complexity

The selected production model must be documented.

---

# 16. Hyperparameter Optimization

Use Optuna.

Tune appropriate parameters for:

- LightGBM
- XGBoost
- CatBoost

Use time-series-aware validation inside the optimization objective.

Do not use ordinary random K-fold cross-validation.

Use early stopping wherever supported.

Store Optuna results.

---

# 17. Model Explainability

Use SHAP for tree-based models.

For every prediction, allow the system to return:

- prediction
- top positive features
- top negative features
- SHAP values
- feature values

Example:

Prediction:

194 units

Explanation:

Promotion +31%\
Lag-7 Demand +22%\
Weekend +15%\
Seasonality +12%\
Price -6%

The backend should return structured explanation data.

The SLM can convert this into natural language.

---

# 18. Prediction Intervals

The system should support uncertainty estimates.

Do not present a point prediction as certainty.

Preferred output:

Forecast: 194 units\
80% interval: 170–219\
95% interval: 160–230

The initial implementation can use an appropriate statistical/conformal approach.

Do not fabricate confidence intervals.

Clearly distinguish:

- prediction interval
- confidence interval

---

# 19. Inventory Intelligence

Where inventory information is available, calculate:

- projected demand
- available inventory
- projected shortage
- excess inventory
- stockout risk
- recommended inventory level

Example:

Expected demand = 194\
Safety stock = 32\
Recommended stock = 226\
Current inventory = 180

Projected shortage = 46

The business recommendation must come from deterministic calculations.

The SLM only explains the result.

---

# 20. MLflow

Use MLflow for:

- experiment tracking
- parameters
- metrics
- artifacts
- dataset information
- model versions

Register production models.

Track:

- model name
- model version
- training dataset
- feature version
- code version
- evaluation metrics

Every production prediction should be traceable to a model version.

---

# 21. Model Registry

Maintain model lifecycle:

Candidate\
→ Validation\
→ Staging\
→ Production\
→ Archived

Only validated models can become production models.

Do not automatically replace the production model simply because a new model was trained.

Require comparison against the current production model.

---

# 22. Drift Monitoring

Implement:

## Feature drift

- PSI
- KS test

Monitor important features such as:

- price
- promotion
- lag\_7
- lag\_28
- store\_type
- product\_category

## Prediction drift

Monitor:

- prediction distribution
- prediction mean
- prediction variance

## Residual monitoring

When actual values become available:

- residual distribution
- MAE over time
- WAPE over time
- forecast bias

Example:

Model Status: HEALTHY

price: 2.1% ✓\
promotion: 3.4% ✓\
lag\_7: 7.8% ✓\
store\_type: 1.2% ✓

---

# 23. Retraining

The system should eventually support:

New Data\
→ Validation\
→ Drift Check\
→ Retraining Trigger\
→ Train Candidate\
→ Evaluate\
→ Compare with Production\
→ Register Candidate\
→ Promote if better

Do not automatically retrain on every request.

Retraining should be an explicit pipeline or controlled trigger.

---

# 24. SLM Analyst

Add an SLM after the forecasting and analytics systems are stable.

The SLM is an analytics assistant.

Possible models:

- Qwen
- Gemma
- another suitable local SLM

Keep the SLM provider/model configurable.

The SLM should receive structured context, not the entire raw dataset.

---

# 25. SLM Tool Architecture

Create tools such as:

forecast\_demand()\
get\_sales\_summary()\
get\_store\_performance()\
get\_product\_performance()\
compare\_stores()\
compare\_products()\
get\_top\_products()\
get\_inventory\_risk()\
get\_model\_metrics()\
get\_model\_explanation()\
get\_drift\_status()\
get\_forecast\_history()

Each tool must return structured JSON.

The SLM must not directly execute arbitrary Python code.

The SLM should only call approved tools.

---

# 26. Example SLM Interaction

User:

"Why is demand increasing for Store 17?"

SLM:

1. Determine that forecast and explanation information are required.
2. Call forecast\_demand().
3. Call get\_model\_explanation().
4. Receive structured results.
5. Explain the results.

Example answer:

"Demand for Store 17 is projected to increase by 28.5%. The main drivers are the active promotion, higher demand seven days earlier, and weekend seasonality. Price is partially offsetting the increase."

The numerical values must originate from backend tools.

---

# 27. Agentic Analytics

Support natural-language questions such as:

"Which products will likely stock out next month?"

"Compare Store 12 and Store 17."

"What are the biggest demand drivers?"

"Why did demand fall last week?"

"Which products have the highest forecast uncertainty?"

"Show me stores where demand is increasing but inventory is low."

"How accurate is the current production model?"

"Is the model experiencing drift?"

The SLM should determine which tools are necessary.

---

# 28. SLM Safety Rules

The SLM must:

- Never invent metrics.
- Never invent predictions.
- Never invent inventory levels.
- Never invent model versions.
- Never claim a model is healthy without monitoring data.
- Never perform numerical calculations when a backend tool can provide the value.
- Never access arbitrary files.
- Never execute arbitrary code.
- Clearly state when required data is unavailable.

If data is insufficient:

"I cannot determine that from the available data."

---

# 29. Backend API

Use FastAPI.

Initial endpoints:

POST /predict\
POST /batch\_predict\
POST /forecast\
GET /model\
GET /health\
GET /metrics\
GET /drift\
GET /explain\
POST /chat

Possible future endpoints:

GET /stores\
GET /products\
GET /forecast/history\
GET /inventory/risk

Use Pydantic request/response schemas.

Do not expose internal Python objects directly.

---

# 30. API Architecture

Frontend\
→ FastAPI\
→ Service Layer\
→ ML/Analytics Layer\
→ Model/Registry

For SLM:

Frontend\
→ /chat\
→ SLM Analyst\
→ Approved Tools\
→ Analytics/ML Services\
→ Structured Results\
→ SLM\
→ Response

---

# 31. Frontend

Use Next.js + React.

The UI should focus on business usefulness.

Main pages:

## Dashboard

Show:

- forecast summary
- demand trend
- revenue
- inventory risk
- model health

## Forecast

Show:

- forecast chart
- actual vs predicted
- prediction intervals
- filters

## Explainability

Show:

- SHAP feature importance
- per-prediction explanation

## Model Performance

Show:

- model leaderboard
- MAE
- RMSE
- WAPE
- sMAPE
- inference latency

## Monitoring

Show:

- drift
- residuals
- model version
- system health

## AI Analyst

Chat interface for natural-language analytics.

---

# 32. Dashboard Design Principle

Do not spend most of the project on frontend design.

The ML system is the primary project.

The dashboard should be:

- clean
- professional
- data-focused
- responsive
- easy to understand

Avoid unnecessary animations and visual complexity.

---

# 33. Docker

Containerize:

- FastAPI
- frontend
- MLflow

Use Docker Compose for local development where appropriate.

Do not unnecessarily containerize training jobs during the initial implementation.

---

# 34. Testing

Add tests for:

- data validation
- feature generation
- leakage prevention
- metric calculations
- forecasting
- API schemas
- tool outputs
- drift calculations

Critical tests:

1. Lag features must not use future data.
2. Rolling features must not use future data.
3. Test data must not influence training.
4. SLM cannot directly access arbitrary functions.
5. Tool outputs must follow schemas.

---

# 35. Configuration

Do not hardcode:

- model parameters
- paths
- API keys
- SLM model names
- forecast horizon
- thresholds

Use configuration files and environment variables.

Example:

configs/model.yaml\
configs/data.yaml\
configs/experiment.yaml

Secrets belong in .env.

Never commit .env.

---

# 36. Reproducibility

Every experiment should record:

- random seed
- dataset identifier
- feature configuration
- model configuration
- code version
- metrics

Training must be reproducible.

---

# 37. Development Order

Do NOT build everything simultaneously.

Follow this order:

PHASE 1\
Project setup\
→ data ingestion\
→ validation

PHASE 2\
EDA\
→ feature engineering

PHASE 3\
Baselines\
→ ML models\
→ time-series evaluation

PHASE 4\
Optuna\
→ model selection\
→ SHAP

PHASE 5\
MLflow\
→ model registry

PHASE 6\
Prediction service\
→ FastAPI\
→ Docker

PHASE 7\
Monitoring\
→ drift\
→ residual monitoring

PHASE 8\
SLM Analyst\
→ tools\
→ structured tool outputs\
→ natural-language explanations

PHASE 9\
Next.js dashboard

PHASE 10\
Integration\
→ testing\
→ documentation\
→ deployment

---

# 38. MVP Definition

The MVP is complete when:

1. User can provide a sales dataset.
2. Dataset is validated.
3. Features are generated without leakage.
4. Baselines are calculated.
5. Multiple ML models are benchmarked.
6. Time-series validation is used.
7. Best model is selected.
8. Forecast can be generated.
9. SHAP explanation is available.
10. MLflow tracks experiments.
11. FastAPI exposes predictions.
12. Basic drift monitoring works.
13. SLM can answer analytical questions through tools.

The dashboard is not required for the first MVP.

---

# 39. Engineering Rules

Follow these rules throughout the project:

- Prefer modular code.
- Avoid giant Python files.
- Separate data, features, models, evaluation and services.
- Use type hints.
- Use Pydantic for API schemas.
- Use logging instead of print statements in production code.
- Handle exceptions explicitly.
- Validate inputs.
- Never silently swallow errors.
- Avoid unnecessary dependencies.
- Keep functions small and testable.
- Write docstrings for important public functions.
- Keep configuration separate from code.
- Never hardcode secrets.
- Never leak future information into training.
- Never fabricate metrics.

---

# 40. Antigravity Execution Rule

When implementing this project, work one phase at a time.

Before moving to the next phase:

1. Implement the phase.
2. Run tests.
3. Run the relevant pipeline.
4. Inspect outputs.
5. Fix errors.
6. Document the result.
7. Only then proceed.

Do not create placeholder implementations for major ML components merely to make the application appear complete.

Prefer a smaller working implementation over a large incomplete architecture.

---

# 41. Definition of Success

The final system should demonstrate:

Data Science:\
EDA + feature engineering + statistical analysis

Machine Learning:\
Forecasting + benchmarking + optimization

Time-Series:\
Walk-forward validation + temporal feature engineering

Explainable AI:\
SHAP + prediction explanations

MLOps:\
MLflow + model registry + monitoring

ML Engineering:\
FastAPI + Docker + modular pipelines

SLM:\
Tool-using analytics assistant

Agentic AI:\
Natural-language orchestration of forecasting and analytics tools

Frontend:\
Professional analytics dashboard

The final project should look and behave like a real production ML product rather than a collection of notebooks.
