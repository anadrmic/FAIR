import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import utils


# Set display options to show all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Set display width to show the entire dataframe without truncation
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)


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
    footer = soup.find('footer')
    content_before_footer = [element for element in soup.descendants if element != footer]
    content_before_footer_str = ' '.join(map(str, content_before_footer))
    dois = re.findall(r'\b(10\.\d{4,}(?:\.\d+)*\/\S+(?:(?!["&\'<>])\S))\b', content_before_footer_str)

    return 1 if dois else 0


def search_keywords_and_output_percentage(keywords, metadata, repository_choice):
    
    """
    Search for keywords in metadata and calculate the percentage of matches.

    Args:
        keywords (list of str): List of keywords to search for.
        metadata (list of dict): Metadata to search within.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: The percentage of keywords found in the metadata.
    """
    
    if not keywords:
        return False

    if repository_choice in {"1", "3", "4", "5", "6"}:
        count = 0
        zeros, ones = 0, 0
        for hit in metadata:
            found_keywords = {keyword.lower() for keyword in keywords if keyword.lower() in ' '.join(str(value).lower() for value in hit.values())}
            percentage_found = (len(found_keywords) / len(keywords)) * 100
            zeros += int(percentage_found == 0)
            ones += int(percentage_found == 100)
            count += percentage_found / 100
        
        print(f"#ZEROS: {zeros}")
        print(f"#ONES: {ones}")
        return count / len(metadata)
    
    else:
        output, _ = utils.find_list_in_list(metadata, keywords)
        found = list(set(output))
        percentage_found = (len(found) / len(keywords)) * 100 if found else 0
        return percentage_found / 100


