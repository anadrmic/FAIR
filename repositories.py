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
    elif repository_choice == "4":
        metadata_list, request_status, url = fetch_encode_metadata(keywords)
    elif repository_choice == "5":
        metadata_list, request_status, url = fetch_gdc_metadata()
    elif repository_choice == "6":
        metadata_list, request_status, url = fetch_icgc_metadata()

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
    request_status = ""
    metadata = ""
    url = "https://www.re3data.org/repository/r3d100010222"
    repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"

    initial_response = requests.get(repository_api, params={
        "study_type": "transcription profiling by array",
        "pageSize": 1,
        "page": 1
    })
    initial_data = initial_response.json()
    total_hits = initial_data.get("totalHits", 0)
    page_size = 100
    total_pages = (total_hits // page_size) + 1

    experiment_ids = []
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
    filename = "metadata/arrayexpress.txt"
    with open(filename, 'w') as file:
        for hit in experiment_ids:
            study_accession = hit
            url_1 = utils.get_json_metadata_link(study_accession)
            r_repo = requests.get(url_1)
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
    repository_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
    url = "https://www.re3data.org/repository/r3d100010283"
    repository_acronym = "gds"

    params = {"db": repository_acronym}
    if keywords:
        params["term"] = " AND ".join(keywords)

    r_repo = requests.get(repository_api, params=params)
    request_status = r_repo.status_code
    root_meta = ET.fromstring(r_repo.text)
    metadata = root_meta[0]

    filename = "metadata/geo.txt"
    with open(filename, 'w') as file:
        file.write(ET.tostring(metadata, encoding='unicode') + '\n')

    return metadata, request_status, url

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
    url = "https://www.re3data.org/repository/r3d100014209"
    base_url = "https://www.ebi.ac.uk/gwas/rest/api/studies"
    page = 1
    page_size = 500
    hits = []

    params = {"page": page, "size": page_size}
    if keywords:
        params["q"] = " AND ".join(keywords)

    while True:
        r_repo = requests.get(base_url, params=params)
        request_status = r_repo.status_code
        metadata = r_repo.json()

        if not metadata["_embedded"]["studies"]:
            break

        for accession in metadata["_embedded"]["studies"]:
            hits.append(accession["accessionId"])

        page += 1
        params["page"] = page

    metadata_list = []
    filename = "metadata/gwas.txt"
    with open(filename, 'w') as file:
        for study_accession in hits:
            accession_url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
            r_repo = requests.get(accession_url)
            request_status = r_repo.status_code
            metadata = r_repo.json()
            metadata_list.append(metadata)
            file.write(json.dumps(metadata, indent=4) + '\n')

    return metadata_list, request_status, url

def fetch_encode_metadata(keywords):
    """
    Fetch metadata from the ENCODE repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - metadata (dict): Dictionary containing biosamples and experiments metadata.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
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

def fetch_encode_biosamples(headers, keywords):
    """
    Fetch biosample metadata from the ENCODE repository.

    Parameters:
    - headers (dict): HTTP headers for the request.
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - biosample_hits (list): List of biosample accessions.
    - biosample_data_list (list): List of biosample metadata records.
    """
    biosample_base_url = 'https://www.encodeproject.org/search/?type=Biosample&limit=all&format=json'
    if keywords:
        biosample_base_url += "&searchTerm=" + "+".join(keywords)

    biosample_response = requests.get(biosample_base_url, headers=headers)
    if biosample_response.status_code == 200:
        biosample_metadata = biosample_response.json()
        biosample_hits = [accession["accession"] for accession in biosample_metadata["@graph"] if
                          "accession" in accession]
    else:
        print("Failed to retrieve biosamples.")
        return [], []

    biosample_data_list = []
    filename = "metadata/encode_biosamples.txt"
    with open(filename, 'w') as file:
        for accession in biosample_hits:
            accession_url = f'https://www.encodeproject.org/biosample/{accession}/?frame=object'
            response = requests.get(accession_url, headers=headers)
            if response.status_code == 200:
                metadata = response.json()
                biosample_data_list.append(metadata)
                file.write(json.dumps(metadata, indent=4) + '\n')

    return biosample_hits, biosample_data_list

def fetch_encode_experiments(headers, keywords):
    """
    Fetch experiment metadata from the ENCODE repository.

    Parameters:
    - headers (dict): HTTP headers for the request.
    - keywords (list): List of keywords to filter metadata.

    Returns:
    - experiment_hits (list): List of experiment accessions.
    - experiment_data_list (list): List of experiment metadata records.
    """
    experiment_base_url = 'https://www.encodeproject.org/search/?type=Experiment&limit=all&format=json'
    if keywords:
        experiment_base_url += "&searchTerm=" + "+".join(keywords)

    experiment_response = requests.get(experiment_base_url, headers=headers)
    if experiment_response.status_code == 200:
        experiment_metadata = experiment_response.json()
        experiment_hits = [accession["accession"] for accession in experiment_metadata["@graph"] if
                           "accession" in accession]
    else:
        print("Failed to retrieve experiments.")
        return [], []

    experiment_data_list = []
    filename = "metadata/encode_experiments.txt"
    with open(filename, 'w') as file:
        for accession in experiment_hits:
            accession_url = f'https://www.encodeproject.org/experiment/{accession}/?frame=object'
            response = requests.get(accession_url, headers=headers)
            if response.status_code == 200:
                metadata = response.json()
                experiment_data_list.append(metadata)
                file.write(json.dumps(metadata, indent=4) + '\n')

    return experiment_hits, experiment_data_list

def fetch_gdc_metadata():
    """
    Fetch metadata from the Genomic Data Commons (GDC) repository.

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
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

    params = {'pretty': 'true'}
    metadata_list = []
    filename = "metadata/gdc.txt"
    with open(filename, 'w') as file:
        for accession in all_hits:
            accession_url = f'https://api.gdc.cancer.gov/files/{accession}'
            response = requests.get(accession_url, params=params)
            if response.status_code == 200:
                metadata = response.json()
                metadata_list.append(metadata)
                file.write(json.dumps(metadata, indent=4) + '\n')

    return metadata_list, response.status_code, url

def fetch_icgc_metadata():
    """
    Fetch metadata from the International Cancer Genome Consortium (ICGC) repository.

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    url = ""
    base_url = 'https://dcc.icgc.org/api/v1/projects'
    params = {
        'filters': '{}',
        'order': 'desc',
        'from': 1,
        'size': 100
    }

    all_hits = []

    while True:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
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

    metadata_list = []
    filename = "metadata/icgc.txt"
    with open(filename, 'w') as file:
        for project in all_hits:
            accession_url = f'https://dcc.icgc.org/api/v1/projects/{project}'
            response = requests.get(accession_url)
            if response.status_code == 200:
                metadata = response.json()
                metadata_list.append(metadata)
                file.write(json.dumps(metadata, indent=4) + '\n')

    return metadata_list, response.status_code, url