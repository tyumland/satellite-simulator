# Polar Orbit & Coverage Simulation Tool

A dynamic, interactive simulation for visualizing satellite constellations in low-Earth orbit (LEO), built with Python and Streamlit. This tool models orbital paths, ground coverage zones, and pass frequency over U.S. military bases.

**Author:** Tyler Umland  
**Target Audience:** Recruiters | Graduate Admissions | Industrial, Manufacturing, & Defense Professionals

---

## Features

- Configure orbit altitude, inclination, and satellite count
- Visualize real-time polar orbits on a 3D Cesium globe
- Compute ground coverage zones for U.S. military bases
- Calculate pass count and longest gap per base
- Analyze redundancy index for orbital coverage
- Interactive filters for military branches and regions

---

## Try It Instantly

[Launch the app on Streamlit Cloud](#)  
(_Link will go here once deployed — next step!_)

---

## Project Structure
📁 satellite-simulator/
├── app.py # Main Streamlit app
├── us_bases_large.csv # Military base location data
└── README.md # This file

```markdown
## How to Run Locally

1. Clone the repository:

```bash
git clone https://github.com/tylerumland/satellite-simulator.git
cd satellite-simulator