def metadata_completeness(metadata_list, repository_choice):

    """
    Assess the richness of the metadata provided.

    Args:
        metadata_list (list): Metadata list to be assessed.

    Returns:
        float: F2 score based on the richness of metadata.
    """

    if repository_choice == "1":

        required_fields = [
            "Title", "ReleaseDate", "Organism", "Description", "Study type", "Protocols"
        ]

        protocol_required_fields = ["Name", "Type", "Description"]

        total = 0
        for hit in metadata_list:
            score = 0
            max_score = 10

            attributes = hit.get('attributes', [])
            section = hit.get('section', {})
            section_attributes = section.get('attributes', [])
            subsections = section.get('subsections', [])

            for field in required_fields:
                if any(attr.get('name') == field for attr in attributes) or \
                   any(attr.get('name') == field for attr in section_attributes):
                    score += 1

            for subsection in subsections:
                for sub in subsection:
                    if sub.get('type') == 'Protocols':
                        sub_attrs = sub.get('attributes', [])
                        for proto_field in protocol_required_fields:
                            if any(attr.get('name') == proto_field for attr in sub_attrs):
                                score += 1

            normalized_score = score / max_score
            total += normalized_score
        return total/len(metadata_list)

    if repository_choice == "2":
        required_fields = [
            "Accession", "title", "summary", "taxon", "entryType", "gdsType", "PDAT", "suppFile", "Samples"
        ]

        output, _ = utils.find_list_in_list(metadata_list, required_fields)
        found = list(set(output))
        percentage_found = (len(found) / len(required_fields)) * 100 if found else 0
        return percentage_found / 100

    if repository_choice == "3":
        required_fields = [
            "initialSampleSize", "gxe", "gxg", "snpCount", "accessionId", "fullPvalueSet",
            "platforms", "ancestries", "diseaseTrait", "genotypingTechnologies",
            "replicationSampleSize", "publicationInfo"
        ]

        ancestry_required_fields = [
            "type", "numberOfIndividuals", "ancestralGroups", "countryOfRecruitment"
        ]

        publication_required_fields = [
            "pubmedId", "publicationDate", "publication", "title", "author"
        ]

        author_required_fields = [
            "fullname", "orcid"
        ]

        max_score = len(required_fields) + len(ancestry_required_fields) + len(publication_required_fields) + len(
            author_required_fields)

        scores = []

        for metadata in metadata_list:
            score = 0
            for field in required_fields:
                if field in metadata and metadata[field]:
                    score += 1
            if "platforms" in metadata and isinstance(metadata["platforms"], list):
                for platform in metadata["platforms"]:
                    if "manufacturer" in platform:
                        score += 1
            if "ancestries" in metadata and isinstance(metadata["ancestries"], list):
                for ancestry in metadata["ancestries"]:
                    for ancestry_field in ancestry_required_fields:
                        if ancestry_field in ancestry and ancestry[ancestry_field]:
                            score += 1
            if "diseaseTrait" in metadata and metadata["diseaseTrait"]:
                if "trait" in metadata["diseaseTrait"]:
                    score += 1
            if "genotypingTechnologies" in metadata and isinstance(metadata["genotypingTechnologies"], list):
                for technology in metadata["genotypingTechnologies"]:
                    if "genotypingTechnology" in technology:
                        score += 1
            if "publicationInfo" in metadata and metadata["publicationInfo"]:
                for pub_field in publication_required_fields:
                    if pub_field in metadata["publicationInfo"] and metadata["publicationInfo"][pub_field]:
                        score += 1
                if "author" in metadata["publicationInfo"] and metadata["publicationInfo"]["author"]:
                    for author_field in author_required_fields:
                        if author_field in metadata["publicationInfo"]["author"] and metadata["publicationInfo"]["author"][author_field]:
                            score += 1
            normalized_score = score / max_score
            scores.append(normalized_score)
        return scores

    if repository_choice == "4":
        required_fields = [
            "accession", "aliases", "schema_version", "status", "lab", "award",
            "date_created", "submitted_by", "documents", "references", "source",
            "biosample_ontology", "genetic_modifications", "alternate_accessions",
            "treatments", "dbxrefs", "donor", "organism", "internal_tags", "part_of",
            "nih_institutional_certification", "@id", "@type", "uuid", "sex", "age",
            "health_status", "life_stage", "applied_modifications", "characterizations",
            "parent_of", "origin_batch", "perturbed", "simple_summary", "summary"
        ]

        max_score = len(required_fields)
        scores = []

        for metadata in metadata_list:
            score = 0

            for field in required_fields:
                if field in metadata and metadata[field]:
                    score += 1

            normalized_score = score / max_score
            scores.append(normalized_score)
        return scores

    if repository_choice == "5":
        required_fields = [
            "data_format", "access", "file_name", "submitter_id", "data_category",
            "acl", "type", "file_size", "created_datetime", "md5sum",
            "updated_datetime", "file_id", "data_type", "state",
            "experimental_strategy", "version", "data_release"
        ]

        max_score = len(required_fields)

        scores = []

        for metadata in metadata_list:
            data = metadata.get('data', {})
            score = 0

            for field in required_fields:
                if field in data and data[field]:
                    score += 1

            normalized_score = score / max_score
            scores.append(normalized_score)
        return scores

    if repository_choice == "6":
        required_fields = [
            "id", "icgcId", "primarySite", "name", "tumourType", "tumourSubtype",
            "pubmedIds", "primaryCountries", "partnerCountries", "availableDataTypes",
            "ssmTestedDonorCount", "cnsmTestedDonorCount", "stsmTestedDonorCount",
            "sgvTestedDonorCount", "methSeqTestedDonorCount", "methArrayTestedDonorCount",
            "expSeqTestedDonorCount", "expArrayTestedDonorCount", "pexpTestedDonorCount",
            "mirnaSeqTestedDonorCount", "jcnTestedDonorCount", "totalDonorCount",
            "totalLiveDonorCount", "repository", "state"
        ]

        max_score = len(required_fields)

        scores = []

        for metadata in metadata_list:
            score = 0

            for field in required_fields:
                if field in metadata and metadata[field]:
                    score += 1

            normalized_score = score / max_score
            scores.append(normalized_score)

        return scores


