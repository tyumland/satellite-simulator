# Satellite Constellation Simulator  
**Built by Tyler Umland**

A web-based tool for visualizing and analyzing polar-orbiting satellite constellations over U.S. military bases. Designed with accessibility and performance in mind — no installation required.

### Live Demo  
Launch the app here:  
[tylerumland-satellite-simulator.streamlit.app](https://tylerumland-satellite-simulator.streamlit.app)

---

## Overview

This simulator models satellites in Low Earth Orbit (LEO) and evaluates their visibility over military bases. It is designed for:

- **Mission planning** (e.g., communications, imaging, or weather observation)
- **Base coverage analysis** (pass counts and coverage gaps)
- **Educational or professional demonstration** of orbital mechanics

---

## Features

- Customize altitude, inclination, and number of satellites
- Visualize orbits and coverage areas on an interactive 3D globe (Cesium.js)
- Filter and analyze U.S. military bases by branch or region
- Displays analytics like:
  - Pass counts per base
  - Longest gap in coverage
  - Redundancy index

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app |
| `us_bases_large.csv` | Dataset of U.S. military base coordinates |
| `requirements.txt` | Minimal dependencies for deployment |

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py