# A Conceptual Workflow for Fine-Grained FAIR Assessment of Genomic Repositories

In this repository we maintain a Python-based framework for automatically assessing the compliance of genomic repositories 
with the **FAIR principles** (Findability, Accessibility, Interoperability, and Reusability).

Unlike existing FAIR assessment tools that typically evaluate entire datasets or repositories, this workflow performs **fine-grained FAIR assessment at the level 
of individual digital objects** (e.g., studies, series, biosamples, experiments, and files). 
The framework translates FAIR principles into measurable _metrics_ and executable _practical tests_ that can be applied across 
heterogeneous genomic repositories.

## Supported repositories

The current implementation supports the following repositories:

- ArrayExpress / BioStudies
- Gene Expression Omnibus (GEO)
- GWAS Catalog
- ENCODE (both Biosamples and Experiments)
- Genomic Data Commons (GDC)

---

# Features

- Automated FAIR assessment
- Fine-grained evaluation of individual digital objects
- Repository-specific metadata extraction
- Keyword-based assessment
- Whole-repository assessment
- Detailed reports for each FAIR principle
- Comparative FAIR scores across repositories

---

# Repository structure

```
FAIR/
│
├── fair_metrics/          # FAIR assessment modules
├── metadata/              # Retrieved metadata
├── results/               # Generated assessment reports
│
├── assess.py              # FAIR assessment engine
├── evaluate.py            # Main entry point
├── repositories.py        # Repository-specific functions
├── utils.py               # Utility functions
├── demo.ipynb             # Example notebook
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/anadrmic/FAIR.git
cd FAIR
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install the dependencies

```bash
pip install -r requirements.txt
```

---

# Usage

Run the assessment tool

```bash
python evaluate.py
```

The program interactively asks the user to:

1. Select a genomic repository
2. Choose the assessment mode
3. (Optionally) provide keywords
4. Execute the FAIR assessment

---

## Assessment modes

### Keyword-based assessment

Evaluates only digital objects matching user-provided keywords.

This mode is useful for evaluating FAIRness of domain-specific collections.

Example:

```
Repository:
ArrayExpress

Keywords:
Parkinson
Homo sapiens
```

---

### Whole-repository assessment

Evaluates all available digital objects retrieved from the selected repository.

This mode provides an overall FAIR profile of the repository.

---

# Output

The assessment generates:

- Overall FAIR scores
- Metric-level scores
- Principle-level reports
- Detailed explanations of each practical test

Results are stored in the `results/` directory.

Typical outputs include

```
scores.txt
Findability.txt
Accessibility.txt
Interoperability.txt
Reusability.txt
fair_principles_scores.png
```

---

# Assessment methodology

The workflow follows a three-level assessment:

```
FAIR Principle
        ↓
Metric
        ↓
Practical Test
```

Each practical test evaluates one aspect of FAIR compliance and produces a normalized score.

Metric scores are aggregated into FAIR principle scores to produce the final assessment.

---

# Publications

If you use this software in your research, please cite:

> Anna Bernasconi, Ana Drmic
> *A Conceptual Workflow for Fine-Grained FAIR Assessment of Genomic Repositories.*
> (under submission)

---

# License

This repository is intended for research and educational purposes.

Please check the repository license before redistribution or commercial use.

---

# Contact

Anna Bernasconi

https://annabernasconi.faculty.polimi.it/

anna.bernasconi@polimi.it
