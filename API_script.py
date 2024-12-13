#I would like to use a script that gathers gene information from the following sites:
#ensembl, NCBI, and GeneCards. 
#I will use Ensembl and NCBI's respective API's and webscraping for GeneCards.

#Set Up:
pip install requests
pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup

#Ensembl REST API
#Ensembl gives information on description, gene synonyms, location, gene type, 
#and regulatory features

def get_ensembl_data(gene_symbol):
    """Fetch data from Ensembl API."""
    ensembl_base_url = "https://rest.ensembl.org"
    headers = {"Content-Type": "application/json"}

    # Gene lookup
    lookup_url = f"{ensembl_base_url}/lookup/symbol/human/{gene_symbol}?expand=1"
    response = requests.get(lookup_url, headers=headers)

    if response.status_code == 200:
        gene_data = response.json()
        description = gene_data.get("description", "N/A")
        synonyms = ", ".join(gene_data.get("synonyms", [])) or "N/A"
        location = f"{gene_data['seq_region_name']}:{gene_data['start']}-{gene_data['end']}"
        gene_type = gene_data.get("biotype", "N/A")
        
        # Fetch regulatory features
        regulatory_url = f"{ensembl_base_url}/regulatory/species/homo_sapiens/feature/{gene_symbol}?content-type=application/json"
        regulatory_response = requests.get(regulatory_url, headers=headers)

        regulatory_features = []
        if regulatory_response.status_code == 200:
            reg_features = regulatory_response.json()
            regulatory_features = [
                f"{feature['feature_type']} at {feature['seq_region_name']}:{feature['start']}-{feature['end']}"
                for feature in reg_features
            ]

        return {
            "Description": description,
            "Synonyms": synonyms,
            "Location": location,
            "Gene Type": gene_type,
            "Regulatory Features": regulatory_features,
        }
    else:
        print("Failed to retrieve data from Ensembl.")
        return {}

def get_ncbi_data(gene_symbol):
    """Fetch data from NCBI API."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "gene",
        "term": f"{gene_symbol}[Gene] AND human[Organism]",
        "retmode": "json"
    }
    search_response = requests.get(base_url, params=params)

    if search_response.status_code == 200:
        search_data = search_response.json()
        if "idlist" in search_data["esearchresult"] and search_data["esearchresult"]["idlist"]:
            gene_id = search_data["esearchresult"]["idlist"][0]
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "gene",
                "id": gene_id,
                "retmode": "json"
            }
            summary_response = requests.get(summary_url, params=summary_params)
            if summary_response.status_code == 200:
                gene_summary = summary_response.json()["result"][gene_id]
                return {
                    "Official Full Name": gene_summary.get("nomenclature", "N/A"),
                    "Summary": gene_summary.get("summary", "N/A"),
                }
    print("Failed to retrieve data from NCBI.")
    return {}

def get_genecards_summary(gene_symbol):
    """Fetch data from GeneCards using web scraping."""
    base_url = f"https://www.genecards.org/cgi-bin/carddisp.pl?gene={gene_symbol}"
    response = requests.get(base_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        summary = soup.find("div", {"class": "gc-subsection-inner"}).get_text(strip=True)
        return {"GeneCards Summary": summary}
    else:
        print("Failed to retrieve data from GeneCards.")
        return {}

# Main function to fetch all data
def fetch_gene_data(gene_symbol):
    ensembl_data = get_ensembl_data(gene_symbol)
    ncbi_data = get_ncbi_data(gene_symbol)
    genecards_data = get_genecards_summary(gene_symbol)

    # Combine all results
    result = {**ensembl_data, **ncbi_data, **genecards_data}
    return result

#Example: Fetch data for KDM6A
fetch_gene_data("KDM6A")



#Resources used: 
#Ensembl REST API documentation: https://rest.ensembl.org 
#Help: https://www.youtube.com/watch?v=JKD2VJnjs98

#NCBI documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/
#Help: Thin-Ad2083 reddit post 
#https://www.reddit.com/r/bioinformatics/comments/172gu4q/how_to_use_ncbi_apis/


#Webscraping: BeautifulSoup https://www.crummy.com/software/BeautifulSoup/bs4/doc/#
#Help: https://www.youtube.com/watch?v=bargNl2WeN4
















