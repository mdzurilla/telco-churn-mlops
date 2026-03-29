# Customer Churn Prediction (Telco)

![Python](https://img.shields.io/badge/Python-3.13-blue)

An end-to-end machine learning project focused on predicting and **prioritizing customer churn risk** in a telecom setting.

This project goes beyond model training — it demonstrates how to design a **reproducible, artifact-driven ML system**, compare multiple modeling approaches, and translate predictions into **actionable business decisions**.

---

## 🚀 Overview

Customer churn is a key challenge for subscription-based businesses. Identifying customers at risk of leaving enables targeted retention strategies and reduces revenue loss.

This project builds a complete churn prediction workflow with a strong emphasis on:

- **Reproducibility** through configuration-driven pipelines  
- **Model comparison** across multiple algorithm families  
- **Decision-aware evaluation** using threshold analysis  
- **Business alignment**, focusing on ranking customers and actionable insights  

---

## 🎯 Business Objective

The goal is not only to predict churn, but to:

1. **Rank customers by likelihood of churn**  
2. **Prioritize high-risk customers for intervention**  
3. **Understand key drivers of churn** to inform retention strategies  

---

## 📊 Dataset

**Telco Customer Churn Dataset**  
https://www.kaggle.com/datasets/blastchar/telco-customer-churn

| Metric        | Value     |
|--------------|----------|
| Customers     | 7,043     |
| Features      | 21        |
| Churn rate    | ~26.5%    |
| Industry      | Telecom   |

The dataset includes:
- Customer demographics  
- Subscription details  
- Contract and billing information  
- Service usage patterns  
- Binary churn outcome  

---

## 🧠 Project Highlights

### 🔹 Reproducible Data Pipeline

A key feature of this project is a **configuration-driven preprocessing pipeline**:

- Transformation logic stored in **JSON artifacts**
- Applied sequentially via a reusable function
- Ensures consistent feature engineering across datasets

This design mirrors production systems where:
- data transformations must be reproducible
- training and scoring pipelines must stay aligned

---

### 🔹 Model Families Evaluated

Multiple modeling approaches were explored and compared:

- Logistic Regression (baseline + interpretable model)
- Decision Tree
- Random Forest
- Histogram Gradient Boosting
- XGBoost / LightGBM
- Support Vector Machines (linear & RBF)
- Neural Networks (PyTorch)

Each model is stored as a **self-contained artifact**, including:
- trained model
- feature configuration
- column alignment
- scaling (if required)

---

### 🔹 Artifact-Driven Evaluation

All models are evaluated using:

- the **same hold-out test set**
- identical preprocessing pipeline
- model-specific feature reconstruction

This ensures:
- fair comparison
- no data leakage
- full reproducibility

---

### 🔹 Threshold Analysis (Key Insight)

Instead of relying on a fixed classification threshold (0.5), the project explores:

- performance across threshold ranges
- precision–recall trade-offs
- F1 optimization per model
- global threshold stability

**Key finding:**
> Threshold selection has a comparable impact on performance as model choice.

---

### 🔹 Global Decision Rule

A unified threshold (~0.31) was identified across models.

Using this shared threshold:
- model rankings shift significantly
- tree-based ensembles outperform neural networks
- recall improves substantially across all models

This demonstrates:
- the importance of decision calibration
- the feasibility of a consistent deployment strategy

---

## 🏆 Final Model Selection

The **Histogram-based Gradient Boosting model** was selected as the final model.

### Why?

- Best **ROC-AUC and PR-AUC** → strongest ranking capability  
- Competitive **F1-score** under global threshold  
- Stable performance across thresholds  

👉 This makes it ideal for:
- prioritizing high-risk customers  
- supporting targeted retention campaigns  

---

## 🔍 Interpretability Strategy

While the final model focuses on predictive performance, **interpretability remains critical**.

This project combines:

- **Gradient Boosting** → ranking and prediction  
- **Logistic Regression** → interpretable feature effects  

This enables a two-step workflow:

1. **Identify high-risk customers**  
2. **Understand drivers of churn and inform interventions**

---

## 🧩 Project Structure
```
.

01_data_overview.ipynb
02_train_test_split.ipynb
03_exploratory_data_analysis.ipynb
04_relationships_and_multicolinearity.ipynb
05_feature_engineering.ipynb
06_data_preparation_pipeline.ipynb
07_modeling_*.ipynb
08_model_evaluation.ipynb
```

```
src/

utils/ # preprocessing + metrics
model_data_loader/ # model-specific data preparation
neural_networks.py # PyTorch models
```

```
data/
configs/ # transformation artifacts
processed/ # train/test datasets
```

```
models/
*.pkl # serialized model artifacts
```


---

## 🛠 Technologies Used

- **Python**
- **Polars** (high-performance data processing)
- **Scikit-learn**
- **XGBoost / LightGBM**
- **PyTorch**
- **Statsmodels**
- **JSON-based configuration pipelines**
- **Jupyter Notebooks**

---

## 💡 Key Insights

- Customers on **month-to-month contracts** have the highest churn risk  
- **Tenure** is one of the strongest predictors (longer tenure → lower churn)  
- Service combinations significantly influence churn behavior  
- Feature engineering contributes more to performance than model complexity  
- Threshold tuning is critical for aligning model outputs with business goals  

---

## 🔮 Future Work

Planned extensions include:

- Interactive app for:
  - real-time churn scoring
  - model retraining on new data
  - actionable customer insights  


---

## 👤 Author

**Matus Dzurilla**

---

## 📜 License

This project is intended for **educational and portfolio purposes**.

Dataset credit belongs to the original Kaggle dataset authors.