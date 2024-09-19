import requests  
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm
from time import sleep
import logging
import random
from tqdm import tqdm
import json
import urllib.parse
from bs4 import BeautifulSoup

def check_required_fields_json(json_elements, required_fields):
    total_count = len(json_elements)
    if total_count == 0:
        return "No JSON elements provided.", 0, 0, {}

    all_required_count = 0
    missing_all_count = 0
    missing_fields_count = {field: 0 for field in required_fields}

    for element in json_elements:
        has_all_required = True
        for field in required_fields:
            value = element.get(field)
            if value in [None, '', [], {}]:
                missing_fields_count[field] += 1
                has_all_required = False
                print(f"Field: {field}, Value: {value} (Missing or empty)")
        if has_all_required:
            all_required_count += 1
        else:
            missing_all_count += 1
    all_required_percentage = (all_required_count / total_count) * 100 if total_count > 0 else 0
    missing_all_percentage = (missing_all_count / total_count) * 100 if total_count > 0 else 0

    return all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count

def check_required_fields_json_gdc(json_elements, required_fields):
    total_count = len(json_elements)
    if total_count == 0:
        return "No JSON elements provided.", 0, 0, {}

    all_required_count = 0
    missing_all_count = 0
    missing_fields_count = {field: 0 for field in required_fields}

    for element in json_elements:
        element = element["data"]
        has_all_required = True
        for field in required_fields:
            value = element.get(field)
            if value in [None, '', [], {}]:
                missing_fields_count[field] += 1
                has_all_required = False
                print(f"Field: {field}, Value: {value} (Missing or empty)")
        if has_all_required:
            all_required_count += 1
        else:
            missing_all_count += 1
    all_required_percentage = (all_required_count / total_count) * 100 if total_count > 0 else 0
    missing_all_percentage = (missing_all_count / total_count) * 100 if total_count > 0 else 0

    return all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count

def initialize_output_file(filename):
    """
    Initialize the output file by clearing its contents.

    Args:
        filename (str): The filename of the output file.
    """
    with open(filename, "w") as file:
        file.write("")

def print_evaluation(principle, description, score, explanation):
    """
    Print the evaluation details.

    Args:
        principle (str): The principle being evaluated.
        description (str): Description of the evaluation.
        score (float): The score of the evaluation.
        explanation (str): Explanation of the result.
    """
    print("______________________________________________________________________________________________________________")
    print(f"Principle: {principle}")
    print(f"Description: {description}")
    print(f"Score: {score}")
    print(f"Explanation: {explanation}")
    print("______________________________________________________________________________________________________________")

def check_required_fields_geo(xml_list, fields):
    total_xmls = len(xml_list)
    all_required_count = 0
    missing_all_count = 0
    missing_fields_count = {field: 0 for field in fields}

    for xml_str in xml_list:
        try:
            root = ET.fromstring(xml_str)
            present_fields = set()

            for field in fields:
                element = root.find(f".//Item[@Name='{field}']")
                if element is not None:
                    value = element.text.strip() if element.text else ""
                    if value:
                        present_fields.add(field)
                    else:
                        missing_fields_count[field] += 1
                else:
                    missing_fields_count[field] += 1
            if len(present_fields) == len(fields):
                all_required_count += 1
            if len(present_fields) == 0:
                missing_all_count += 1

        except ET.ParseError:
            pass
    
    all_required_percentage = (all_required_count / total_xmls) * 100 if total_xmls > 0 else 0
    missing_all_percentage = (missing_all_count / total_xmls) * 100 if total_xmls > 0 else 0    
    return all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_xmls, missing_all_count

def find_list_in_list(long_list, short_list):

    """
    Find occurrences of elements from a short list in a long list.

    Args:
        long_list (list): The list to search within.
        short_list (list): The list of elements to search for.

    Returns:
        tuple: Two lists - one with found elements and one with their indices.
    """
    found = []
    index = []
    for i in range(len(long_list)):
        for j in range(len(short_list)):
            if long_list[i].find(short_list[j]) != -1:
                found.append(short_list[j])
                index.append(i)
    return found, index

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), 
       retry=retry_if_exception_type(requests.exceptions.RequestException))
