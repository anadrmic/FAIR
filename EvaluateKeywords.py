import requests
import xml.etree.ElementTree as ET
from tabulate import tabulate
from fair_metrics import Accessibility, Findability, Interoperability, Reusability

repository_choice = ""
repository_name = ""
keywords = []

def main():
    """
    Prompt the user to select a data repository and enter keywords for the search.

    Returns:
        tuple: The chosen repository name and the list of keywords.
    """
    global repository_choice, repository_name, keywords
    
    print("Which data repository do you want to use?")
    print("1. ArrayExpress")
    print("2. Gene Expression Omnibus")
    print("3. GWAS Catalog")
    print("4. ENCODE")
    print("5. GENOMIC DATA COMMONS")

    repository_choice = input("Enter the number corresponding to your choice: ")

    while repository_choice not in ['1', '2', '3', '4', '5']:
        print("Invalid choice. Please enter either 1, 2, 3, 4 or 5.")
        repository_choice = input("Enter the number corresponding to your choice: ")
    if repository_choice == '1':
        repository_name = "ArrayExpress"
    if repository_choice == '2':
        repository_name = "Gene Expression Omnibus"
    if repository_choice == '3':
        repository_name = "GWAS Catalog"
    if repository_choice == '4':
        repository_name = "ENCODE"
    if repository_choice == '5':
        repository_name = "GENOMIC DATA COMMONS"

    print("\nEnter specific keywords for your search (one per entry). Enter 'done' when finished:")
    while True:
        keyword = input("Enter a keyword (or 'done' to finish): ")
        if keyword.lower() == 'done':
            break
        keywords.append(keyword)
    print("\nRepository choice:", repository_name)
    print("Keywords for search:", keywords)    
    return repository_name, keywords

def initialize(repository_name, keywords):
    """
    Initialize the search by retrieving metadata from the chosen repository using the provided keywords.

    Args:
        repository_name (str): The name of the chosen repository.
        keywords (list): The list of keywords for the search.

    Returns:
        tuple: Metadata, repository choice, repository URL, and request status.
    """
    request_status = ""
    response_data = ""

    if repository_name == "ArrayExpress":
        repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
        dataset_download = "https://ftp.ebi.ac.uk/biostudies/fire/"
        url = "https://www.re3data.org/repository/r3d100010222"  
        r_repo = requests.get(repository_api,
                        params={
                                "study_type": "transcription profiling by array",
                                "pageSize" : 100,
                                "query"      :  keywords[0], 
                                "study_type":  keywords[1],
                                "organism"      :  keywords[2] 
                                })
        request_status = r_repo.status_code
        response_data = r_repo.json()
        hits = response_data.get("hits", [])
        experiment_ids = []
        for hit in hits:
            accession = hit.get("accession", "")
            experiment_ids.append(accession)
        print("Experiment IDs:", experiment_ids)
        response_data_list = []
        for hit in experiment_ids:
            study_accession = hit
            url_1 = Utils.get_json_metadata_link(study_accession)
            print(url_1)
            r_repo = requests.get(url_1)
            request_status = r_repo.status_code
            print(request_status)
            response_data = r_repo.json()
            response_data_list.append(response_data)
        response_data = response_data_list

    if repository_name == "Gene Expression Omnibus":
        repository_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        metadata_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
        url = "https://www.re3data.org/repository/r3d100010283"  
        repository_acronym = "gds"
        query_string = keywords[0] +  " AND " + keywords[1] + " AND " + keywords[2]
        r_repo = requests.get(repository_api,
                        params={"db"   : repository_acronym,
                                "term" : query_string
                                })
        request_status = r_repo.status_code
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
        request_status = r_repo.status_code
        hits = []
        for accession in response_data["_embedded"]["studies"]:
            disease = accession["diseaseTrait"]["trait"]
            if disease == keywords[0]:
                hits.append(accession["accessionId"])
        print("Experiment IDs:", hits)
        study_accession = input("Enter a study accession you want to access (one of the provided ids): ")
        accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
        r_repo = requests.get(accession_url)
        response_data = r_repo.json()
        response_data_list = []
        for hit in hits:
            study_accession = hit
            accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
            print(accession_url)
            r_repo = requests.get(accession_url)
            response_data = r_repo.json()
            response_data_list.append(response_data)
        response_data = response_data_list

    if repository_name == "ENCODE":
        url = "https://www.re3data.org/repository/r3d100013051"
        search_query = "+".join(keywords)
        base_url = f'https://www.encodeproject.org/search/?searchTerm={search_query}&frame=object'
        base_url = f'https://www.encodeproject.org/search/?type=Biosample&limit=all&format=json'
        headers = {'accept': 'application/json'}
        response = requests.get(base_url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
        request_status = response.status_code
        hits = []
        for accession in response_data["@graph"]:
            try:
                hits.append(accession["accession"])
            except:
                continue
        print("Experiment IDs:", hits)
        study_accession = input("Enter a study accession you want to access (one of the provided ids): ")
        response_data_list = []
        for hit in hits:
            study_accession = hit
        for i in range(100):    
            study_accession = hits[i]
            accession_url = f'https://www.encodeproject.org/biosample/{study_accession}/?frame=object'
            print(accession_url)
            response = requests.get(accession_url, headers=headers)
            response_data = response.json()
            response_data_list.append(response_data)
        response_data = response_data_list

    if repository_name == "GENOMIC DATA COMMONS":
        url = "https://www.re3data.org/repository/r3d100012061"
        search_query = "+".join("")
        base_url = f'https://api.gdc.cancer.gov/files'
        params = {
            'from': '0',
            'size': '200', 
            'sort': 'file_size:asc',
            'pretty': 'true'
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            response_data = response.json()
        request_status = response.status_code
        hits = []
        for accession in response_data["data"]["hits"]:
            try:
                hits.append(accession["id"])
            except:
                continue
        print("Experiment IDs:", hits)
        params = {
            'pretty': 'true'
        }
        response_data_list = []
        for i in range(100):    
            study_accession = hits[i]
            accession_url = f'https://api.gdc.cancer.gov/files/{study_accession}'
            response = requests.get(accession_url, params=params)
            response_data = response.json()
            response_data_list.append(response_data)
        response_data = response_data_list
    metadata = response_data

    if repository_name == "ICGC":
        url = ""
        base_url = f'https://dcc.icgc.org/api/v1/projects?filters=%7B%7D&from=1&size=100&order=desc'    
        response = requests.get(base_url)
        if response.status_code == 200:
            response_data = response.json()
        request_status = response.status_code
        hits = []
        for hit in response_data["hits"]:
            try:
                hits.append(hit["id"])
            except:
                continue
        print("Experiment IDs:", hits)
        response_data_list = []
        for i in range(len(hits)):    
            project = hits[i]
            accession_url = f'https://dcc.icgc.org/api/v1/projects/{project}'
            response = requests.get(accession_url)
            response_data = response.json()
            response_data_list.append(response_data)
        response_data = response_data_list
    metadata = response_data
    return metadata, repository_choice, url, request_status

def assess(metadata, keywords, repository_choice, url, request_status):
    """
    Assess the retrieved metadata using various scoring functions.

    Args:
        metadata (dict): The metadata retrieved from the repository.
        keywords (list): The list of keywords for the search.
        repository_choice (str): The chosen repository.
        url (str): The URL of the repository.
        request_status (int): The status code of the request.

    Returns:
        list: A list of scores for various metrics.
    """
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
