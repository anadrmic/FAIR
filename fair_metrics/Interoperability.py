import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import json
import requests
import re
import utils
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_format(metadata_list):
    """
    Check the format of the input string to determine if it's in a known interoperable format.

    Args:
        metadata_list (str or list): The input string or list to check the format of.

    Returns:
        tuple: (float, str) - Proportion of recognized interoperable formats and the format name.
    """
    META = "(Meta)data is in format: "
    score = 0
    format_detected = ""

    for input_str in metadata_list:
        if is_json(input_str):
            print(META + "json")
            score += 1
            format_detected = "json"
        elif is_xml(input_str):
            print(META + "xml")
            score += 1
            format_detected = "xml"
        elif is_owl(input_str):
            print(META + "owl")
            score += 1
            format_detected = "owl"
        elif is_obo(input_str):
            print(META + "OBO")
            score += 1
            format_detected = "OBO"
        elif is_rdf(input_str):
            print(META + "RDF")
            score += 1
            format_detected = "RDF"
        elif is_json_ld(input_str):
            print(META + "JSON-LD")
            score += 1
            format_detected = "JSON-LD"
        elif is_ttl(input_str):
            print(META + "TTL")
            score += 1
            format_detected = "TTL"
        elif is_ntriples(input_str):
            print(META + "N-Triples")
            score += 1
            format_detected = "N-Triples"
    return score / len(metadata_list), format_detected

def is_json(input_str):
    """Check if input string is JSON format."""
    try:
        if isinstance(input_str, (Element, dict)):
            return True
        json.loads(input_str)
        return True
    except (ValueError, TypeError):
        return False

def is_xml(input_str):
    """Check if input string is XML format."""
    try:
        ET.fromstring(input_str)
        return True
    except ET.ParseError:
        return False

def is_owl(input_str):
    """Check if input string is OWL format."""
    return "owl:" in input_str or "http://www.w3.org/2002/07/owl#" in input_str

def is_obo(input_str):
    """Check if input string is OBO format."""
    return "[Term]" in input_str or "[Typedef]" in input_str

def is_rdf(input_str):
    """Check if input string is RDF format."""
    return "@prefix" in input_str or "<http://www.w3.org/1999/02/22-rdf-syntax-ns#" in input_str

def is_json_ld(input_str):
    """Check if input string is JSON-LD format."""
    return "@context" in input_str

def is_ttl(input_str):
    """Check if input string is Turtle (TTL) format."""
    return "@prefix" in input_str or "<http://www.w3.org/1999/02/22-rdf-syntax-ns#" in input_str

def is_ntriples(input_str):
    """Check if input string is N-Triples format."""
    return "<http://" in input_str or "@prefix" in input_str

def check_ontology(metadata, repository_choice):
    """
    Check the ontology used in the metadata for different repository choices.

    Args:
        metadata (list or dict): The metadata to check for ontology usage.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The proportion of valid ontology usage based on the repository choice.
    """
    if repository_choice == "6":
        return check_ontology_icgc(metadata)
    elif repository_choice == "5":
        return 0
    elif repository_choice[0] == "4":
        return check_ontology_biosamples(metadata)
    elif repository_choice == "3":
        return check_ontology_gwas(metadata)
    elif repository_choice == "2":
        return 0
    elif repository_choice == "1":
        return check_ontology_array_express(metadata)
    else:
        return 0

def check_ontology_icgc(metadata):
    """Check ontology usage for ICGC repository."""
    samples = 0
    count = 0
    for hit in metadata:
        mutation_id = hit["id"]
        url = f'https://dcc.icgc.org/api/v1/projects/{mutation_id}/mutations?filters=%7B%7D&from=1&size=1&sort=affectedDonorCountFiltered&order=desc'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for ont in data["hits"][0]["clinical_evidence"].keys():
                for disease in data["hits"][0]["clinical_evidence"][ont]:
                    query = disease.get("disease", "")
                    samples += 1
                    if samples > 10:
                        break
                    if search_bioportal(query, ont):
                        count += 1
    return count / samples if samples else 0

def check_ontology_biosamples(metadata):
    """Check ontology usage for biosamples repository."""
    count = 0
    for hit in metadata["biosamples"]:
        ontology_id = hit.get("biosample_ontology", "")
        pattern = r'(?<=_)[A-Z]+(?=_)'
        if re.search(pattern, ontology_id):
            count += 1
    return count / len(metadata["biosamples"]) if metadata["biosamples"] else 0

def check_ontology_gwas(metadata):
    """Check ontology usage for GWAS repository."""
    count = 0
    for hit in metadata:
        try:
            ontology_score = 0
            ontology_link = hit["_links"]["efoTraits"]["href"]
            response = requests.get(ontology_link)
            if response.status_code == 200 and response.json():
                ontology_score += 1
            manufacturer = hit["platforms"][0]["manufacturer"]
            genotypingTechnology = hit["genotypingTechnologies"][0]["genotypingTechnology"]
            trait = hit["diseaseTrait"]["trait"]
            for term in [manufacturer, genotypingTechnology, trait]:
                if search_bioportal(term, "EFO"):
                    ontology_score += 1
            count += ontology_score / 4
        except: 
            pass
    return count / len(metadata) if metadata else 0

