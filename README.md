# V2V-TPSM Project — Traffic Stability Analysis with Look-Ahead Range (LAR)

A research project simulating and statistically analysing the impact of Look-Ahead Range (LAR) on traffic flow stability by comparing human-driven and autonomous (CAV) vehicle platoons using V2V (Vehicle-to-Vehicle) communication.

---

## 📁 Project Structure

```
V2V-TPSM_Project/
├── cav-v2v-lookahead-research/        # Python simulation (Pygame)
│   ├── run_simulation.py              # Entry point — run this to start
│   ├── scenario.py                    # Platoon setup (cars, speed, spacing)
│   ├── config.py                      # Display settings (window, colors, FPS)
│   ├── requirements.txt               # Python dependencies
│   └── simulation/
│       ├── visualizer.py              # Pygame rendering + simulation loop
│       ├── context.py                 # Simulation state (road, lanes)
│       └── cars/
│           ├── car.py                 # Base Car class (physics + car-following)
│           ├── human_car.py           # Human driver model (reaction delay ~0.45s)
│           └── autonomous_car.py      # CAV model (instant response, V2V lookahead)
└── data/
    ├── scenario_1_results.csv         # Simulation output data (7 scenarios)
    ├── scenario_2_results.csv
    ├── ...
    ├── scenario_7_results.csv
    └── analytics/
        ├── final_research.R           # Final R analysis script
        ├── full_analysis.R            # Full statistical analysis
        ├── plot_results_explanation.md
        ├── r_script_explanation.md
        └── viva_questions_and_justification.md.resolved
```

---

## 🔬 Research Overview

This project investigates how increasing Look-Ahead Range (LAR) in Connected Autonomous Vehicles (CAVs) affects platoon safety and traffic efficiency compared to human-driven vehicles.

Two platoons of 8 cars are simulated side-by-side on a 2-lane road:

| Platoon | Lane | Colour | Behaviour |
|---------|------|--------|-----------|
| Human | 0 | Light red | Reacts to lead car with ~0.45s reaction delay |
| Autonomous (CAV) | 1 | Light blue | Reacts instantly using V2V data and lookahead |

The lead car of each platoon decelerates sharply then re-accelerates — allowing observation of how the braking wave propagates through each platoon.

The analysis focuses on three key metrics:

| Metric | Description |
|--------|-------------|
| `Peak_Speed_Variance` | How much speed fluctuates across the platoon |
| `Amplification_Factor` | How much the braking wave grows as it travels rearward |
| `Settling_Time_sec` | How long the platoon takes to return to stable speed |

---

## 🖥️ Part 1 — Pygame Simulation

### Prerequisites

- Python 3.11+
- pip

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Lumini003/v2v-lookahead-project.git
cd V2V-TPSM_Project
```

**2. Navigate to the simulation folder**

```bash
cd cav-v2v-lookahead-research
```

**3. Create and activate a virtual environment**

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Run the simulation**

```bash
python run_simulation.py
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `SPACE` | Start / Pause / Resume |
| `R` | Restart simulation |
| `ESC` | Quit |

### Configuration

Edit `scenario.py` to change the road and cars; edit `config.py` for display and scale.

```python
# scenario.py
NUM_CARS = 8           # Cars per platoon
SPACING = 28           # Initial gap between cars (units)
DECEL_DURATION = 3.0   # Lead car braking duration (seconds)
ACCEL_DURATION = 3.0   # Lead car re-acceleration duration (seconds)

# config.py
PIXELS_PER_UNIT = 2.0  # Zoom level
WINDOW_WIDTH = 1400    # Window width in pixels
FPS = 60               # Frames per second
```

---

## 📊 Part 2 — Statistical Analysis (R)

### What the Analysis Covers

- Descriptive statistics per lane type and LAR level
- Visualisations — boxplots, histograms, trend plots
- Statistical hypothesis testing (Welch t-test, ANOVA, Kruskal-Wallis)
- Regression modelling (LAR vs stability metrics)
- Correlation analysis
- Diminishing returns evaluation

### Dataset

The R scripts automatically load all CSV files from `data/` matching `scenario_*_results.csv`. Each file represents one simulation scenario with a different LAR configuration.

Key columns used:

| Column | Description |
|--------|-------------|
| `Lane_Type` | Human or Automated (with LAR level) |
| `Peak_Speed_Variance` | Speed fluctuation across the platoon |
| `Amplification_Factor` | Braking wave growth factor |
| `Settling_Time_sec` | Time to return to stable speed (seconds) |

### Prerequisites

- R 4.0+
- RStudio (recommended)

### Install Required R Packages

```r
install.packages(c("rstatix", "car", "ggplot2", "plotly"))
```

### Run the Analysis

```r
# Run the final research analysis
source("data/analytics/final_research.R")

# Or run the full analysis
source("data/analytics/full_analysis.R")
```

---

## 🧪 Key Findings

- CAV platoons show significantly reduced braking wave amplification compared to human-driven platoons.
- Human platoons exhibit the classic accordion effect — braking disturbance grows as it propagates rearward.
- Increasing LAR improves stability up to a point, after which diminishing returns are observed.
- V2V lookahead allows CAVs to respond to lead car deceleration before it physically reaches them, reducing collision risk and improving throughput.

---

## 📦 Dependencies

**Python (simulation)**

| Package | Version |
|---------|---------|
| pygame | ≥ 2.5.0 |

**R (analysis)**

| Package | Purpose |
|---------|---------|
| ggplot2 | Visualisation |
| plotly | Interactive plots |
| rstatix | Statistical tests |
| car | Regression diagnostics |

---

## 📄 License

This project was developed as part of a Transport and Policy Systems Modelling (TPSM) research module.
