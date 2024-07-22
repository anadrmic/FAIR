# Project Technical Requirements

## Overview
This project involves evaluating specific keywords against various data repositories to retrieve and assess relevant metadata. The system supports multiple repositories and uses different APIs to fetch data based on user input. The metadata is then evaluated using several custom metrics, and the results are displayed in a tabular format.

## Technical Requirements

### Programming Language
- Python

### Libraries and Dependencies
The following Python libraries are required for the project:

requests
tabulate
pandas
xml.etree.ElementTree
bs4
re
json
ftplib

These dependencies can be quickly installed using the `requirements.txt` file.

### Installation
To set up the project environment, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. **Create a Virtual Environment:**
It's recommended to create a virtual environment to manage dependencies.

    ```bash 
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`

3. **Install Dependencies:**
Install the required libraries using the requirements.txt file.

    ```bash 
    pip install -r requirements.txt



# To start the FAIR Evaluator follow these steps:

## 1. KEYWORD APPROACH:
- open DemoKeywords.ipynb
- run the first two Python cells
- after running the second cell: type the number of the repository you want to evaluate, type in the keywords you want your samples to contain
- run the third cell: choose from the printed samples the one you want to evaluate
- run the fourth cell to print out the results of your evaluation

## 2. NO KEYWORD APPROACH:
- open Demo.ipynb
- run the first two Python cells
- after running the second cell: type the number of the repository you want to evaluate
- run the third cell
- run the fourth cell to print out the results of your evaluation