def title_geo(metadata_list, start_element=0):
    found_count = 0
    not_found_count = 0
    session = create_session_with_retries()

    for index, root in enumerate(tqdm(metadata_list[start_element:], desc="Processing datasets", unit="dataset"), start=start_element):
        root = metadata_list[index]
        try:
            title_element = ET.fromstring(root).find(".//Item[@Name='title']")
            if title_element is not None:
                title = urllib.parse.quote(title_element.text)
                search_url = f"https://datasetsearch.research.google.com/search?query={title}"
                
                response = session.get(search_url)
                
                if title.lower() in BeautifulSoup(response.content, 'html.parser').get_text().lower():
                    found_count += 1
                    print(f"The dataset for {title} is found on Google Dataset Search.")
                else:
                    not_found_count += 1
                    # print(f"The dataset for {title} is NOT found on Google Dataset Search.")
            else:
                not_found_count += 1
        
        except Exception as e:
            with open("details.txt", "a") as details_file:
                details_file.write(f"Exception occurred at index {index}.\n")
                details_file.write(f"Element content: {root}\n")
                details_file.write(f"Exception details: {str(e)}\n")
                details_file.write(f"Found count so far: {found_count}\n")
                details_file.write(f"Not found count so far: {not_found_count}\n\n")
    
    total_count = found_count + not_found_count
    if total_count == 0:
        return "No elements to check.", 0, 0
    
    found_percentage = (found_count / total_count)  
    return found_percentage


### FETCHING THE WHOLE ARRAY EXPRESS DB ###

import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm

# Retry strategy with tenacity for any failed HTTP requests
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), 
       retry=retry_if_exception_type(requests.exceptions.RequestException))
def fetch_with_retries(session, url, params=None):
    response = session.get(url, params=params)
    response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
    return response

def create_session_with_retries():
    session = requests.Session()
    return session

# Fetch a single page of study data
def fetch_page_data(session, repository_api, page, page_size):
    params = {
        "pageSize": page_size,
        "page": page
    }
    response = fetch_with_retries(session, repository_api, params=params)
    return response.json().get("hits", [])

# Function to process hits and store them
def process_hits(hits, file, experiment_ids):
    for hit in hits:
        accession = hit.get("accession", "")
        if accession:
            experiment_ids.append(accession)
            file.write(accession + "\n")

