import xml.etree.ElementTree as ET
import requests  
import xml.etree.ElementTree as ET
import requests
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from time import sleep
import logging
import random
from datetime import datetime
from tqdm import tqdm
import json


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
                # Check if the element is present and has a non-empty value
                if element is not None and element.text.strip():
                    present_fields.add(field)
                else:
                    missing_fields_count[field] += 1

            if len(present_fields) == len(fields):
                all_required_count += 1
            if len(present_fields) == 0:
                missing_all_count += 1

        except ET.ParseError:
            print("Error parsing XML:", xml_str)
    
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


def fetch_summary_ae(summary_api, record_ids):
    """Fetches summaries for a list of records with retries."""
    summary_api += record_ids
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r_summary = requests.get(summary_api, timeout=30)
            print(f"API Call: {r_summary.url}")
            r_summary.raise_for_status()
            root_summary = r_summary.json()
            return root_summary
        except (requests.exceptions.RequestException, ET.ParseError) as e:
            if attempt == max_retries - 1:
                logging.error(f"Error fetching summary for IDs {record_ids}: {e}")
            sleep(2 ** attempt + random.uniform(0, 1)) 
    return None

def fetch_batch_ae(retstart, params, repository_api, summary_api):
    """Fetches a batch of records from the repository with retries."""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            batch_metadata = []
            for i in range(0, len(retstart)):
                id_group = retstart[i]
                root_summary = fetch_summary_ae(summary_api, id_group)
                if root_summary is not None:
                    batch_metadata.append(root_summary)
                sleep(0.1)  
            return batch_metadata
        except (requests.exceptions.RequestException, ET.ParseError) as e:
            if attempt == max_retries - 1:
                logging.error(f"Error fetching batch starting at {retstart}: {e}")
            sleep(2 ** attempt + random.uniform(0, 1)) 
    return None

def fetch_ae_metadata(start_batch=0):
    """Main function to fetch AE metadata."""
    repository_api = "https://www.ebi.ac.uk/biostudies/api/v1/search"
    summary_api = "https://www.ebi.ac.uk/biostudies/api/v1/studies/"
    params = {"pageSize": 500}
    metadata_list = []
    r_repo = requests.get(repository_api, params=params)
    print(f"API Call: {r_repo.url}")
    request_status = r_repo.status_code
    response_data = r_repo.json()
    hits = response_data.get("hits", [])
    experiment_ids = []
    for hit in hits:
        accession = hit.get("accession", "")
        if len(accession) == 11:
            experiment_ids.append(accession)
            print(accession)
    total_count = len(experiment_ids) 
    print(f"Total Study IDs retrieved: {total_count}")
    filename = "metadata/arrayexpress.txt"
    failed_batches = []
    with open(filename, 'a') as file: 
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(start_batch * 5, 5, total_count):
                retstart = experiment_ids[i:i+5]
                futures.append(executor.submit(fetch_batch_ae, retstart, params.copy(), repository_api, summary_api))
            for future in tqdm(as_completed(futures), total=len(futures), desc='Fetching AE', unit='batch'):
                try:
                    batch_metadata = future.result()
                    if batch_metadata is None:
                        failed_batches.append(future)
                    else:
                        print(batch_metadata)
                        for metadata in batch_metadata:
                            metadata_list.append(metadata)
                            file.write(json.dumps(metadata, indent=4) + '\n')
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
    if failed_batches:
        with open("metadata/failed_batches_ae.txt", "w") as fail_file:
            for future in failed_batches:
                params_with_retstart = future.args[1]
                fail_file.write(f"Failed batch with retstart={params_with_retstart['retstart']} and params={params_with_retstart}\n")
    return metadata_list, request_status

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

def fetch_gwas_metadata():
    pass

def fetch_encode_biosamples_metadata():
    pass

def fetch_encode_experiments_metadata():
    pass

def fetch_gdc_metadata():
    pass

def fetch_icgc_metadata():
    pass