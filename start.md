# A Fine-Grained FAIRness Assessment Workflow for Genomic Data Sources

## Overview

This repository is part of the Master’s Thesis titled:

**A Fine-Grained FAIRness Assessment Workflow for Genomic Data Sources**
- **Author**: Ana Drmic
- **Student ID**: 10919624
- **Study Programme**: Computer Science and Engineering -- Ingegneria Informatica
- **Advisor**: Prof. Anna Bernasconi
- **Academic Year**: 2023-24

The project involves evaluating specific keywords against various genomic data repositories or the entire repositories to retrieve and assess relevant metadata using a FAIRness evaluation workflow. The system supports multiple repositories and uses different APIs to fetch data based on user input. The metadata is then evaluated using several custom metrics, and results are displayed in the `results` folder.

## Installation and Usage

To use this tool, please follow the steps below.

### 1. Installation

First, clone the repository, set up the environment, and install the dependencies:

1. **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Create a Virtual Environment:**
    It's recommended to create a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies:**
    Install the required libraries using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### 2. Running the Tool

You can evaluate the repositories by using the `evaluate.py` script or the Jupyter notebooks, depending on your preference.

#### **Using `evaluate.py` (Command-line Interface)**

To run the tool, use the `evaluate.py` script and follow the terminal instructions:

```bash
python evaluate.py
```

You will be prompted to select a repository and (in case of choosing the keyword-based approach) provide keywords for evaluating the metadata. Follow the on-screen instructions to complete the process.

### Using Jupyter Notebooks

If you prefer using Jupyter notebooks, you can run the `demo.ipynb` script instead. Modify the `keywords` and `repository_choice` variables inside the script to match your preferences, and then run it to evaluate the selected repository.

## Adding a New Repository

If you want to evaluate metadata from a new data repository, follow these steps:

- Check for API Documentation: Ensure that the repository has accessible API documentation. The API should provide a base endpoint and an endpoint to retrieve the metadata of the selected entity.
- Modify the `evaluate.py` Module: Add the new repository to the repositories dictionary.
- Define a New Metadata Fetching Function: In the `repositories.py` module, create a new function to fetch the metadata using the new repository's API endpoint.
- Define New Findability Fields: In the `Findability.py` module, modify the `get_findability_fields()` and `get_findability_fields_id()` functions. These should define the appropriate fields to indicate findability, even without a specified ID. If working with JSON data, use the `check_required_fields_json()` function from `utils.py`. For XML data, use `check_required_fields_geo()`. For other formats, define a custom function.
- Define New Interoperability Fields: In the `Interoperability.py` module, modify the `check_required_fields()` function to add the new fields that indicate interoperability (e.g., metadata references). Define a custom ontology check using `check_ontology()` based on the metadata's format. Use the appropriate field-checking function from `utils.py`.
- Define New Reusability Fields: In the `Reusability.py` module, modify the `R1()` and `R1_2()` functions to specify fields that suggest the data format or protocol and provenance data, respectively. Use `check_required_fields_json()` for JSON and `check_required_fields_geo()` for XML from `utils.py`, or define a new function for other formats.