# Fetch all study hits using pagination and concurrency
def fetch_hits_concurrently(session, repository_api, page_size=100, start_page=1):
    print(f"Fetching study hits from {repository_api}...")

    # Fetch the initial data to get the total number of hits
    initial_response = session.get(repository_api, params={"pageSize": 1, "page": 1})
    initial_data = initial_response.json()
    total_hits = initial_data.get("totalHits", 0)

    if total_hits == 0:
        print("No hits found.")
        return []

    total_pages = (total_hits // page_size) + 1
    experiment_ids = []

    # Fetch all pages of hits concurrently
    with open("experiment_ids.txt", "a") as file:
        with ThreadPoolExecutor(max_workers=4) as executor:  
            futures = [
                executor.submit(fetch_page_data, session, repository_api, page, page_size)
                for page in range(start_page, total_pages + 1)
            ]

            for future in tqdm(as_completed(futures), total=total_pages - start_page + 1, desc="Fetching datasets", unit="dataset"):
                hits = future.result()
                process_hits(hits, file, experiment_ids)

    print(f"Total Study IDs retrieved: {len(experiment_ids)}")
    return experiment_ids

# Fetch a single study's metadata
def fetch_study_metadata(session, study_accession):
    url = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{study_accession}"
    response = fetch_with_retries(session, url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metadata for {study_accession} with status code {response.status_code}")
        return None

def fetch_arrayexpress_metadata():
    session = create_session_with_retries()
    repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
    page_size = 100  
    start_page = 1   

    # Fetch study hits concurrently using ThreadPoolExecutor
    experiment_ids = fetch_hits_concurrently(session, repository_api, page_size, start_page)

    # If no experiment IDs were retrieved, return early
    if not experiment_ids:
        print("No study IDs retrieved. Exiting.")
        return None, 500 

    metadata_list = []
    filename = "metadata/arrayexpress.txt"

    # Fetch metadata for each study concurrently using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:  
        future_to_study = {
            executor.submit(fetch_study_metadata, session, study_accession): study_accession 
            for study_accession in experiment_ids
        }

        with open(filename, 'w') as file:
            for future in as_completed(future_to_study):
                study_accession = future_to_study[future]
                try:
                    metadata = future.result()
                    if metadata:
                        metadata_list.append(metadata)
                        file.write(json.dumps(metadata, indent=4) + '\n')
                except Exception as exc:
                    print(f"Study {study_accession} generated an exception: {exc}")

    return metadata_list, 200

### FETCHING THE WHOLE GEO DB ###

def fetch_summary_geo(summary_api, record_ids):
    """Fetches summaries for a list of records with retries."""
    summary_params = {"db": "gds", "id": ",".join(record_ids)} 
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r_summary = requests.get(summary_api, params=summary_params, timeout=30)
            print(f"API Call: {r_summary.url}")
            r_summary.raise_for_status()
            root_summary = ET.fromstring(r_summary.text)
            return root_summary
        except (requests.exceptions.RequestException, ET.ParseError) as e:
            if attempt == max_retries - 1:
                logging.error(f"Error fetching summary for IDs {record_ids}: {e}")
            sleep(2 ** attempt + random.uniform(0, 1)) 
    return None

def fetch_batch_geo(retstart, params, repository_api, summary_api):
    """Fetches a batch of records from the repository with retries."""
    params["retstart"] = retstart
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r_repo = requests.get(repository_api, params=params, timeout=60)
            print(f"API Call: {r_repo.url}")
            r_repo.raise_for_status()
            root_meta = ET.fromstring(r_repo.text)
            ids = [record.text for record in root_meta.findall(".//Id")]

            batch_metadata = []
            for i in range(0, len(ids), 100):
                id_group = ids[i:i + 100]
                root_summary = fetch_summary_geo(summary_api, id_group)
                if root_summary is not None:
                    batch_metadata.append(root_summary)
                sleep(0.1)  
            return batch_metadata
        except (requests.exceptions.RequestException, ET.ParseError) as e:
            if attempt == max_retries - 1:
                logging.error(f"Error fetching batch starting at {retstart}: {e}")
            sleep(2 ** attempt + random.uniform(0, 1)) 
    return None

def fetch_geo_metadata(keywords, start_batch=0):
    """Main function to fetch GEO metadata."""
    repository_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    summary_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "gds", "term": "GSE[ETYP]", "retmax": 500}  # Batch size of 500
    if keywords:
        params["term"] = f"GSE[ETYP] AND {' AND '.join(keywords)}"
    metadata_list = []
    filename = "metadata/geo.txt"
    print("Fetching GEO metadata...")
    if not keywords:
        print("No keywords provided. Fetching all metadata...")
    else:
        print(f"Fetching metadata with keywords: {keywords}")
    initial_request = requests.get(repository_api, params=params)
    print(f"API Call: {initial_request.url}")
    initial_root = ET.fromstring(initial_request.text)
    total_count = int(initial_root.find(".//Count").text)

    failed_batches = []

    with open(filename, 'a') as file: 
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_batch_geo, retstart, params.copy(), repository_api, summary_api) 
                       for retstart in range(start_batch * 500, total_count, 500)]
            for future in tqdm(as_completed(futures), total=len(futures), desc='Fetching GEO', unit='batch'):
                try:
                    batch_metadata = future.result()
                    print(len(batch_metadata))
                    if batch_metadata is None:
                        failed_batches.append(future)
                    else:
                        for root_summary in batch_metadata:
                            file.write(ET.tostring(root_summary, encoding='unicode') + '\n')
                            metadata_list.append(ET.tostring(root_summary, encoding='unicode'))
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")

    if failed_batches:
        with open("failed_batches.txt", "w") as fail_file:
            for future in failed_batches:
                params_with_retstart = future.args[1]
                fail_file.write(f"Failed batch with retstart={params_with_retstart['retstart']} and params={params_with_retstart}\n")

    return metadata_list, 200

### FETCH THE WHOLE GWAS CATALOG DB ###

