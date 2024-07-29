import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import json
import requests
import re
import pandas as pd


# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Set display width to show the entire dataframe without truncation
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)


def check_format(metadata_list):

    """
    Check the format of the input string to determine if it's in a known interoperable format.

    Args:
        metadata_list (str or list): The input string or list to check the format of.

    Returns:
        int: 1 if the format is recognized as interoperable (e.g., json, xml, owl, etc.), 0 otherwise.
    """

    META = "(Meta)data is in format: "
    if type(metadata_list) == dict:
        metadata_list = input_str["biosamples"]

    score = 0
    for input_str in metadata_list:
        try:
            if isinstance(input_str, Element) or isinstance(input_str, dict):
                print(META + "json")
                score += 1
                continue
        except:
            pass
        try:
            json.loads(input_str)
            print(META + "json")
            score += 1
            continue
        except ValueError:
            pass
        try:
            ET.fromstring(input_str)
            print(META + "xml")
            score += 1
            continue
        except ET.ParseError:
            pass
        try:
            if "owl:" in input_str or "http://www.w3.org/2002/07/owl#" in input_str:
                print(META + "owl")
                score += 1
                continue
            if "[Term]" in input_str or "[Typedef]" in input_str:
                print(META + "OBO")
                score += 1
                continue
            if "@prefix" in input_str or "<http://www.w3.org/1999/02/22-rdf-syntax-ns#" in input_str:
                print(META + "RDF")
                score += 1
                continue
            if "@context" in input_str:
                print(META + "JSON-LD")
                score += 1
                continue
            if "@prefix" in input_str or "<http://www.w3.org/1999/02/22-rdf-syntax-ns#" in input_str:
                print(META + "Turtle (TTL)")
                score += 1
                continue
            if "<http://" in input_str or "@prefix" in input_str:
                print(META + "N-Triples")
                score += 1
                continue
        except:
            pass

    return score / len(metadata_list)


def check_ontology(metadata, repository_choice):

    """
    Check the ontology used in the metadata for different repository choices.

    Args:
        metadata (list or dict): The metadata to check for ontology usage.
        repository_choice (str): The choice of repository to determine specific checks.

    Returns:
        float: The proportion of valid ontology usage based on the repository choice.
    """

    count = 0
    zeros = 0
    ones = 0

    if repository_choice == "6":
        samples = 0
        for hit in metadata:
            mutation_id = hit["id"]
            url = f'https://dcc.icgc.org/api/v1/projects/{mutation_id}/mutations?filters=%7B%7D&from=1&size=1&sort=affectedDonorCountFiltered&order=desc'
            response = requests.get(url)
            data = response.json()
            if response.status_code == 200:
                for ont in data["hits"][0]["clinical_evidence"].keys():
                    try:
                        for disease in data["hits"][0]["clinical_evidence"][ont]:
                            try:
                                query = disease["disease"]
                                samples += 1
                                if samples > 10:
                                    break
                                if search_bioportal(query, ont):
                                    count += 1
                                else:
                                    zeros += 1                            
                            except:
                                continue
                    except:
                        continue
        ones = count
        zeros = samples - ones
        print("#ZEROS: " + str(zeros))
        print("#ONES: " + str(ones))
        return count / samples

    if repository_choice == "5":
        # no ontology mentioned
        return 0

    if repository_choice == "4":
        for hit in metadata["biosamples"]:
            ontology_id = hit["biosample_ontology"]
            pattern = r'(?<=_)[A-Z]+(?=_)'
            match = re.search(pattern, ontology_id)
            if match:
                ontology = match.group(0)
                count += 1
        ones = count
        zeros = len(metadata) - ones
        print("#ZEROS: " + str(zeros))
        print("#ONES: " + str(ones))
        return count / len(metadata)

    if repository_choice == "3":
        for hit in metadata:
            ontology_score = 0
            ontology_link = hit["_links"]["efoTraits"]["href"]
            r_repo = requests.get(ontology_link)
            response_data = r_repo.json()
            if response_data:
                ontology_score += 1
            manufacturer = hit["platforms"][0]["manufacturer"]
            genotypingTechnology = hit["genotypingTechnologies"][0]["genotypingTechnology"]
            trait = hit["diseaseTrait"]["trait"]
            if search_bioportal(manufacturer, "EFO"):
                ontology_score += 1
            if search_bioportal(genotypingTechnology, "EFO"):
                ontology_score += 1
            if search_bioportal(trait, "EFO"):
                ontology_score += 1
            count += ontology_score / 4 
        ones = count
        zeros = len(metadata) - ones
        print("#ZEROS: " + str(zeros))
        print("#ONES: " + str(ones))
        return count / len(metadata)

    if repository_choice == "2":
        # no ontology mentioned
        return 0

    if repository_choice == "1":
        o_name_list = []
        o_id_list = []
        o_of_name = []
        o_of_value = []
        try:
            for term in metadata:
                term = term["section"]["attributes"]
                try:
                    ontology_name = term["valqual"][0]["value"]
                    ontology_id = term["valqual"][1]["value"]
                    ontology_of_name = term["name"]
                    ontology_of_value = term["value"]

                    o_name_list.append(ontology_name)
                    o_id_list.append(ontology_id)
                    o_of_name.append(ontology_of_name)
                    o_of_value.append(ontology_of_value)
                except:
                    continue
            for term in metadata["section"]["subsections"][0]:
                try:
                    ontology_name = term["attributes"][1]["valqual"][0]["value"]
                    ontology_id = term["attributes"][1]["valqual"][1]["value"]
                    ontology_of_name = term["attributes"][1]["name"]
                    ontology_of_value = term["attributes"][1]["value"]
                    o_name_list.append(ontology_name)
                    o_id_list.append(ontology_id)
                    o_of_name.append(ontology_of_name)
                    o_of_value.append(ontology_of_value)
                except:
                    continue
        except:
            o_name_list.append(0)
            o_id_list.append(0)
            o_of_name.append(0)
            o_of_value.append(0)

        return o_name_list, o_id_list, o_of_name, o_of_value


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
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        ontologies = response.json()
        ontology_info = [(ontology["name"], ontology["acronym"]) for ontology in ontologies]
        for i in ontology_info:
            if i[1] == ontology_name:
                return 1
        return 0
    else:
        print("Error:", response.status_code)

        return None


