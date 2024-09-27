
"""
@authour:Nagaraj
@guidance:Prabir


it will read the niravana json2csv csv file , look for clinvar colum if its empty it will take the dbsnp colum rs ID and make request. if result found it wll print otherwise it will continue.create csv file and paste the found Clinvar ID in the respective clinvar cloumn. 
"""
import pandas as pd
import requests

def get_clinvar_accession_and_description(rs_id):
    query_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={rs_id}[snp]&retmode=json"
    response = requests.get(query_url)
    try:
        data = response.json()
    except ValueError:
        print(f"Error decoding JSON response for {rs_id}")
        return None

    if 'esearchresult' in data and 'idlist' in data['esearchresult']:
        id_list = data['esearchresult']['idlist']
        clinvar_info = []
        if id_list:
            for clinvar_id in id_list:
                detail_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={clinvar_id}&retmode=json"
                detail_response = requests.get(detail_url)
                try:
                    detail_data = detail_response.json()
                except ValueError:
                    print(f"Error decoding details JSON response for {rs_id}")
                    continue

                if 'result' in detail_data and clinvar_id in detail_data['result']:
                    record = detail_data['result'][clinvar_id]
                    description = record.get('germline_classification', {}).get('description')
                    accession = record.get('accession')
                    if description and accession:
                        clinvar_info.append(f"{accession}:{description}")

            if clinvar_info:
                return "$".join(clinvar_info)
    return None

def update_csv_with_clinvar(input_filename, output_filename):
    df = pd.read_csv(input_filename)

    if 'clinvar' not in df.columns:
        df['clinvar'] = None

    for index, row in df.iterrows():
        if pd.isna(row['clinvar']) and pd.notna(row['dbsnp']):
            clinvar_data = get_clinvar_accession_and_description(row['dbsnp'])
            if clinvar_data:  # Only log and update if data is not None
                print(f"Updating dbSNP ID {row['dbsnp']} with ClinVar data.")
                df.at[index, 'clinvar'] = clinvar_data

    df.to_csv(output_filename, index=False)
    print(f"Updated CSV saved as {output_filename}")

# files
input_filename = "WLEAR-B-cf-D-CEFu-nonfilter.csv"
output_filename = "Updated_WLEAR-B-cf-D-CEFu-nonfilter.csv"
update_csv_with_clinvar(input_filename, output_filename)
