import requests
import xml.etree.ElementTree as ET
import json
import os
from tqdm import tqdm  # Progress bar library
from time import sleep

def retrieve_metadata(repository_choice, keywords):
    """
    Retrieve metadata based on the chosen repository and keywords.

    Parameters:
    - repository_choice (str): The choice of repository (e.g., "1" for ArrayExpress).
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata_list (list): A list of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    metadata_list = []
    request_status = 400
    url = ""

    if repository_choice == "1":
        metadata_list, request_status, url = fetch_arrayexpress_metadata(keywords)
    elif repository_choice == "2":
        metadata_list, request_status, url = fetch_geo_metadata(keywords)
    elif repository_choice == "3":
        metadata_list, request_status, url = fetch_gwas_metadata(keywords)
    elif repository_choice == "4":
        metadata_list, request_status, url = fetch_encode_metadata(keywords)
    elif repository_choice == "5":
        metadata_list, request_status, url = fetch_gdc_metadata()
    elif repository_choice == "6":
        metadata_list, request_status, url = fetch_icgc_metadata()

    return metadata_list, request_status, url

def fetch_arrayexpress_metadata(keywords):
    url = "https://www.re3data.org/repository/r3d100010222"
    repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
    metadata_list = []
    page_size = 100

    # Initial request to get total hits
    initial_response = requests.get(repository_api, params={
        "keywords": " ".join(keywords),
        "pageSize": 1,
        "page": 1
    })
    initial_data = initial_response.json()
    total_hits = initial_data.get("totalHits", 0)
    total_pages = (total_hits // page_size) + 1

    filename = "metadata/arrayexpress3.txt"
    with open(filename, 'w') as file:
        for page in tqdm(range(1, total_pages + 1), desc='Fetching ArrayExpress', unit='pages'):
            r_repo = requests.get(repository_api, params={
                "keywords": " ".join(keywords),
                "pageSize": page_size,
                "page": page
            })
            request_status = r_repo.status_code
            metadata = r_repo.json()
            hits = metadata.get("hits", [])
            for hit in hits:
                study_accession = hit.get("accession", "")
                if len(study_accession) == 11:
                    url_1 = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{study_accession}"
                    r_study = requests.get(url_1)
                    request_status = r_study.status_code
                    if request_status == 200:
                        metadata = r_study.json()
                        metadata_list.append(metadata)
                        file.write(json.dumps(metadata, indent=4) + '\n')
                    else:
                        print(f"Failed to fetch study: {study_accession}")

            sleep(0.1)

    return metadata_list, request_status, url

def fetch_geo_metadata(keywords):
    repository_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    url = "https://www.re3data.org/repository/r3d100010283"
    repository_acronym = "gds"
    params = {"db": repository_acronym, "retmax": 100}
    if keywords:
        params["term"] = " AND ".join(keywords)

    metadata_list = []
    filename = "metadata/geo.txt"
    with open(filename, 'w') as file:
        for retstart in tqdm(range(0, 10000, 100), desc='Fetching GEO', unit='batch'):
            params["retstart"] = retstart
            r_repo = requests.get(repository_api, params=params)
            request_status = r_repo.status_code
            root_meta = ET.fromstring(r_repo.text)
            for record in root_meta.findall(".//Id"):
                metadata_list.append(record.text)
                file.write(ET.tostring(record, encoding='unicode') + '\n')

            sleep(0.1)

    return metadata_list, request_status, url

def fetch_gwas_metadata(keywords):
    url = "https://www.re3data.org/repository/r3d100014209"
    base_url = "https://www.ebi.ac.uk/gwas/rest/api/studies"
    page_size = 500
    metadata_list = []
    page = 1

    params = {"page": page, "size": page_size}
    if keywords:
        params["q"] = " AND ".join(keywords)

    filename = "metadata/gwas.txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        while True:
            r_repo = requests.get(base_url, params=params)
            request_status = r_repo.status_code
            if request_status != 200:
                print(f"Request failed with status code: {request_status}")
                break

            metadata = r_repo.json()
            studies = metadata["_embedded"]["studies"]
            if not studies:
                break

            for study in studies:
                study_accession = study.get("accessionId", "")
                accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
                r_study = requests.get(accession_url)
                if r_study.status_code == 200:
                    study_metadata = r_study.json()
                    metadata_list.append(study_metadata)
                    file.write(json.dumps(study_metadata, indent=4) + '\n')
                else:
                    print(f"Study request failed with status code: {r_study.status_code}")

            page += 1
            params["page"] = page
            sleep(0.1)

    return metadata_list, request_status, url

def fetch_encode_metadata(keywords):
    url = "https://www.re3data.org/repository/r3d100013051"
    headers = {'accept': 'application/json'}

    biosample_hits, biosample_data_list = fetch_encode_biosamples(headers, keywords)
    experiment_hits, experiment_data_list = fetch_encode_experiments(headers, keywords)

    metadata = {
        "biosamples": biosample_data_list,
        "experiments": experiment_data_list
    }

    filename = "metadata/encode.txt"
    with open(filename, 'w') as file:
        file.write(json.dumps(metadata, indent=4) + '\n')

    return metadata, 200, url

import requests
import json
from tqdm import tqdm
from time import sleep, time

def fetch_encode_biosamples(headers, keywords):
    biosample_base_url = 'https://www.encodeproject.org/search/?type=Biosample&limit=all&format=json'
    if keywords:
        biosample_base_url += "&searchTerm=" + "+".join(keywords)

    biosample_response = requests.get(biosample_base_url, headers=headers)
    if biosample_response.status_code == 200:
        biosample_metadata = biosample_response.json()
        biosample_hits = []
        for accession in biosample_metadata["@graph"]:
            if "accession" in accession:
                accession_id = accession["accession"]
                print(f"Found accession ID: {accession_id}")
                biosample_hits.append(accession_id)
    else:
        print("Failed to retrieve biosamples.")
        return [], []

    biosample_data_list = []
    filename = "metadata/encode_biosamples.txt"
    
    start_time = time()
    with open(filename, 'a') as file:  # Using 'a' to append to the file
        for i in tqdm(range(0, len(biosample_hits), 100), desc='Fetching ENCODE Biosamples', unit='batch'):
            batch = biosample_hits[i:i + 100]
            for accession in batch:
                print(f"Retrieving data for accession ID: {accession}")
                accession_url = f'https://www.encodeproject.org/biosample/{accession}/?frame=object'
                response = requests.get(accession_url, headers=headers)
                if response.status_code == 200:
                    metadata = response.json()
                    biosample_data_list.append(metadata)
                    file.write(json.dumps(metadata) + '\n')  # Writing each metadata as a new line

                elapsed_time = time() - start_time
                print(f"Elapsed time: {elapsed_time:.2f} seconds")

            sleep(0.1)

    return biosample_hits, biosample_data_list

def fetch_encode_experiments(headers, keywords):
    experiment_base_url = 'https://www.encodeproject.org/search/?type=Experiment&limit=all&format=json'
    if keywords:
        experiment_base_url += "&searchTerm=" + "+".join(keywords)

    experiment_response = requests.get(experiment_base_url, headers=headers)
    if experiment_response.status_code == 200:
        experiment_metadata = experiment_response.json()
        experiment_hits = []
        for accession in experiment_metadata["@graph"]:
            if "accession" in accession:
                accession_id = accession["accession"]
                print(f"Found accession ID: {accession_id}")
                experiment_hits.append(accession_id)
    else:
        print("Failed to retrieve experiments.")
        return [], []

    experiment_data_list = []
    filename = "metadata/encode_experiments.txt"
    
    start_time = time()
    with open(filename, 'a') as file:  # Using 'a' to append to the file
        for i in tqdm(range(0, len(experiment_hits), 100), desc='Fetching ENCODE Experiments', unit='batch'):
            batch = experiment_hits[i:i + 100]
            for accession in batch:
                print(f"Retrieving data for accession ID: {accession}")
                accession_url = f'https://www.encodeproject.org/experiment/{accession}/?frame=object'
                response = requests.get(accession_url, headers=headers)
                if response.status_code == 200:
                    metadata = response.json()
                    experiment_data_list.append(metadata)
                    file.write(json.dumps(metadata) + '\n')  # Writing each metadata as a new line

                elapsed_time = time() - start_time
                print(f"Elapsed time: {elapsed_time:.2f} seconds")

            sleep(0.1)

    return experiment_hits, experiment_data_list

def read_metadata_from_file(filename):
    metadata_list = []
    with open(filename, 'r') as file:
        for line in file:
            metadata_list.append(json.loads(line.strip()))
    return metadata_list

# Example usage:
# headers = {'Authorization': 'Bearer YOUR_API_KEY'}
# biosample_hits, biosample_data_list = fetch_encode_biosamples(headers, ["keyword1", "keyword2"])
# experiment_hits, experiment_data_list = fetch_encode_experiments(headers, ["keyword1", "keyword2"])
# biosample_metadata_list = read_metadata_from_file("metadata/encode_biosamples.txt")
# experiment_metadata_list = read_metadata_from_file("metadata/encode_experiments.txt")



def fetch_gdc_metadata():
    url = "https://www.re3data.org/repository/r3d100012515"
    repository_api = "https://api.gdc.cancer.gov/projects"
    metadata_list = []
    page_size = 100

    # Initial request to get total hits
    initial_response = requests.get(repository_api, params={
        "size": 1,
        "from": 0
    })
    initial_data = initial_response.json()
    total_hits = initial_data.get("pagination", {}).get("total", 0)
    total_pages = (total_hits // page_size) + 1

    filename = "metadata/gdc.txt"
    with open(filename, 'w') as file:
        for page in tqdm(range(total_pages), desc='Fetching GDC', unit='pages'):
            r_repo = requests.get(repository_api, params={
                "size": page_size,
                "from": page * page_size
            })
            request_status = r_repo.status_code
            if request_status != 200:
                print(f"Request failed with status code: {request_status}")
                break

            metadata = r_repo.json()
            hits = metadata.get("data", {}).get("hits", [])
            for hit in hits:
                metadata_list.append(hit)
                file.write(json.dumps(hit, indent=4) + '\n')

            sleep(0.1)

    return metadata_list, request_status, url

def fetch_icgc_metadata():
    url = "https://www.re3data.org/repository/r3d100010602"
    repository_api = "https://dcc.icgc.org/api/v1/projects"
    metadata_list = []
    page_size = 50

    # Initial request to get total hits
    initial_response = requests.get(repository_api, params={
        "size": 1,
        "page": 1
    })
    initial_data = initial_response.json()
    total_hits = initial_data.get("total", 0)
    total_pages = (total_hits // page_size) + 1

    filename = "metadata/icgc.txt"
    with open(filename, 'w') as file:
        for page in tqdm(range(1, total_pages + 1), desc='Fetching ICGC', unit='pages'):
            r_repo = requests.get(repository_api, params={
                "size": page_size,
                "page": page
            })
            request_status = r_repo.status_code
            if request_status != 200:
                print(f"Request failed with status code: {request_status}")
                break

            metadata = r_repo.json()
            hits = metadata.get("hits", [])
            for hit in hits:
                metadata_list.append(hit)
                file.write(json.dumps(hit, indent=4) + '\n')

            sleep(0.1)

    return metadata_list, request_status, url
