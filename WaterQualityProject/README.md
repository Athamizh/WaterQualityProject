Water Quality Monitoring & Pollution Detection (Brisbane Dataset)
Project Title

Water Quality Monitoring & Pollution Detection Using Risk-Based Analysis

Student Names and Emails

Varun Baru
Email: vbaru@stevens.edu

Anandhageethan Thamizharasan
Athamizh@stevens.edu

(This project was completed as a team project. Both team members contributed equally.)

Problem Description

Water quality monitoring is a fundamental problem in environmental science and engineering, as poor water quality can pose serious risks to ecosystems and public health. The objective of this project is to design and implement a Python-based system that analyzes real-world water quality sensor data and determines whether individual water samples should be classified as Safe or Unsafe.

The program uses publicly available water quality measurements collected from Brisbane waterways. These measurements include physical and chemical indicators such as pH, turbidity, dissolved oxygen, temperature, salinity, and chlorophyll. The system validates the input data, handles missing or low-quality records, computes a risk score for each sample using a transparent, rule-based model, and classifies the sample accordingly. The emphasis of the solution is on interpretability, modular design, and reproducibility rather than black-box prediction.

Program Structure and How to Use the Program
Program Structure

The repository is organized as follows:

WaterQualityProject/
│
├── data/
│   └── brisbane_water_quality.csv
│
├── notebooks/
│   └── Run_Project.ipynb        # Main executable Jupyter notebook
│
├── src/
│   ├── loader.py                # Data loading and validation
│   ├── samples.py               # WaterSample class definition
│   ├── model.py                 # Risk scoring and classification
│   ├── analysis.py              # Analysis utilities and generators
│   └── exceptions.py            # Custom exception handling
│
├── tests/
│   ├── test_loader.py           # Unit tests for data loading
│   └── test_model.py            # Unit tests for model behavior
│
├── README.md
├── requirements.txt
└── pytest.ini

How to Use the Program

Clone the public GitHub repository and navigate to the project directory.

Create and activate a Python virtual environment using Python 3.12 or 3.13.

Install required dependencies listed in requirements.txt.

Open the project folder in Visual Studio Code.

Open the notebook notebooks/Run_Project.ipynb.

Select the virtual environment as the Jupyter kernel.

Click Run All to execute the entire program.

### Quick Start (Command Line)

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python -m pytest -q

When executed, the notebook automatically:

generates the required Python modules,

runs unit tests using Pytest,

loads and validates the dataset,

computes risk scores,

classifies samples as Safe or Unsafe,

saves results to an output CSV file, and

displays visualizations and summary statistics.

Main Contributions of Each Teammate
Varun Baru

Designed the overall project architecture and modular structure

Implemented data loading, preprocessing, and validation logic

Developed the risk scoring and Safe/Unsafe classification model

Implemented model calibration to ensure meaningful classification results

Created data visualizations and output reporting

Integrated all components into a single executable Jupyter notebook

Anandhageethan Thamizharasan

Implemented automated unit tests using Pytest

Assisted with data analysis and threshold selection

Contributed to debugging and validation

Assisted with documentation and GitHub repository management

## Limitations
- Rule-based scoring is interpretable but not a machine learning model.
- Thresholds are dataset-dependent; calibration helps but may vary by location.
- Quality flags may differ across datasets; column_map may need adjustments.
