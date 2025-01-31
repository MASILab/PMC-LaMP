#!/bin/bash

start_time=$(date +%s)

base_url="https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi"
format="BioC_json"
encoding="ascii"

output_dir="pmc_articles"
mkdir -p "$output_dir"

total_count=$(wc -l < pmc_result.txt)
current_count=0

while IFS= read -r pmcid
do
    current_count=$((current_count + 1))
    url="${base_url}/${format}/${pmcid}/${encoding}"
    response=$(curl -s -w "%{http_code}" "$url" -o "${output_dir}/${pmcid}.json")
    http_code=${response: -3}
    
    if [ $http_code -eq 200 ]; then
        echo "[$current_count/$total_count] Successfully fetched article $pmcid"
    else
        echo "[$current_count/$total_count] Failed to fetch article $pmcid: HTTP $http_code"
        rm "${output_dir}/${pmcid}.json"
    fi
done < pmc_result.txt

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "Completed fetching $total_count articles in $duration seconds"
echo "JSON files are stored in the '$output_dir' directory"