def find_other_metadata_references(metadata):
    uri_regex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    metadata_str = str(metadata)
    if uri_regex.search(metadata_str):
        score = 1
        explanation = "Metadata include qualified references to other (meta)data"
    else:
        score = 0
        explanation = "Metadata do not include qualified references to other (meta)data: there is no URI in the (meta)data that would represent an entity."
    return score, explanation


def I1(metadata):

    """
    Evaluate the interoperability principle I1 by checking the format of metadata.

    Args:
        metadata (str or list): The metadata to check the format of.

    Returns:
        int: 1 if the format is recognized as interoperable, 0 otherwise.
    """

    score = check_format(metadata)
    df = pd.DataFrame({
        "Principle": ["I1"],
        "Description": ["Interoperability: Format check"],
        "Score": [score],
        "Explanation": ["Format is interoperable" if score else "Format is not interoperable: the format of the (meta)data is not one of the following: json, xml, json-ld, owl, obo, rdf, ttl, or n-triples."]
    })
    print(df.head())

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

    score = check_ontology(metadata, repository_choice)
    df = pd.DataFrame({
        "Principle": ["I2"],
        "Description": ["Interoperability: Ontology check"],
        "Score": [score],
        "Explanation": ["Ontology is used and valid" if score else "Ontology is not valid: the ontology that is used is not present on the BioPortal or not used at all."]
    })
    print(df.head())

    return score


def I3(metadata):

    """
    Evaluate the interoperability principle I3 by checking for qualified references in metadata.

    Args:
        metadata (str or list): The metadata to check for qualified references.

    Returns:
        int: 1 if qualified references are found, 0 otherwise.
    """

    score, explanation = find_other_metadata_references(metadata)
    df = pd.DataFrame({
        "Principle": ["I3"],
        "Description": ["Interoperability: Metadata include qualified references to other (meta)data"],
        "Score": [score],
        "Explanation": [explanation]
    })
    print(df.head())

    return score