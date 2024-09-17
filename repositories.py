import requests
import xml.etree.ElementTree as ET
import utils
import json


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
    elif repository_choice == "41":
        metadata_list, request_status, url = fetch_biosamples_metadata(keywords)
    elif repository_choice == "42":
        metadata_list, request_status, url = fetch_experiments_metadata(keywords)
    elif repository_choice == "5":
        metadata_list, request_status, url = fetch_gdc_metadata(keywords)
    elif repository_choice == "6":
        metadata_list, request_status, url = fetch_icgc_metadata(keywords)
    print("\nThe dataset is fetched!")
    return metadata_list, request_status, url

def fetch_arrayexpress_metadata(keywords):
    """
    Fetch metadata from the ArrayExpress repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching ArrayExpress metadata...")
    metadata_list = []
    url = "https://www.re3data.org/repository/r3d100010222"
    repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
    if not keywords:
        print("No keywords provided. Fetching all metadata...")
        metadata, request_status = utils.fetch_ae_metadata(start_batch=0)
        metadata_list.extend(metadata)
    else:
        print(f"Fetching metadata with keywords: {keywords}")
        combined_query = " AND ".join(keywords)
        r_repo = requests.get(repository_api, params={
            "query": combined_query, 
            "pageSize": 500,
        })
        print(f"API Call: {r_repo.url}")
        request_status = r_repo.status_code
        response_data = r_repo.json()
        hits = response_data.get("hits", [])
        experiment_ids = []
        for hit in hits:
            accession = hit.get("accession", "")
            #if len(accession) == 11:
            experiment_ids.append(accession)
        print(f"Total Study IDs retrieved: {len(experiment_ids)}")
        filename = "metadata/arrayexpress.txt"
        with open(filename, 'w') as file:
            for study_accession in experiment_ids:
                url_1 = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{study_accession}"
                r_repo = requests.get(url_1)
                print(f"API Call: {r_repo.url}")
                request_status = r_repo.status_code
                metadata = r_repo.json()
                metadata_list.append(metadata)
                file.write(json.dumps(metadata, indent=4) + '\n')
    return metadata_list, request_status, url

def fetch_geo_metadata(keywords):
    """
    Fetch metadata from the Gene Expression Omnibus (GEO) repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata (Element): XML metadata.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching GEO metadata...")
    metadata = []
    if not keywords:
        print("No keywords provided. Fetching all metadata...")
        metadata, request_status = utils.fetch_geo_metadata(None, start_batch=0)
    else:
        print(f"Fetching metadata with keywords: {keywords}")
        query_string = ' AND '.join(keywords)
        r_repo = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?",
                        params={"db"   : "gds",
                                "term" : query_string,
                                "retmax" : 5000,
                                "usehistory" : "y"})
        print(f"API Call: {r_repo.url}")
        request_status = r_repo.status_code
        root = ET.fromstring(r_repo.text)
        filename = "metadata/geo.txt"
        with open(filename, 'w') as file:
            for field in root.iter('Id'):
                id = field.text
                root_summary = utils.fetch_summary_geo("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", [id])
                inner_content = list(root_summary)
                inner_content_string = ''.join(ET.tostring(child, encoding='unicode') for child in inner_content)
                file.write(inner_content_string + '\n')
                metadata.append(inner_content_string)
    return metadata, request_status, "https://www.re3data.org/repository/r3d100010283"

