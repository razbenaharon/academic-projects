# MatchPoint ⚽✈️🏠

### European Football Tourism Recommendation Engine

**Data Collection & Management Lab (00940290) – Final Project**

---

## 🎯 Project Overview

### Motivation

Sports tourism is growing rapidly, with fans traveling internationally to attend major football matches. Unlike general leisure travel, football tourists mainly care about stadium proximity and game-day convenience, while still balancing price and accommodation quality. Current platforms (Airbnb / Booking.com) are not optimized for this scenario, forcing users to manually compare many options across multiple criteria.

### Objectives

- **Enhanced User Experience:** Users receive targeted recommendations aligned with their primary travel purpose, eliminating the need for manual cross-platform comparisons.
- **LLM-Powered Stadium Context:** Large Language Models enrich the recommendations by providing relevant stadium-area insights (food & drinks, directions, ticket info), improving planning efficiency and overall trip convenience.
- **Strategic Value:** The project demonstrates how domain-specific recommendation systems can enhance platform usability for niche audiences.

---

## 💻 Setup & Execution Guide

This guide provides step-by-step instructions to configure, build, and run the project from scratch. Follow the steps in the exact order presented.

### 1. Environment Configuration

Before running any notebooks, configure the following credentials using Databricks Secrets or environment variables:

```ini
# Bright Data Proxy Credentials (for scraping)
BRIGHTDATA_USER=your_username
BRIGHTDATA_PASSWORD=your_password

# Azure Blob Storage SAS Tokens (for data loading)
SAS_SUBMISSIONS="your_sas_token_for_submissions"
SAS_AIRBNB="your_sas_token_for_airbnb_data"
```

### 2. Execution Pipeline

Run the notebooks in the following strict sequential order. Each step generates artifacts required by the next.

#### ▶️ Step 1: Data Scraping

**Notebook:** `scraping.ipynb`

| | |
|---|---|
| **Action** | Connects to Wikipedia via Bright Data proxies to scrape match schedules, stadium information, and geographic coordinates for all 16 European leagues. Implements rate limiting and error handling for robust data collection. |
| **Output** | `/dbfs/FileStore/Stadium_LLM_Enrichment.csv`<br>`/dbfs/FileStore/Match_Schedule_All_Leagues.csv` |

#### ▶️ Step 2: LLM Enrichment

**Notebook:** `llm_enrichment.ipynb`

| | |
|---|---|
| **Input** | `/dbfs/FileStore/Stadium_LLM_Enrichment.csv` (from Step 1) |
| **Action** | Uses LangChain with Llama 3.3 70B via Databricks serving endpoints to generate rich stadium guides. For each stadium, the LLM produces three categories of insights: Food & Drinks, How to Get There, and Ticket Information. |
| **Output** | `/dbfs/FileStore/stadium_guides.json` |

#### ▶️ Step 3: Main Application

**Notebook:** `Final Project - MatchPoint.ipynb`

| | |
|---|---|
| **Inputs** | `Match_Schedule_All_Leagues.csv` (from Step 1)<br>`stadium_guides.json` (from Step 2)<br>Airbnb Dataset (loaded from Azure via `SAS_AIRBNB`) |
| **Action** | Executes the full recommendation pipeline:<br>1. Loads and joins all data sources<br>2. Calculates distances between accommodations and stadiums<br>3. Applies the 50km proximity filter<br>4. Computes VFM scores (quality, price, amenities, flexibility)<br>5. Generates final weighted scores (60% proximity + 40% VFM)<br>6. Ranks and selects top 10 recommendations per match<br>7. Builds interactive HTML application with Leaflet maps |
| **Output** | `MatchPoint_App.html` — Standalone interactive web application |

### 3. Running the Application

After completing all steps, download `MatchPoint_App.html` from DBFS and open it in any modern web browser. The application runs entirely client-side with no additional dependencies.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Core Logic** | Python, PySpark, Pandas |
| **Infrastructure** | Databricks (Compute & Serving Endpoints) |
| **AI & ML** | Llama 3.3 70B, Custom Weighted Ranking |
| **Data Acquisition** | BeautifulSoup, Bright Data Proxies |
| **Frontend** | HTML5, JavaScript, Leaflet Maps |

---

## 📁 Project Structure

```
MatchPoint/
├── scraping.ipynb                    # Step 1: Web scraping notebook
├── llm_enrichment.ipynb              # Step 2: LLM stadium guides generation
├── Final Project - MatchPoint.ipynb  # Step 3: Main application notebook
└── README.md                         # This file
```
