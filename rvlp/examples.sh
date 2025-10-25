#!/bin/bash

# =============================================================================
# Examples of using the Document Classifier
# =============================================================================

echo "Document Classifier - Usage Examples"
echo "====================================="
echo ""

# Example 1: Quick test with small sample
echo "1. Quick test with 10 samples per category:"
echo "   ./run_classifier.sh 10"
echo ""

# Example 2: Test only target categories
echo "2. Test only EMAIL and SCIENTIFIC_PUBLICATION with 100 samples:"
echo "   ./run_classifier.sh 100 email scientific_publication"
echo ""

# Example 3: Full test with plot
echo "3. Full test (200 samples) with confusion matrix saved:"
echo "   ./run_classifier.sh 200 --save-plot"
echo ""

# Example 4: Test specific categories with plot
echo "4. Test specific categories with plot:"
echo "   ./run_classifier.sh 50 --save-plot email invoice letter"
echo ""

# Example 5: Large scale test
echo "5. Large scale test (500 samples per category):"
echo "   ./run_classifier.sh 500"
echo ""

echo "====================================="
echo ""
echo "Running a quick demo with 25 samples..."
echo ""

# Run a quick demo
./run_classifier.sh 25 email scientific_publication