def fetch_gwas_metadata(keywords):
    """
    Fetch metadata from the GWAS Catalog repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching GWAS Catalog metadata...")
    url = "https://www.re3data.org/repository/r3d100014209"
    base_url = "https://www.ebi.ac.uk/gwas/rest/api/studies/search/findByDiseaseTrait?"
    metadata_list = []
    hits = []
    if not keywords:
        print("No keywords provided. Fetching all metadata...")
        metadata, request_status = utils.fetch_gwas_metadata(None, start_batch=0)
        metadata_list.extend(metadata)
    else: 
        print(f"Fetching metadata with keywords: {keywords}")
        params = {"diseaseTrait": keywords[-1], "size": 500}
        r_repo = requests.get(base_url, params=params)
        print(f"API Call: {r_repo.url}")
        request_status = r_repo.status_code
        metadata = r_repo.json()
        for study in metadata["_embedded"]["studies"]:
            study_accession = study["accessionId"]
            hits.append(study_accession)
        filename = "metadata/gwas.txt"
        print(f"Total Study IDs retrieved: {len(hits)}")
        with open(filename, 'w') as file:
            for study_accession in hits:
                accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
                r_repo = requests.get(accession_url)
                print(f"API Call: {r_repo.url}")
                request_status = r_repo.status_code
                metadata = r_repo.json()
                metadata_list.append(metadata)
                file.write(json.dumps(metadata, indent=4) + '\n')
    return metadata_list, request_status, url


def fetch_biosamples_metadata(keywords):
    """
    Fetch biosample metadata from the ENCODE repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - biosample_data_list (list): List of biosample metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching ENCODE biosamples metadata...")
    url = "https://www.re3data.org/repository/r3d100013051"
    headers = {'accept': 'application/json'}
    biosample_base_url = 'https://www.encodeproject.org/search/?type=Biosample' #https://www.encodeproject.org/search/?searchTerm=bone+chip&frame=object&format=json
                                                                 #https://www.encodeproject.org/search/?type=Biosample&searchTerm=melanoma&limit=all&format=json
    if not keywords:
        print("No keywords provided. Fetching all biosample metadata...")
        metadata, request_status = utils.fetch_encode_biosamples_metadata(None, start_batch=0)
        biosample_data_list.extend(metadata)
    else:
        print(f"Fetching biosample metadata with keywords: {keywords}")
        biosample_base_url += "&searchTerm=" + "+".join(keywords) + "&limit=all&format=json"
        biosample_response = requests.get(biosample_base_url, headers=headers)
        print(f"API Call: {biosample_response.url}")
        request_status = biosample_response.status_code
        if request_status == 200:
            biosample_metadata = biosample_response.json()
            biosample_hits = [accession["accession"] for accession in biosample_metadata["@graph"] if "accession" in accession]
            print(f"Total Biosample IDs retrieved: {len(biosample_hits)}")
        else:
            print("Failed to retrieve biosamples.")
            return [], request_status, url
        biosample_data_list = []
        filename = "metadata/encode_biosamples.txt"
        with open(filename, 'w') as file:
            for accession in biosample_hits:
                accession_url = f'https://www.encodeproject.org/biosample/{accession}'
                response = requests.get(accession_url, headers=headers)
                print(f"API Call: {response.url}")
                if response.status_code == 200:
                    metadata = response.json()
                    biosample_data_list.append(metadata)
                    file.write(json.dumps(metadata, indent=4) + '\n')
    return biosample_data_list, request_status, url


