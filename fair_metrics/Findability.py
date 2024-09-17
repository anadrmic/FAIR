import requests
from bs4 import BeautifulSoup
import re
import utils
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor, as_completed

def find_doi_in_webpage(url):
    """
    Check for the presence of a DOI (Digital Object Identifier) in a webpage.

    Args:
        url (str): The URL of the webpage to search for a DOI.

    Returns:
        int: 1 if a DOI is found, 0 otherwise.
    """
    if not url:
        return 0

    response = requests.get(url)
    if response.status_code != 200:
        return 0

    soup = BeautifulSoup(response.content, 'html.parser')
    content_before_footer = ' '.join(str(element) for element in soup.find_all(string=True))
    dois = re.findall(r'\b(10\.\d{4,}(?:\.\d+)*\/\S+(?:(?!["&\'<>])\S))\b', content_before_footer)
    if dois:
        return 1, dois
    else:
        return 0, ""


def search_google_datasets(metadata, repository_choice):
    """
    Search for dataset names in Google Dataset Search and calculate the percentage found.

    Args:
        metadata (list of dict): Metadata containing dataset names.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: The percentage of dataset names found in Google Dataset Search.
    """
    dataset_name_list = extract_dataset_names(metadata, repository_choice)
    if not dataset_name_list:
        return 0.0

    count = 0
    for dataset_name in dataset_name_list:
        if search_dataset_on_google(dataset_name):
            count += 1

    return count / len(dataset_name_list) if dataset_name_list else 0.0


def extract_dataset_names(metadata, repository_choice):
    """
    Extract dataset names based on repository choice.

    Args:
        metadata (list of dict): Metadata to extract from.
        repository_choice (str): Identifier for the repository type.

    Returns:
        list: List of dataset names.
    """
    if repository_choice == "1":
        return [hit["attributes"][0]["value"] for hit in metadata]
    elif repository_choice == "2":
        return [utils.xml_to_list(metadata)[0][1][3]]
    elif repository_choice == "3":
        return [hit["publicationInfo"]["title"] for hit in metadata]
    elif repository_choice[0] == "4":
        return [hit.get("description", "") for hit in metadata]
    elif repository_choice == "5":
        return []
    elif repository_choice == "6":
        return [hit.get("name", "") for hit in metadata]
    else:
        return []

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
def search_dataset_on_google(dataset_name):
    """
    Search for a dataset name on Google Dataset Search.

    Args:
        dataset_name (str): The dataset name to search for.

    Returns:
        bool: True if found, False otherwise.
    """
    url = f"https://datasetsearch.research.google.com/search?query={dataset_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return dataset_name.lower() in BeautifulSoup(response.content, 'html.parser').get_text().lower()
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return False

def log_findability_evaluation(principle, description, score, explanation):
    """
    Log the findability evaluation to a file.

    Args:
        principle (str): The principle being evaluated.
        description (str): Description of the evaluation.
        score (float): The score of the evaluation.
        explanation (str): Explanation of the result.
    """
    with open("results/Findability.txt", "a") as file:
        file.write(f"\n{principle}: {description}\n")
        file.write(f"{explanation}\n")
        file.write(f"The score is: {score}.\n")

def get_findability_fields_id(repository_choice):
    """
    Get the id fields based on the repository choice.

    Args:
        repository_choice (str): Identifier for the repository type.

    Returns:
        list: List of id fields.
    """
    findability_fields_dict = {
        "1": ["accno"],
        "2": ["Accession"],
        "3": ["accessionId"],
        "41": ["accession"],
        "42": ["accession"],
        "5": ["file_id"],
        "6": ["icgcId"]
    }
    return findability_fields_dict.get(repository_choice, [])

def get_findability_fields(repository_choice):
    """
    Get the findability fields based on the repository choice.

    Args:
        repository_choice (str): Identifier for the repository type.

    Returns:
        list: List of findability fields.
    """
    findability_fields_dict = {
        "1": ["value"], 
        "2": ["title", "taxon", "gdsType"],
        "3": ["initialSampleSize", "snpCount"],
        "41": ["aliases", "lab", "organism"],
        "42": ["doi", "lab", "organism"],
        "5": ["data_category", "data_type", "data_release"],
        "6": ["primarySite", "icgcId", "ssmTestedDonorCount"]
    }
    return findability_fields_dict.get(repository_choice, [])

