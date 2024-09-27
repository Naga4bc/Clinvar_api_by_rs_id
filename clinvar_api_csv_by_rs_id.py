import pandas as pd
import requests

"""
@authour:Nagaraj
@guidance:Prabir

it will print the Clinvar ids wait for few mins

"""
def get_clinvar_accession_and_description_from_dbsnp(rs_id):
    # Construct the entrez query URL to search ClinVar with rsID
    query_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={rs_id}[snp]&retmode=json"
    response = requests.get(query_url)
    data = response.json()
    results = []

    # Check if IDs were found
    id_list = data['esearchresult']['idlist']
    if id_list:
        for clinvar_id in id_list:
            detail_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={clinvar_id}&retmode=json"
            detail_response = requests.get(detail_url)
            detail_data = detail_response.json()
            record = detail_data['result'][clinvar_id]
            description = record.get('germline_classification', {}).get('description', 'No description available')
            accession = record.get('accession', 'No accession available')
            results.append({'description': description, 'accession': accession})
    else:
        results.append({'description': 'No description available', 'accession': 'No accession available'})

    return results

def process_csv(filename):
    # Load the CSV file
    df = pd.read_csv(filename)
    # Iterate over the dbSNP IDs in the "dbsnp" column
    results = {}
    for rs_id in df['dbsnp'].dropna().unique():
        clinvar_info = get_clinvar_accession_and_description_from_dbsnp(rs_id)
        results[rs_id] = clinvar_info
    return results

filename = "clinvar_api_test_27_09_24.csv"
clinvar_results = process_csv(filename)
for rs_id, info in clinvar_results.items():
    print(f"{rs_id}: {info}")
