# IPO Risk Score

A logistic-bounded risk scoring framework for Initial Public Offerings (IPOs).

This project implements a simple yet extensible model that maps multi-dimensional IPO characteristics into a **bounded risk score between 0 and 100**.
A score of `0` denotes the lowest ex-ante risk, while `100` represents the highest.
The framework is designed for researchers, analysts, and practitioners who need a transparent and modular way to quantify IPO risk before trading.

---

## 🌐 Overview

The IPO Risk Score normalizes key deal characteristics into features in the `[0, 1]` range, combines them linearly, and applies a logistic transformation.

High-risk factors (e.g., micro-float, weak underwriters, overpriced valuation) push the score up.
Low-risk factors push it down.

The model emphasizes:

- **Modularity**: clear separation between domain entities, feature engineering, scoring engine, and logistic model.
- **Interpretability**: all features are normalized and visible in the output.
- **Extensibility**: easy to add new features, change weights, or plug new versions of the model.

---

## ⚡ Quick Start

### Install

```bash
git clone https://github.com/Diesan-Romero-LLC/ipo_risk_score.git
cd ipo_risk_score
pip install -e ".[dev]"