def check_for_id(metadata_list, repository_choice):
    
    """
    Check for specific identifiers in the metadata based on the repository choice.

    Args:
        metadata_list (list of dict): Metadata to search for identifiers.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: The percentage of entries containing the identifier.
    """
    
    if repository_choice == "1":
        count = 0
        for hit in metadata_list:
            try:
                if hit["section"]["attributes"][1]["valqual"][1]["name"] == "TermId":
                    count += 1
            except (IndexError, KeyError, TypeError):
                pass
        print(f"#ZEROS: {len(metadata_list) - count}")
        print(f"#ONES: {count}")

    if repository_choice == "2" and metadata_list[0]:
        for metadata in metadata_list:
            soup = BeautifulSoup(metadata, 'xml')
            id_tag = soup.find('Id')
            if id_tag and id_tag.get_text(strip=True):
                count += 1
        print(f"#ZEROS: {len(metadata_list) - count}")
        print(f"#ONES: {count}")

    if repository_choice == "3":
        count = sum(1 for hit in metadata_list if hit.get("publicationInfo", {}).get("pubmedId"))
        print(f"#ZEROS: {len(metadata_list) - count}")
        print(f"#ONES: {count}")

    if repository_choice == "4":
        count = sum(1 for hit in metadata_list if hit.get("product_id"))
        print(f"#ZEROS: {len(metadata_list) - count}")
        print(f"#ONES: {count}")

    if repository_choice == "5":
        count = sum(1 for hit in metadata_list if hit.get("data", {}).get("file_id"))
        print(f"#ZEROS: {len(metadata_list) - count}")
        print(f"#ONES: {count}")

    if repository_choice == "6":
        count = sum(1 for hit in metadata_list if hit.get("icgcId"))
        print(f"#ZEROS: {len(metadata_list) - count}")
        print(f"#ONES: {count}")

    return count / len(metadata_list)

def search_google_datasets(metadata, repository_choice):
    
    """
    Search for dataset names in Google Dataset Search and calculate the percentage found.

    Args:
        metadata (list of dict): Metadata containing dataset names.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: The percentage of dataset names found in Google Dataset Search.
    """
    
    dataset_name_list = []
    if repository_choice == "1":
        dataset_name_list = [hit["attributes"][0]["value"] for hit in metadata]
    elif repository_choice == "2":
        dataset_name_list = [utils.xml_to_list(metadata)[0][1][3]]
    elif repository_choice == "3":
        dataset_name_list = [hit["publicationInfo"]["title"] for hit in metadata]
    elif repository_choice == "4":
        dataset_name_list = [hit.get("description", "") for hit in metadata]
    elif repository_choice == "5":
        dataset_name_list = ["" for _ in metadata]
    elif repository_choice == "6":
        dataset_name_list = [hit.get("name", "") for hit in metadata]

    count = 0
    zeros, ones = 0, 0
    for dataset_name in dataset_name_list:
        url = f"https://datasetsearch.research.google.com/search?query={dataset_name}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            if dataset_name.lower() in BeautifulSoup(response.content, 'html.parser').get_text().lower():
                count += 1
                ones += 1
            else:
                zeros += 1
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)
            return None
        
    print(f"#ZEROS: {zeros}")
    print(f"#ONES: {ones}")
    return count / len(dataset_name_list)


def F1(url):

    """
    Evaluate the findability principle F1 for a given dataset by checking DOI presence in a webpage.

    Args:
        url (str): The URL of the webpage to search for a DOI.

    Returns:
        int: Score indicating DOI presence (1 if found, 0 otherwise).
    """

    score = find_doi_in_webpage(url)
    df = pd.DataFrame({
        "Principle": ["F1"],
        "Description": ["Findability: DOI presence in webpage"],
        "Score": [score],
        "Explanation": ["DOI found on re3data" if score else "DOI not found on re3data: DOI not found on re3data for the specified repository with a corresponding URL."]
    })
    print(df.head())

    return score


def F2(keywords, metadata, repository_choice):

    """
    Evaluate the findability principle F2 for a given dataset by searching for keywords in metadata.

    Args:
        keywords (list of str): List of keywords to search for.
        metadata (list of dict): Metadata to search within.
        repository_choice (str): Identifier for the repository type.

    Returns:
        float: Score indicating the percentage of keywords found in the metadata.
    """

    score = search_keywords_and_output_percentage(keywords, metadata, repository_choice)
    if not score:
        metadata_completeness(metadata, repository_choice)
    df = pd.DataFrame({
        "Principle": ["F2"],
        "Description": ["Findability: Keyword search in metadata"],
        "Score": [score],
        "Explanation": [f"Keywords found with percentage: {score * 100}"]
    })
    print(df.head())

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

    score = check_for_id(metadata, repository_choice)
    df = pd.DataFrame({
        "Principle": ["F3"],
        "Description": ["Findability: Check for identifiers"],
        "Score": [score],
        "Explanation": [f"Identifiers found in {score * 100}% of entries"]
    })
    print(df.head())

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

    score = search_google_datasets(metadata, repository_choice)
    df = pd.DataFrame({
        "Principle": ["F4"],
        "Description": ["Findability: Presence in Google Datasets"],
        "Score": [score],
        "Explanation": [f"Datasets found in Google Dataset Search: {score * 100}%"]
    })
    print(df.head())

    return score
