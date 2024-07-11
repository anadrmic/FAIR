import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import Utils

def find_doi_in_webpage(url):
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
    if not keywords:
        return 1

    if repository_choice == "1":
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
    
    if repository_choice == "2":
        output, _ = Utils.find_list_in_list(metadata, keywords)
        found = list(set(output))
        percentage_found = (len(found) / len(keywords)) * 100 if found else 0
        return percentage_found / 100

    if repository_choice in {"3", "4", "5", "6"}:
        return 1

def check_for_id(dictionary, repository_choice):
    if repository_choice == "1":
        count = 0
        for hit in dictionary:
            try:
                if hit["section"]["attributes"][1]["valqual"][1]["name"] == "TermId":
                    count += 1
            except (IndexError, KeyError, TypeError):
                pass
        print(f"#ZEROS: {len(dictionary) - count}")
        print(f"#ONES: {count}")
        return count / len(dictionary)
    
    if repository_choice == "2" and dictionary[0]:
        return 1
    
    if repository_choice == "3":
        count = sum(1 for hit in dictionary if hit.get("publicationInfo", {}).get("pubmedId"))
        print(f"#ZEROS: {len(dictionary) - count}")
        print(f"#ONES: {count}")
        return count / len(dictionary)
    
    if repository_choice == "4":
        count = sum(1 for hit in dictionary if hit.get("product_id"))
        print(f"#ZEROS: {len(dictionary) - count}")
        print(f"#ONES: {count}")
        return count / len(dictionary)
    
    if repository_choice == "5":
        count = sum(1 for hit in dictionary if hit.get("data", {}).get("file_id"))
        print(f"#ZEROS: {len(dictionary) - count}")
        print(f"#ONES: {count}")
        return count / len(dictionary)

    if repository_choice == "6":
        count = sum(1 for hit in dictionary if hit.get("icgcId"))
        print(f"#ZEROS: {len(dictionary) - count}")
        print(f"#ONES: {count}")
        return count / len(dictionary)

    return 0

def search_google_datasets(metadata, repository_choice):
    dataset_name_list = []
    if repository_choice == "1":
        dataset_name_list = [hit["attributes"][0]["value"] for hit in metadata]
    elif repository_choice == "2":
        dataset_name_list = [Utils.xml_to_list(metadata)[0][1][3]]
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
    score = find_doi_in_webpage(url)
    df = pd.DataFrame({
        "Principle": ["F1"],
        "Description": ["Findability: DOI presence in webpage"],
        "Score": [score],
        "Explanation": ["DOI found in webpage" if score else "DOI not found in webpage: DOI not found on re3data for the specified repository."]
    })
    print(df.head())
    return score

def F2(keywords, metadata, repository_choice):
    score = search_keywords_and_output_percentage(keywords, metadata, repository_choice)
    df = pd.DataFrame({
        "Principle": ["F2"],
        "Description": ["Findability: Keyword search in metadata"],
        "Score": [score],
        "Explanation": [f"Keywords found with percentage: {score * 100}"]
    })
    print(df.head())
    return score

def F3(metadata, repository_choice):
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
    score = search_google_datasets(metadata, repository_choice)
    df = pd.DataFrame({
        "Principle": ["F4"],
        "Description": ["Findability: Presence in Google Datasets"],
        "Score": [score],
        "Explanation": [f"Datasets found in Google Dataset Search: {score * 100}%"]
    })
    print(df.head())
    return score
