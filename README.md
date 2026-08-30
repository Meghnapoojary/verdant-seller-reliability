# 🛡️ TrustMart — Seller Reliability & Review Integrity System

TrustMart helps online shoppers compare sellers before buying by combining seller ratings, return rates, complaint history, price signals, listing history, explainable trust scoring, and an **AI-assisted review integrity signal**.

## What makes it different
- Seller Trust Score built from multiple behavioral signals
- Risk classification: Low / Medium / High
- Explainable score breakdown
- Seller comparison across the same product
- Price-vs-trust comparison
- Seller profile and history view
- Complaint workflow
- Shopping cart trust warnings
- **AI Review Trust Check**: analyzes a supplied set of reviews for suspicious repetition, generic language, sentiment uniformity, rating/text mismatch and other manipulation signals

> The AI Review Trust Check is a heuristic. It does **not** prove that a review is genuine or fake.

## Stack
Frontend: HTML5, CSS3, JavaScript, Chart.js
Backend: Python, Flask, Flask-CORS, Google Gemini API
Database: MySQL

## Local setup
1. Create the MySQL database by running `backend/schema.sql`.
2. Copy `backend/.env.example` to `backend/.env` and fill in your database credentials and Gemini API key.
3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```
4. Start the API:
```bash
python app.py
```
5. Serve the frontend with VS Code Live Server or:
```bash
cd frontend
python -m http.server 8080
```

## API
- GET `/products`
- GET `/product/<id>`
- GET `/trust-data/<product_id>`
- GET `/sellers`
- POST `/place-order`
- POST `/file-complaint`
- POST `/review-trust-analysis`

## AI review analysis input
The review endpoint accepts a product/seller context, an overall rating, a review count and a block of review text. The model returns a low/medium/high authenticity risk, confidence, consistency commentary, signals, positive signals, summary and recommendation.

## Deployment
The included `render.yaml` prepares the Flask backend for Render. Render supports Flask web services with `pip install -r requirements.txt` and `gunicorn app:app`. A hosted MySQL database is still required; local MySQL cannot be used by a public Render deployment.

## Security
Never commit `.env` or database credentials. Use environment variables in production. If credentials were ever committed to Git, rotate them before making the repository public.