def check_ontology_array_express(metadata):
    """Check ontology usage for Array Express repository."""
    o_name_list = []
    for term in metadata:
        attributes = term.get("section", {}).get("attributes", [])
        o_name_list.append(extract_ontology_from_attributes(attributes))
    return len(o_name_list) / len(metadata) if metadata else 0

def extract_ontology_from_attributes(attributes):
    """Extract ontology information from a list of attributes."""
    ontology_info = []
    for attr in attributes:
        valqual = attr.get("valqual", [])
        try:
            if valqual:
                ontology_name = valqual[0]["value"]
                ontology_id = valqual[1]["value"]
                ontology_info.extend([ontology_name, ontology_id])
        except (KeyError, IndexError):
            continue
    print(ontology_info)
    return ontology_info


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
def search_bioportal(query, ontology_name):
    """
    Search for a term in BioPortal to check if it exists within a specified ontology.

    Args:
        query (str): The query term to search for.
        ontology_name (str): The name of the ontology to search within.

    Returns:
        int: 1 if the term exists in the ontology, 0 otherwise.
    """
    BASE_URL = "https://data.bioontology.org"
    API_KEY = "da05700b-cb69-49ef-840e-731b6d425aa4"
    url = f"{BASE_URL}/ontologies"
    params = {"q": query}
    headers = {"Authorization": f"apikey token={API_KEY}"}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status() 
        if response.status_code == 200:
            ontologies = response.json()
            for ontology in ontologies:
                if ontology["acronym"] == ontology_name:
                    return 1
            return 0
        else:
            print("Error:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        raise 

def log_interoperability_evaluation(principle, description, score, explanation):
    """
    Log the interoperability evaluation to a file.

    Args:
        principle (str): The principle being evaluated.
        description (str): Description of the evaluation.
        score (float): The score of the evaluation.
        explanation (str): Explanation of the result.
    """
    with open("results/Interoperability.txt", "a") as file:
        file.write(f"\n{principle}: {description}\n")
        file.write(f"{explanation}\n")
        file.write(f"The score is: {score}.\n")

def check_required_fields(metadata, repository_choice):
    """Check for required fields based on repository choice."""
    if repository_choice.startswith("1"):
        return utils.check_required_fields_json(metadata, ["refs"])[0]
    elif repository_choice.startswith("3"):
        return utils.check_required_fields_json(metadata, ["_links"])[0]
    elif repository_choice == "2":
        return utils.check_required_fields_geo(metadata, ["FTPLink"])[0]
    elif repository_choice.startswith("4"):
        return utils.check_required_fields_json(metadata, ["dbxrefs"])[0]
    elif repository_choice.startswith("5"):
        return utils.check_required_fields_json_gdc(metadata, ["refs"])[0]
    elif repository_choice.startswith("6"):
        return utils.check_required_fields_json(metadata, ["refs"])[0]
    else:
        return 0
    

def I1(metadata):
    """
    Evaluate the interoperability principle I1 by checking the format of metadata.

    Args:
        metadata (str or list): The metadata to check the format of.

    Returns:
        int: 1 if the format is recognized as interoperable, 0 otherwise.
    """
    score, format_detected = check_format(metadata)
    log_interoperability_evaluation("I1", "Format check", score, f"The metadata are in standard format: {format_detected}.")
    utils.print_evaluation("I1", "Interoperability: Format check", score, f"Format is {format_detected}.")

    return score

def I2(metadata, repository_choice):
    """
    Evaluate the interoperability principle I2 by checking ontology usage in metadata.

    Args:
        metadata (list or dict): The metadata to check for ontology usage.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The proportion of valid ontology usage based on the repository choice.
    """
    score = check_ontology(metadata, repository_choice)*100
    log_interoperability_evaluation("I2", "Ontology check", score, f"The metadata uses valid ontology terms in {score:.2f}% of entities.")
    utils.print_evaluation("I2", "Interoperability: Ontology check", score, f"Ontology is used and valid in {score:.2f}% of entities.")
    return score/100

def I3(metadata, repository_choice):
    """
    Evaluate the interoperability principle I3 by checking for qualified references in metadata.

    Args:
        metadata (str or list): The metadata to check for qualified references.

    Returns:
        int: 1 if qualified references are found, 0 otherwise.
    """
    all_required_percentage = check_required_fields(metadata, repository_choice)
    score = all_required_percentage / 100
    explanation = f"{all_required_percentage:.2f}% of entities have a reference to other metadata."
    log_interoperability_evaluation("I3", "Qualified references check", score, explanation)
    utils.print_evaluation("I3", "Interoperability: Metadata include qualified references to other (meta)data", score, explanation)
    return score