def check_required_fields_ae(json_elements):
    total_count = len(json_elements)
    missing_fields_count = {field: 0 for field in ["value"]}
    if total_count == 0:
        return "No JSON elements provided.", 0, 0, {}
    all_required_count = 0
    missing_all_count = 0
    for element in json_elements:
        if element["attributes"][0]["value"]:
            all_required_count += 1
        else:
            missing_all_count += 1
            missing_fields_count["value"] += 1
    all_required_percentage = (all_required_count / total_count) * 100 if total_count > 0 else 0
    missing_all_percentage = (missing_all_count / total_count) * 100 if total_count > 0 else 0
    return all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count


def F1(url):
    """
    Evaluate the findability principle F1 for a given dataset by checking DOI presence in a webpage.

    Args:
        url (str): The URL of the webpage to search for a DOI.

    Returns:
        int: Score indicating DOI presence (1 if found, 0 otherwise).
    """
    score, dois = find_doi_in_webpage(url)
    explanation = (f"The data source has a valid DOI associated with it available at re3data: {dois}."
                   if score else "The data source does not have a valid DOI associated with it available at re3data.")

    log_findability_evaluation("F1", "Evaluating the findability principle F1 for a given data source by checking DOI presence in a webpage.",
                               score, explanation)
    utils.print_evaluation("F1", "Findability: DOI presence in webpage", score, explanation)

    return score

def F2(metadata, repository_choice):
    """
    Evaluate the findability principle F2 for a given dataset by searching for keywords in metadata.

    Args:
        keywords (list of str): List of keywords to search for.
        metadata (list of dict): Metadata to search within.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: Score indicating the percentage of keywords found in the metadata.
    """
    findability_fields = get_findability_fields(repository_choice)
    if repository_choice == "1":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = check_required_fields_ae(metadata)
    elif repository_choice == "2":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_geo(metadata, findability_fields)
    elif repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json_gdc(metadata, findability_fields)
    else:
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, findability_fields)
    score = all_required_percentage/100
    explanation = (f"{all_required_percentage:.2f}% of entities have all required fields ({all_required_count} out of {total_count}).\n"
                   f"{missing_all_percentage:.2f}% of entities are missing some required fields ({missing_all_count} out of {total_count}).\n"
                   "\nBreakdown of missing fields:\n" +
                   "\n".join(f"{count} entities are missing '{field}' field." for field, count in missing_fields_count.items()))
    
    log_findability_evaluation("F2", "Evaluating the findability principle F2 for a given dataset by searching for predefined findability fields in metadata.",
                               score, explanation) 
    utils.print_evaluation("F2", "Findability: Keyword search in metadata", score, explanation) 

    return score

def F3(metadata, repository_choice):
    """
    Evaluate the findability principle F3 for a given dataset by checking for identifiers in metadata.

    Args:
        metadata (list of dict): Metadata to search for identifiers.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: Score indicating the percentage of entries containing the identifier.
    """

    findability_fields = get_findability_fields_id(repository_choice)
    if repository_choice == "2":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_geo(metadata, findability_fields)
    elif repository_choice == "5":
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json_gdc(metadata, findability_fields)
    else:
        all_required_percentage, missing_all_percentage, missing_fields_count, all_required_count, total_count, missing_all_count = utils.check_required_fields_json(metadata, findability_fields)
    score = all_required_percentage/100
    explanation = (f"{all_required_percentage:.2f}% of entities have an ID field ({all_required_count} out of {total_count}).\n"
                   f"{missing_all_percentage:.2f}% of entities are missing the ID field ({missing_all_count} out of {total_count}).")
    score = all_required_percentage/100
    log_findability_evaluation("F3", "Evaluating the findability principle F3 for a given dataset by checking for identifiers in metadata.",
                               score, explanation)
    utils.print_evaluation("F3", "Findability: Check for identifiers", score, explanation)

    return score


def F4(metadata, repository_choice):
    """
    Evaluate the findability principle F4 for a given dataset by checking for presence in Google Dataset Search.

    Args:
        metadata (list of dict): Metadata containing dataset names.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: Score indicating the percentage of dataset names found in Google Dataset Search.
    """
    score = round(search_google_datasets(metadata, repository_choice), 2)
    explanation = f"Datasets found in Google Dataset Search: {score * 100}%"

    utils.print_evaluation("F4", "Findability: Presence in Google Datasets", score, explanation)

    return score
