# AegisQ

AegisQ is a Post-Quantum Safe Privileged Access Management (PAM) and Insider Threat Detection prototype built for the FinSpark'26 cybersecurity hackathon.

## Overview

AegisQ combines:
- a dark-themed Streamlit dashboard for privileged access monitoring,
- a simulated post-quantum key exchange flow inspired by ML-KEM / Kyber-style concepts,
- an Isolation Forest-based anomaly engine to highlight suspicious privileged-user behavior.

## Features

- Real-time simulated admin action logs
- Threat risk scoring for each action
- Sidebar controls to simulate normal or malicious insider activity
- Quantum-style key exchange visualization
- Local SQLite storage for telemetry simulation

## Tech Stack

- Python
- Streamlit
- Pandas
- scikit-learn
- PyCryptodome
- SQLite

## Project Structure

- `app.py` — main Streamlit dashboard and application logic
- `aegis_quantum_core.py` — supporting prototype logic
- `aegisq.db` — local SQLite database for simulated telemetry

## Installation

Make sure Python 3.10+ is installed.

Install the required dependencies:

```bash
pip install streamlit pandas scikit-learn pycryptodome
```

## Run the App

From the project directory, run:

```bash
streamlit run app.py
```

Or, if you prefer the explicit Python launcher:

```bash
python -m streamlit run app.py
```

## Demo

The app runs locally on:

```text
http://localhost:8501/
```

## GitHub

Repository: https://github.com/Anushkaa-tech/AegisQ

## License

This project is for hackathon and educational demonstration purposes.
