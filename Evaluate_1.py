import requests
import xml.etree.ElementTree as ET
from tabulate import tabulate
from fair_metrics import Accessibility as A, Findability as F, Interoperability as I, Reusability as R
import utils


repository_choice = ""
repository_name = ""
keywords = []

def initialize():

    """
    Prompt the user to select a data repository and specify the number of samples to assess.

    Returns:
        tuple: The chosen repository name and the number of samples to assess.
    """

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

    return repository_names[repository_choice]

def retrieve_metadata(repository_name):

    """
    Initialize the assessment by retrieving metadata from the chosen repository.

    Args:
        repository_name (str): The name of the chosen repository.

    Returns:
        tuple: Metadata, repository choice, repository URL, and request status.
    """

    request_status = ""
    metadata = ""
    url = ""

    if repository_name == "ArrayExpress":
        repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
        url = "https://www.re3data.org/repository/r3d100010222"

        # Initial request to get the total number of hits
        initial_response = requests.get(repository_api, params={
            "study_type": "transcription profiling by array",
            "pageSize": 1,  # We only need the meta information initially
            "page": 1
        })
        initial_data = initial_response.json()
        total_hits = initial_data.get("totalHits", 0)
        page_size = 100
        total_pages = (total_hits // page_size) + 1

        experiment_ids = []
        # Loop through all pages
        for page in range(1, total_pages + 1):
            r_repo = requests.get(repository_api, params={
                "study_type": "transcription profiling by array",
                "pageSize": page_size,
                "page": page
            })
            request_status = r_repo.status_code
            metadata = r_repo.json()
            hits = metadata.get("hits", [])
            for hit in hits:
                accession = hit.get("accession", "")
                if len(accession) == 11:
                    experiment_ids.append(accession)

        print(f"Total Study IDs retrieved: {len(experiment_ids)}")

        metadata_list = []
        for hit in experiment_ids:
            print(hit)
            study_accession = hit
            url_1 = utils.get_json_metadata_link(study_accession)
            r_repo = requests.get(url_1)
            request_status = r_repo.status_code
            metadata = r_repo.json()
            metadata_list.append(metadata)

    if repository_name == "Gene Expression Omnibus":
        repository_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        url = "https://www.re3data.org/repository/r3d100010283"
        repository_acronym = "gds" 
        r_repo = requests.get(repository_api, params={"db": repository_acronym})
        request_status = r_repo.status_code
        root_meta = ET.fromstring(r_repo.text)
        metadata = root_meta[0]

    if repository_name == "GWAS Catalog":
        url = "https://www.re3data.org/repository/r3d100014209"
        base_url = "https://www.ebi.ac.uk/gwas/rest/api/studies"
        page = 1
        page_size = 500
        hits = []

        while True:
            r_repo = requests.get(base_url, params={"page": page, "size": page_size})
            request_status = r_repo.status_code
            metadata = r_repo.json()

            # Break the loop if there are no more studies to retrieve
            if not metadata["_embedded"]["studies"]:
                break

            for accession in metadata["_embedded"]["studies"]:
                hits.append(accession["accessionId"])

            page += 1

        print(f"Total Study IDs retrieved: {len(hits)}")

        metadata_list = []
        for study_accession in hits:
            accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
            r_repo = requests.get(accession_url)
            request_status = r_repo.status_code
            metadata = r_repo.json()
            metadata_list.append(metadata)

        metadata = metadata_list

    if repository_name == "ENCODE":
        url = "https://www.re3data.org/repository/r3d100013051"

        # Retrieve all biosamples
        biosample_base_url = 'https://www.encodeproject.org/search/?type=Biosample&limit=all&format=json'
        headers = {'accept': 'application/json'}

        biosample_response = requests.get(biosample_base_url, headers=headers)
        if biosample_response.status_code == 200:
            biosample_metadata = biosample_response.json()
            biosample_hits = [accession["accession"] for accession in biosample_metadata["@graph"] if
                              "accession" in accession]
        else:
            print("Failed to retrieve biosamples.")
            return

        print(f"Total Biosample IDs retrieved: {len(biosample_hits)}")

        biosample_data_list = []
        for accession in biosample_hits:
            accession_url = f'https://www.encodeproject.org/biosample/{accession}/?frame=object'
            response = requests.get(accession_url, headers=headers)
            if response.status_code == 200:
                metadata = response.json()
                biosample_data_list.append(metadata)

        # Retrieve all experiments
        experiment_base_url = 'https://www.encodeproject.org/search/?type=Experiment&limit=all&format=json'
        experiment_response = requests.get(experiment_base_url, headers=headers)
        if experiment_response.status_code == 200:
            experiment_metadata = experiment_response.json()
            experiment_hits = [accession["accession"] for accession in experiment_metadata["@graph"] if
                               "accession" in accession]
        else:
            print("Failed to retrieve experiments.")
            return

        print(f"Total Experiment IDs retrieved: {len(experiment_hits)}")

        experiment_data_list = []
        for accession in experiment_hits:
            accession_url = f'https://www.encodeproject.org/experiment/{accession}/?frame=object'
            response = requests.get(accession_url, headers=headers)
            if response.status_code == 200:
                metadata = response.json()
                experiment_data_list.append(metadata)

        metadata = {
            "biosamples": biosample_data_list,
            "experiments": experiment_data_list
        }

    if repository_name == "GENOMIC DATA COMMONS":
        url = "https://www.re3data.org/repository/r3d100012061"
        base_url = 'https://api.gdc.cancer.gov/files'

        all_hits = []
        params = {
            'from': '0',
            'size': '1000',
            'sort': 'file_size:asc',
            'pretty': 'true'
        }

        while True:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                metadata = response.json()
                hits = metadata["data"]["hits"]
                all_hits.extend([accession["id"] for accession in hits if "id" in accession])
                print(f"Fetched {len(hits)} records, Total: {len(all_hits)}")

                if len(hits) < 1000:
                    break
                params['from'] = str(int(params['from']) + 1000)
            else:
                print("Failed to retrieve data.")
                break

        print(f"Total Files IDs retrieved: {len(all_hits)}")

        params = {'pretty': 'true'}
        metadata_list = []
        for accession in all_hits:
            accession_url = f'https://api.gdc.cancer.gov/files/{accession}'
            response = requests.get(accession_url, params=params)
            if response.status_code == 200:
                metadata = response.json()
                metadata_list.append(metadata)

        metadata = metadata_list

    if repository_name == "ICGC":
        url = ""
        base_url = 'https://dcc.icgc.org/api/v1/projects'
        params = {
            'filters': '{}',
            'order': 'desc',
            'from': 1,
            'size': 100  # Fetch 100 records per page
        }

        all_hits = []

        while True:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                response_data = response.json()
                hits = response_data.get("hits", [])
                all_hits.extend([hit["id"] for hit in hits if "id" in hit])
                print(f"Fetched {len(hits)} records, Total: {len(all_hits)}")

                # Check if there are more records to fetch
                if len(hits) < 100:
                    break

                # Update 'from' parameter for the next page
                params['from'] += 100
            else:
                print("Failed to retrieve data.")
                break

        print(f"Total Project IDs retrieved: {len(all_hits)}")

        # Retrieve detailed data for each project
        response_data_list = []
        for project in all_hits:
            accession_url = f'https://dcc.icgc.org/api/v1/projects/{project}'
            response = requests.get(accession_url)
            if response.status_code == 200:
                response_data = response.json()
                response_data_list.append(response_data)

    return metadata, repository_choice, url, request_status

def assess(metadata, keywords, repository_choice, url, request_status):
    """
    Assess the FAIR metrics for the given metadata and repository choice.

    Args:
        metadata (list or dict): The metadata to be assessed.
        keywords (list): Keywords to be used in the assessment.
        repository_choice (str): The chosen repository for assessment.
        url (str): The URL of the repository.
        request_status (int): The status code of the metadata request.

    Returns:
        list: A list of scores for each assessed FAIR metric.
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


retrieve_metadata("ArrayExpress")