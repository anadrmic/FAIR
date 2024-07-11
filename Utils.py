import requests
from ftplib import FTP

def pretty_print_xml (root): 
    count = 0
    for i in range (0, len(root)):
        if len(root[i]) == 0:
            print ("<"  + str(root[i].tag) + ">")
            print ("   " + str(root[i].text))
            count = count + 1
        else: 
            for j in range(0, len(root[i])):
                if len(root[i][j]) == 0:
                    print ("<"  + str(root[i][j].tag) + ">")
                    print ("   " + str(root[i][j].text))
                    print ("<"  + str(root[i][j].tag + ">"))
                    count = count + 1
                else: 
                    for k in range (0, len(root[i][j])):
                        print ("  <"  + str(root[i][j][k].tag + ">"))
                        print ("      " + str(root[i][j][k].text))
                        count = count + 1
    return count

def xml_to_list(root): 
    xml_list_tag = []
    xml_list_text = []
    for i in range (0, len(root)):
        if len(root[i]) == 0:
            tag  = str(root[i].tag)
            text = str(root[i].text)
            xml_list_tag.append(tag.lower()) 
            xml_list_text.append(text.lower())
        else: 
            for j in range(0, len(root[i])):
                if len(root[i][j]) == 0:
                    tag  = str(root[i][j].tag)
                    text = str(root[i][j].text)
                    xml_list_tag.append(tag.lower()) 
                    xml_list_text.append(text.lower())
                else: 
                    for k in range (0, len(root[i][j])):
                        tag  = str(root[i][j][k].tag)
                        text = str(root[i][j][k].text)
                        xml_list_tag.append(tag.lower()) 
                        xml_list_text.append(text.lower())
    xml_list = [ xml_list_tag, xml_list_text ]
    return xml_list

def find_list_in_list(long_list, short_list):
    found = []
    index = []
    for i in range(0, len(long_list)):
        for j in range(0, len(short_list)):
            if long_list[i].find(short_list[j]) != -1 :
                found.append(short_list[j])
                index.append(i)
    return found, index

def get_ftp_link(study_accession):
    source_code = study_accession.split("-")[1]
    url = "ftp://ftp.ebi.ac.uk/pub/databases/microarray/data/experiment/" + source_code + f"/{study_accession}/{study_accession}.sdrf.txt"
    return url

def download_file_via_ftp(ftp_link, local_file_path):
    try:
        ftp_parts = ftp_link.split("/")
        ftp_host = ftp_parts[2]
        ftp_path = "/".join(ftp_parts[3:-1])
        with FTP(ftp_host) as ftp:
            ftp.login()
            ftp.cwd(ftp_path)
            with open(local_file_path, "wb") as local_file:
                ftp.retrbinary(f"RETR {ftp_parts[-1]}", local_file.write)
        print("File downloaded successfully.")
    except Exception as e:
        print(f"Error downloading file: {e}")

def get_json_metadata_link(study_accession):
    url = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{study_accession}/info"
    response = requests.get(url)
    data = response.json()
    link = data.get("httpLink") + f"/{study_accession}.json"
    return link