def fetch_experiments_metadata(keywords):
    """
    Fetch experiment metadata from the ENCODE repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - experiment_data_list (list): List of experiment metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching ENCODE experiments metadata...")
    url = "https://www.re3data.org/repository/r3d100013051"
    headers = {'accept': 'application/json'}
    experiment_base_url = 'https://www.encodeproject.org/search/?type=Experiment'
    if not keywords:
        print("No keywords provided. Fetching all experiment metadata...")
        metadata, request_status = utils.fetch_encode_biosamples_metadata(None, start_batch=0)
        experiment_data_list.extend(metadata)
    else:
        print(f"Fetching experiment metadata with keywords: {keywords}")
        experiment_base_url += "&searchTerm=" + "+".join(keywords) + "&limit=all&format=json"
        experiment_response = requests.get(experiment_base_url, headers=headers)
        print(f"API Call: {experiment_response.url}")
        request_status = experiment_response.status_code
        if request_status == 200:
            experiment_metadata = experiment_response.json()
            experiment_hits = [accession["accession"] for accession in experiment_metadata["@graph"] if "accession" in accession]
            print(f"Total Experiment IDs retrieved: {len(experiment_hits)}")
        else:
            print("Failed to retrieve experiments.")
            return [], request_status, url
        experiment_data_list = []
        filename = "metadata/encode_experiments.txt"
        with open(filename, 'w') as file:
            for accession in experiment_hits:
                accession_url = f'https://www.encodeproject.org/experiment/{accession}'
                response = requests.get(accession_url, headers=headers)
                print(f"API Call: {response.url}")
                if response.status_code == 200:
                    metadata = response.json()
                    experiment_data_list.append(metadata)
                    file.write(json.dumps(metadata, indent=4) + '\n')
    return experiment_data_list, request_status, url

def fetch_gdc_metadata(keywords):
    """
    Fetch metadata from the Genomic Data Commons (GDC) repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching GDC metadata...")
    url = "https://www.re3data.org/repository/r3d100012061"
    metadata_list = []
    if not keywords:
        print("No keywords provided. Fetching all metadata...")
        metadata, request_status = utils.fetch_gdc_metadata()
        metadata_list.extend(metadata)
    else:
        print(f"Fetching metadata with keywords: {keywords}")
        files_endpt = "https://api.gdc.cancer.gov/files"
        filters = {
            "content":[
                {
                "op": "in",
                "content":{
                    "field": "cases.project.primary_site",
                    "value": keywords[-1]
                    }
                }
            ]
        }
        params = {
            "filters": filters,
            "size": "2000"
            }
        response = requests.get(files_endpt, json = params)
        print(f"API Call: {response.url}")
        if response.status_code == 200:
            response_data = response.json()
        request_status = (response.status_code)
        hits = []
        for accession in response_data["data"]["hits"]:
            try:
                hits.append(accession["id"])
            except:
                continue
        print(f"Total Files IDs retrieved: {len(hits)}")
        params = {
            'pretty': 'true'
        }
        for i in range(len(hits)):    
            study_accession = hits[i]
            accession_url = f'https://api.gdc.cancer.gov/files/{study_accession}'
            response = requests.get(accession_url, params=params)
            print(f"API Call: {response.url}")
            response_data = response.json()
            metadata_list.append(response_data)
    return metadata_list, request_status, url

def fetch_icgc_metadata(keywords):
    """
    Fetch metadata from the International Cancer Genome Consortium (ICGC) repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching ICGC metadata...")
    url = "https://dcc.icgc.org/api/v1/projects"
    base_url = 'https://dcc.icgc.org/api/v1/projects'
    params = {
        'filters': '{}',
        'order': 'desc',
        'from': 1,
        'size': 100
    }
    metadata_list = []
    if not keywords:
        print("No keywords provided. Fetching all metadata...")
        metadata, request_status = utils.fetch_icgc_metadata(None, start_batch=0)
        metadata_list.extend(metadata)
    else:
        print(f"Fetching metadata with keywords: {keywords}")
        all_hits = []
        while True:
            response = requests.get(base_url, params=params)
            print(f"API Call: {response.url}")
            request_status = response.status_code
            if request_status == 200:
                metadata = response.json()
                hits = metadata.get("hits", [])
                all_hits.extend([hit["id"] for hit in hits if "id" in hit])
                print(f"Fetched {len(hits)} records, Total: {len(all_hits)}")
                if len(hits) < 100:
                    break
                params['from'] += 100
            else:
                print("Failed to retrieve data.")
                break
        filename = "metadata/icgc.txt"
        with open(filename, 'w') as file:
            for project in all_hits:
                accession_url = f'https://dcc.icgc.org/api/v1/projects/{project}'
                response = requests.get(accession_url)
                print(f"API Call: {response.url}")
                if response.status_code == 200:
                    metadata = response.json()
                    metadata_list.append(metadata)
                    file.write(json.dumps(metadata, indent=4) + '\n')
    return metadata_list, request_status, url
