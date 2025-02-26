#!/bin/bash

start_time=$(date +%s)

# Define configuration for using the PubMed Central Open Access (PMCOA) API
base_url="https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi"
format="BioC_json"
encoding="ascii"
input_file="$1"
keyword=$(basename "$input_file" _pmc_result.txt)
output_dir="fulltext_articles/${keyword}_pmc_articles"
mkdir -p "$output_dir"

# Get the total count of PMCIDs in the input file
total_count=$(wc -l < "$input_file")
current_count=0

# Iterate through the PMCIDs in the input file
while IFS= read -r pmcid
do
    current_count=$((current_count + 1))

    # Construct the API URL for the current PMCID
    url="${base_url}/${format}/${pmcid}/${encoding}"

    # Use cURL to fetch the article in BioC JSON format and capture the HTTP response code
    response=$(curl -s -w "%{http_code}" "$url" -o "${output_dir}/${pmcid}.json")
    http_code=${response: -3}

    # Check the HTTP response code
    if [ "$http_code" -eq 200 ]; then
        echo "[$current_count/$total_count] Successfully fetched article $pmcid"
    else
        echo "[$current_count/$total_count] Failed to fetch article $pmcid: HTTP $http_code"
        rm "${output_dir}/${pmcid}.json"
    fi
done < "$input_file"

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "Completed fetching $total_count articles in $duration seconds"
echo "JSON files are stored in the '$output_dir' directory"