# Fetch a single page of GWAS data
def fetch_page_data_2(session, base_url, page, page_size):
    params = {
        "page": page,
        "size": page_size
    }
    response = fetch_with_retries(session, base_url, params=params)
    return response.json().get("_embedded", {}).get("studies", [])

# Function to process hits and store them
def process_hits_2(hits, file, experiment_ids):
    for study in hits:
        accession = study.get("accessionId", "")
        if accession:
            experiment_ids.append(accession)
            file.write(accession + "\n")

# Fetch all study hits using pagination and concurrency
def fetch_hits_concurrently_2(session, base_url, page_size=100, start_page=0):
    print(f"Fetching study hits from {base_url}...")

    # Fetch the initial data to get the total number of hits
    initial_response = session.get(base_url, params={"page": 0, "size": 1})
    initial_data = initial_response.json()
    total_hits = initial_data.get("page", {}).get("totalElements", 0)

    if total_hits == 0:
        print("No hits found.")
        return []

    total_pages = (total_hits // page_size) + 1
    experiment_ids = []

    # Fetch all pages of hits concurrently
    with open("metadata/gwas_experiment_ids.txt", "a") as file:
        with ThreadPoolExecutor(max_workers=4) as executor:  
            futures = [
                executor.submit(fetch_page_data_2, session, base_url, page, page_size)
                for page in range(start_page, total_pages)
            ]

            for future in tqdm(as_completed(futures), total=total_pages - start_page, desc="Fetching datasets", unit="dataset"):
                hits = future.result()
                process_hits_2(hits, file, experiment_ids)

    print(f"Total Study IDs retrieved: {len(experiment_ids)}")
    return experiment_ids

# Fetch a single study's metadata
def fetch_study_metadata_2(session, study_accession):
    url = f"https://www.ebi.ac.uk/gwas/rest/api/studies/{study_accession}"
    response = fetch_with_retries(session, url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metadata for {study_accession} with status code {response.status_code}")
        return None

# Main function to fetch GWAS metadata
def fetch_gwas_metadata():
    print("Fetching GWAS Catalog metadata...")
    base_url = "https://www.ebi.ac.uk/gwas/rest/api/studies"
    page_size = 100  
    start_page = 0  

    session = create_session_with_retries()

    # Fetch study hits concurrently using ThreadPoolExecutor
    experiment_ids = fetch_hits_concurrently_2(session, base_url, page_size, start_page)

    # If no experiment IDs were retrieved, return early
    if not experiment_ids:
        print("No study IDs retrieved. Exiting.")
        return None, 500  

    metadata_list = []
    filename = "metadata/gwas.txt"

    # Fetch metadata for each study concurrently using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:  
        future_to_study = {
            executor.submit(fetch_study_metadata_2, session, study_accession): study_accession 
            for study_accession in experiment_ids
        }

        with open(filename, 'w') as file:
            for future in as_completed(future_to_study):
                study_accession = future_to_study[future]
                try:
                    metadata = future.result()
                    if metadata:
                        metadata_list.append(metadata)
                        file.write(json.dumps(metadata, indent=4) + '\n')
                except Exception as exc:
                    print(f"Study {study_accession} generated an exception: {exc}")

    return metadata_list, 200

### FETCH THE WHOLE ENCODE BIOSAMPLES DB ###

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), 
       retry=retry_if_exception_type(requests.exceptions.RequestException))
def fetch_with_retries_41(session, url, headers, params):
    response = session.get(url, headers=headers, params=params)
    response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
    return response

# Function to fetch a single page of biosamples
def fetch_biosamples_page(session, base_url, headers, page, limit):
    params = {
        "type": "Biosample",
        "format": "json",
        "frame": "object",
        "limit": limit,
        "from": page * limit
    }
    response = fetch_with_retries_41(session, base_url, headers, params=params)
    return response.json().get("@graph", [])

# Function to process and store the hits (accessions)
def process_biosample_hits(hits, file, biosample_ids):
    for hit in hits:
        accession = hit.get("accession", "")
        if accession:
            biosample_ids.append(accession)
            file.write(accession + "\n")

# Function to fetch biosample metadata for each accession
def fetch_biosample_metadata(session, accession, headers):
    biosample_url = f"https://www.encodeproject.org/biosample/{accession}/?format=json"
    response = fetch_with_retries_41(session, biosample_url, headers, params=None)
    return response.json()

