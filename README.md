# Corporate Credit Rating System (CCRS) Simulator

A Python-based corporate credit rating simulator built on banking industry standards, calculating Probability of Default (PD) and assigning credit ratings based on quantitative and qualitative financial analysis.

## Live Demo
[🚀 Launch App](여기에 Streamlit 링크 붙여넣기)

## Features
- **Quantitative Scoring (60%)** — 7 financial indicators including debt ratio, EBITDA, and liquidity
- **Qualitative Scoring (40%)** — CEO experience, technology grade (TCB), and industry risk (IRR)
- **Knockout Rules** — Automatic flags for capital erosion and qualified audit opinions
- **Notching Rules** — Grade adjustment based on conditional factors
- **Stress Test** — Macroeconomic shock scenario simulation
- **PD Calculation** — Probability of Default via logistic regression model
- **100 Sample Companies** — Pre-loaded dataset across 6 rating tiers (AA to CCC/D/Reject)

## Tech Stack
- Python
- Streamlit
- Pandas

## How to Run Locally
```bash
pip install streamlit pandas
streamlit run app.py
```

## Project Structure
```
├── app.py                  # Main application
├── ccrs_sample_data.csv    # 100 sample company dataset
├── requirements.txt        # Dependencies
└── README.md
```
