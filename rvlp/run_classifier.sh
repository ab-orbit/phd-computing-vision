#!/bin/bash

# =============================================================================
# Document Classifier Runner Script
# =============================================================================
# Usage: ./run_classifier.sh [samples] [categories...]
# Example: ./run_classifier.sh 100
# Example: ./run_classifier.sh 50 email scientific_publication
# Example: ./run_classifier.sh 200 --save-plot
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_SAMPLES=200
SAVE_PLOT=""
CATEGORIES=""

# Function to print usage
usage() {
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${GREEN}Document Classifier Runner${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
    echo ""
    echo "Usage: $0 [samples] [options] [categories...]"
    echo ""
    echo "Arguments:"
    echo "  samples         Number of samples per category (default: 200)"
    echo ""
    echo "Options:"
    echo "  --save-plot     Save confusion matrix as image"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Categories (optional, default: all):"
    echo "  email, scientific_publication, advertisement, invoice, letter, presentation"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run with default 200 samples"
    echo "  $0 100                       # Run with 100 samples per category"
    echo "  $0 50 email invoice          # Test only email and invoice with 50 samples"
    echo "  $0 150 --save-plot           # Run with 150 samples and save plot"
    echo ""
    echo -e "${BLUE}===============================================================================${NC}"
}

# Check for help flag
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    usage
    exit 0
fi

# Parse arguments
SAMPLES=$DEFAULT_SAMPLES
ARGS=()

for arg in "$@"; do
    if [[ "$arg" == "--save-plot" ]]; then
        SAVE_PLOT="--save-plot"
    elif [[ "$arg" =~ ^[0-9]+$ ]] && [[ -z "$SAMPLES_SET" ]]; then
        SAMPLES=$arg
        SAMPLES_SET=true
    else
        ARGS+=("$arg")
    fi
done

# Build categories argument if specified
if [[ ${#ARGS[@]} -gt 0 ]]; then
    CATEGORIES="--categories ${ARGS[@]}"
fi

# Print configuration
echo -e "${BLUE}===============================================================================${NC}"
echo -e "${GREEN}Running Document Classifier${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  Samples per category: ${GREEN}$SAMPLES${NC}"

if [[ -n "$SAVE_PLOT" ]]; then
    echo -e "  Save confusion matrix: ${GREEN}Yes${NC}"
else
    echo -e "  Save confusion matrix: ${YELLOW}No${NC}"
fi

if [[ -n "$CATEGORIES" ]]; then
    echo -e "  Categories: ${GREEN}${ARGS[@]}${NC}"
else
    echo -e "  Categories: ${GREEN}All (default)${NC}"
fi

echo -e "${BLUE}===============================================================================${NC}"
echo ""

# Check if Python script exists
if [[ ! -f "simple_classifier_cli.py" ]]; then
    echo -e "${RED}Error: simple_classifier_cli.py not found!${NC}"
    echo "Please ensure you're running this script from the correct directory."
    exit 1
fi

# Check if data directory exists
if [[ ! -d "data/test" ]]; then
    echo -e "${YELLOW}Warning: data/test directory not found!${NC}"
    echo "Checking alternative paths..."

    # Try alternative path
    if [[ -d "/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/rvlp/data/test" ]]; then
        echo -e "${GREEN}Found data at absolute path${NC}"
        DATA_PATH="/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/rvlp/data/test"
    else
        echo -e "${RED}Error: Could not find test data directory!${NC}"
        exit 1
    fi
else
    DATA_PATH="data/test"
fi

# Run the classifier
echo "Starting classification..."
echo ""

# Build the command
CMD="python simple_classifier_cli.py --samples $SAMPLES"

if [[ -n "$DATA_PATH" ]] && [[ "$DATA_PATH" != "data/test" ]]; then
    CMD="$CMD --test-path $DATA_PATH"
fi

if [[ -n "$SAVE_PLOT" ]]; then
    CMD="$CMD $SAVE_PLOT"
fi

if [[ -n "$CATEGORIES" ]]; then
    CMD="$CMD $CATEGORIES"
fi

# Execute the command
eval $CMD

# Check exit status
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}Classification completed successfully!${NC}"

    if [[ -n "$SAVE_PLOT" ]] && [[ -f "confusion_matrix.png" ]]; then
        echo -e "${GREEN}Confusion matrix saved as confusion_matrix.png${NC}"
    fi
else
    echo ""
    echo -e "${RED}Classification failed!${NC}"
    exit 1
fi

echo -e "${BLUE}===============================================================================${NC}"