# Main function to fetch biosample metadata
def fetch_biosamples_metadata():
    print("Fetching ENCODE biosamples metadata...")
    
    session = create_session_with_retries()
    base_url = 'https://www.encodeproject.org/search/'
    headers = {'accept': 'application/json'}
    limit = 100 
    
    # Fetch the first page to get the total number of biosamples
    initial_response = session.get(base_url, headers=headers, params={"type": "Biosample", "format": "json", "limit": 1})
    initial_data = initial_response.json()
    total_hits = initial_data.get("total", 0)
    
    if total_hits == 0:
        print("No biosamples found.")
        return [], 500
    
    total_pages = (total_hits // limit) + 1
    biosample_ids = []

    # Fetch biosample IDs concurrently using ThreadPoolExecutor
    with open("metadata/biosample_ids.txt", "a") as file:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(fetch_biosamples_page, session, base_url, headers, page, limit)
                for page in range(total_pages)
            ]

            for future in tqdm(as_completed(futures), total=total_pages, desc="Fetching biosample IDs", unit="page"):
                hits = future.result()
                process_biosample_hits(hits, file, biosample_ids)

    print(f"Total Biosample IDs retrieved: {len(biosample_ids)}")

    biosample_data_list = []
    metadata_filename = "metadata/encode_biosamples.txt"

    # Fetch biosample metadata concurrently using ThreadPoolExecutor
    with open(metadata_filename, 'w') as file:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_accession = {
                executor.submit(fetch_biosample_metadata, session, accession, headers): accession
                for accession in biosample_ids
            }

            for future in tqdm(as_completed(future_to_accession), total=len(biosample_ids), desc="Fetching biosample metadata", unit="biosample"):
                accession = future_to_accession[future]
                try:
                    metadata = future.result()
                    biosample_data_list.append(metadata)
                    file.write(json.dumps(metadata, indent=4) + '\n')
                except Exception as exc:
                    print(f"Error fetching metadata for biosample {accession}: {exc}")

    return biosample_data_list, 200

### FETCH THE WHOLE ENCODE EXPERIMENTS DB ###

# Function to fetch a single page of experiments
def fetch_experiments_page(session, base_url, headers, page, limit):
    params = {
        "type": "Experiment",
        "format": "json",
        "frame": "object",
        "limit": limit,
        "from": page * limit
    }
    response = fetch_with_retries_41(session, base_url, headers, params=params)
    return response.json().get("@graph", [])

# Function to process and store the experiment IDs (accessions)
def process_experiment_hits(hits, file, experiment_ids):
    for hit in hits:
        accession = hit.get("accession", "")
        if accession:
            experiment_ids.append(accession)
            file.write(accession + "\n")

# Function to fetch experiment metadata for each accession
def fetch_experiment_metadata(session, accession, headers):
    experiment_url = f"https://www.encodeproject.org/experiments/{accession}/?format=json"
    response = fetch_with_retries_41(session, experiment_url, headers, params=None)
    return response.json()

# Main function to fetch experiment metadata
def fetch_experiments_metadata():
    print("Fetching ENCODE experiments metadata...")
    
    session = create_session_with_retries()
    base_url = 'https://www.encodeproject.org/search/'
    headers = {'accept': 'application/json'}
    limit = 100 
    
    # Fetch the first page to get the total number of experiments
    initial_response = session.get(base_url, headers=headers, params={"type": "Experiment", "format": "json", "limit": 1})
    initial_data = initial_response.json()
    total_hits = initial_data.get("total", 0)
    
    if total_hits == 0:
        print("No experiments found.")
        return [], 500
    
    total_pages = (total_hits // limit) + 1
    experiment_ids = []

    # Fetch experiment IDs concurrently using ThreadPoolExecutor
    with open("metadata/experiment_ids.txt", "a") as file:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(fetch_experiments_page, session, base_url, headers, page, limit)
                for page in range(total_pages)
            ]

            for future in tqdm(as_completed(futures), total=total_pages, desc="Fetching experiment IDs", unit="page"):
                hits = future.result()
                process_experiment_hits(hits, file, experiment_ids)

    print(f"Total Experiment IDs retrieved: {len(experiment_ids)}")

    experiment_data_list = []
    metadata_filename = "metadata/encode_experiments.txt"

    # Fetch experiment metadata concurrently using ThreadPoolExecutor
    with open(metadata_filename, 'w') as file:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_accession = {
                executor.submit(fetch_experiment_metadata, session, accession, headers): accession
                for accession in experiment_ids
            }

            for future in tqdm(as_completed(future_to_accession), total=len(experiment_ids), desc="Fetching experiment metadata", unit="experiment"):
                accession = future_to_accession[future]
                try:
                    metadata = future.result()
                    experiment_data_list.append(metadata)
                    file.write(json.dumps(metadata, indent=4) + '\n')
                except Exception as exc:
                    print(f"Error fetching metadata for experiment {accession}: {exc}")

    return experiment_data_list, 200

