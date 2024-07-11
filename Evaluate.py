import requests
import xml.etree.ElementTree as ET
from tabulate import tabulate
import Utils
import F
import A
import I
import R

repository_choice = ""
repository_name = ""
keywords = []

def main_1():
    global repository_choice, repository_name
    
    print("Which data repository do you want to use?")
    print("1. ArrayExpress")
    print("2. Gene Expression Omnibus")
    print("3. GWAS Catalog")
    print("4. ENCODE")
    print("5. GENOMIC DATA COMMONS")
    print("6. ICGC")

    repository_choice = input("Enter the number corresponding to your choice: ")
    while repository_choice not in ['1', '2', '3', '4', '5', '6']:
        print("Invalid choice. Please enter either 1, 2, 3, 4, 5 or 6.")
        repository_choice = input("Enter the number corresponding to your choice: ")
    repository_names = {
        '1': "ArrayExpress",
        '2': "Gene Expression Omnibus",
        '3': "GWAS Catalog",
        '4': "ENCODE",
        '5': "GENOMIC DATA COMMONS",
        '6': "ICGC"
    }
    repository_name = repository_names[repository_choice]
    limit = int(input("Enter the number of samples you want to assess: "))
    return repository_name, limit

def assess(metadata, keywords, repository_choice, url, request_status):
    data = [
        ["F1 score", F.F1(url)],
        ["F2 score", F.F2(keywords, metadata, repository_choice)],
        ["F3 score", F.F3(metadata, repository_choice)],
        ["F4 score", F.F4(metadata, repository_choice)],
        ["A1 score", A.A1(request_status)],
        ["A1.1 score", A.A1_1(request_status)],
        ["A1.2 score", A.A1_2(request_status)],
        ["A2 score", A.A2(repository_choice)],
        ["I1 score", I.I1(metadata)],
        ["I2 score", I.I2(metadata, repository_choice)],
        ["I3 score", I.I3(metadata)],
        ["R1 score", R.R1(metadata, repository_choice)],
        ["R1.1 score", R.R1_1(metadata, repository_choice)],
        ["R1.2 score", R.R1_2(metadata, repository_choice)],
        ["R1.3 score", R.R1_3(metadata, repository_choice)]
    ]
    print(tabulate(data, headers=["Metric", "Score"], tablefmt="fancy_grid"))
    return [row[1] for row in data]

def initialize(repository_name, limit):
    request_status = ""
    response_data = ""
    
    if repository_name == "ArrayExpress":
        repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
        url = "https://www.re3data.org/repository/r3d100010222"  
        experiment_ids = []
        for page in range(limit):
            r_repo = requests.get(repository_api,
                            params={
                                    "study_type": "transcription profiling by array",
                                    "pageSize" : 100,
                                    "page": page
                                    })
            request_status = r_repo.status_code
            response_data = r_repo.json()
            hits = response_data.get("hits", [])
            for hit in hits:
                accession = hit.get("accession", "")
                if len(accession) == 11:
                    experiment_ids.append(accession)
        print("Experiment IDs:", experiment_ids[0:limit])
        response_data_list = []
        for hit in experiment_ids[0:limit]:
            study_accession = hit
            url_1 = Utils.get_json_metadata_link(study_accession)
            r_repo = requests.get(url_1)
            request_status = (r_repo.status_code)
            response_data = r_repo.json()
            response_data_list.append(response_data)
        response_data = response_data_list

    if repository_name == "Gene Expression Omnibus":
        repository_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        metadata_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
        url = "https://www.re3data.org/repository/r3d100010283"  
        repository_acronym = "gds" 
        r_repo = requests.get(repository_api,
                        params={"db"   : repository_acronym })
        request_status = (r_repo.status_code)
        root = ET.fromstring(r_repo.text)
        for field in root.iter('Id'):
            id = field.text
        r_meta = requests.get(metadata_api,
                        params={"db" : repository_acronym,
                                "id" : id})
        root_meta = ET.fromstring(r_meta.text)
        response_data = root_meta[0]

    if repository_name == "GWAS Catalog":
        url = "https://www.re3data.org/repository/r3d100014209"
        base_url = "https://www.ebi.ac.uk/gwas/rest/api/studies?page=1&size=500"
        r_repo = requests.get(base_url)
        response_data = r_repo.json()
        request_status = (r_repo.status_code)
        hits = []
        for accession in response_data["_embedded"]["studies"]:
            hits.append(accession["accessionId"])
        print("Experiment IDs:", hits[0:limit])
        response_data_list = []
        for i in range(limit):
            study_accession = hits[i]
            accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
            r_repo = requests.get(accession_url)
            response_data = r_repo.json()
            response_data_list.append(response_data)
        response_data = response_data_list

    if repository_name == "ENCODE":
        url = "https://www.re3data.org/repository/r3d100013051"
        base_url = f'https://www.encodeproject.org/search/?type=Biosample&limit=all&format=json'
        headers = {'accept': 'application/json'}
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
        request_status = (response.status_code)
        hits = []
        for accession in response_data["@graph"]:
            try:
                hits.append(accession["accession"])
            except:
                continue
        print("Experiment IDs:", hits[0:limit])
        response_data_list = []
        for i in range(limit):   
            study_accession = hits[i]
            accession_url = f'https://www.encodeproject.org/biosample/{study_accession}/?frame=object'
            response = requests.get(accession_url, headers=headers)
            response_data = response.json()
            response_data_list.append(response_data)
        response_data = response_data_list

    if repository_name == "GENOMIC DATA COMMONS":
        url = "https://www.re3data.org/repository/r3d100012061"
        base_url = f'https://api.gdc.cancer.gov/files'
        params = {
            'from': '0',
            'size': str(limit),
            'sort': 'file_size:asc',
            'pretty': 'true'
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            response_data = response.json()
        request_status = (response.status_code)
        hits = []
        for accession in response_data["data"]["hits"]:
            try:
                hits.append(accession["id"])
            except:
                continue
        print("Experiment IDs:", hits[0:limit])

        params = {
            'pretty': 'true'
        }
        response_data_list = []
        for i in range(limit):    
            study_accession = hits[i]
            accession_url = f'https://api.gdc.cancer.gov/files/{study_accession}'
            response = requests.get(accession_url, params=params)
            response_data = response.json()
            response_data_list.append(response_data)
        response_data = response_data_list
    
    if repository_name == "ICGC":
        url = ""
        base_url = f'https://dcc.icgc.org/api/v1/projects?filters=%7B%7D&from=1&size=100&order=desc'    
        response = requests.get(base_url)
        if response.status_code == 200:
            response_data = response.json()
        request_status = (response.status_code)
        hits = []
        for hit in response_data["hits"]:
            try:
                hits.append(hit["id"])
            except:
                continue
        print("Experiment IDs:", hits[0:limit])
        response_data_list = []
        for i in range(limit):    
            project = hits[i]
            accession_url = f'https://dcc.icgc.org/api/v1/projects/{project}'
            response = requests.get(accession_url)
            response_data = response.json()
            response_data_list.append(response_data)
        response_data = response_data_list
    metadata = response_data
    return metadata, repository_choice, url, request_status
