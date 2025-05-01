#!/bin/bash

echo "PMC-LaMP: PubMed Central Language Model Pipeline"
echo "==============================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3.8 or higher and try again."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if required directories exist, create if they don't
mkdir -p pmcids
mkdir -p fulltext_articles
mkdir -p indexes

echo "Starting PMC-LaMP..."
echo
echo "This terminal will keep the API server running."
echo "Please don't close this terminal while using the application."
echo
echo "Press Ctrl+C to stop the server when you're done."
echo

python3 run_pmc_lamp.py --step run

read -p "Press Enter to exit..." 