### FETCH THE WHOLE GDC DB ###
# Fetch a single page of file IDs
def fetch_file_ids(session, files_endpt, page, page_size):
    params = {
        "size": page_size,
        "from": (page - 1) * page_size
    }
    response = fetch_with_retries(session, files_endpt, params=params)
    return response.json().get("data", {}).get("hits", [])

# Process and collect file IDs
def process_file_hits(hits, file_ids):
    for hit in hits:
        file_ids.append(hit.get("id", ""))

# Fetch all file IDs using pagination and concurrency
def fetch_gdc_file_ids(session, files_endpt, page_size=100, start_page=1):
    # Fetch the first page to get the total number of files
    initial_response = session.get(files_endpt, params={"size": 1})
    initial_data = initial_response.json()
    total_hits = initial_data.get("data", {}).get("pagination", {}).get("total", 0)

    if total_hits == 0:
        print("No files found.")
        return []

    total_pages = (total_hits // page_size) + 1
    file_ids = []

    # Fetch all pages of file IDs concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(fetch_file_ids, session, files_endpt, page, page_size)
            for page in range(start_page, total_pages + 1)
        ]

        for future in tqdm(as_completed(futures), total=total_pages - start_page + 1, desc="Fetching file IDs", unit="page"):
            hits = future.result()
            process_file_hits(hits, file_ids)

    print(f"Total File IDs retrieved: {len(file_ids)}")
    return file_ids

# Fetch a single file's metadata
def fetch_file_metadata(session, file_id):
    url = f'https://api.gdc.cancer.gov/files/{file_id}'
    params = {'pretty': 'true'}
    response = fetch_with_retries(session, url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metadata for file ID {file_id} with status code {response.status_code}")
        return None

# Main function to fetch GDC metadata
def fetch_gdc_metadata():
    """
    Fetch metadata from the Genomic Data Commons (GDC) repository.

    Parameters:
    - keywords (list): List of keywords to filter metadata (currently not used).

    Returns:
    - metadata_list (list): List of metadata records.
    - request_status (int): HTTP request status code.
    - url (str): URL of the repository.
    """
    print("Fetching GDC metadata...")
    session = create_session_with_retries()
    files_endpt = "https://api.gdc.cancer.gov/files"
    page_size = 100 
    start_page = 1 

    # Fetch file IDs concurrently
    file_ids = fetch_gdc_file_ids(session, files_endpt, page_size, start_page)

    # If no file IDs were retrieved, return early
    if not file_ids:
        print("No file IDs retrieved. Exiting.")
        return None, 500  

    metadata_list = []
    filename = "metadata/gdc_metadata.json"

    # Fetch metadata for each file concurrently using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:  
        future_to_file = {
            executor.submit(fetch_file_metadata, session, file_id): file_id 
            for file_id in file_ids
        }

        with open(filename, 'w') as file:
            for future in as_completed(future_to_file):
                file_id = future_to_file[future]
                try:
                    metadata = future.result()
                    if metadata:
                        metadata_list.append(metadata)
                        file.write(json.dumps(metadata, indent=4) + '\n')
                except Exception as exc:
                    print(f"File ID {file_id} generated an exception: {exc}")

    return metadata_list, 200

### UNFORTUNATELY, THE ICGC API CLOSED DURING THE WRITING OF OUR THESIS ###
def fetch_icgc_metadata():
    pass