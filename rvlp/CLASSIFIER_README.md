# Document Classifier - Deterministic Image Processing Approach

A simple, explainable document classifier that uses only digital image processing techniques to classify documents into categories.

## 🎯 Features

- **No Machine Learning Required** - Pure rule-based approach
- **Fast Processing** - ~100-150 images/second
- **Highly Interpretable** - Clear, simple rules
- **Configurable** - Flexible sample sizes and category selection

## 📊 Performance

| Category | Accuracy | Detection Rule |
|----------|----------|----------------|
| EMAIL | 68.5% | High white space (>97%) + Low edge density (<3%) |
| SCIENTIFIC_PUBLICATION | 77.5% | High text component count (>1,200) |
| OTHER | 71.75% | Everything else |
| **Overall** | **72.38%** | Combined accuracy |

## 🚀 Quick Start

### Basic Usage

```bash
# Run with default settings (200 samples per category)
./run_classifier.sh

# Run with custom sample size
./run_classifier.sh 100

# Run with specific categories only
./run_classifier.sh 50 email scientific_publication

# Save confusion matrix as image
./run_classifier.sh 150 --save-plot
```

### Show Help

```bash
./run_classifier.sh --help
```

## 📁 Files

| File | Description |
|------|-------------|
| `run_classifier.sh` | Main execution script with parameters |
| `simple_classifier_cli.py` | Command-line classifier with arguments |
| `simple_classifier.py` | Original classifier with visualization |
| `test_classifier.py` | Simplified testing script |
| `analyze_categories.py` | Category analysis and feature exploration |
| `overview.md` | Complete implementation plan |

## 🔧 Python API Usage

```python
from simple_classifier_cli import SimpleDocumentClassifier

# Initialize classifier
classifier = SimpleDocumentClassifier()

# Classify a single image
prediction, confidence, features = classifier.classify('path/to/image.tif')

# Evaluate on dataset
y_true, y_pred, confidences = classifier.evaluate_on_dataset(
    test_path='data/test',
    categories_to_test=['email', 'scientific_publication'],
    samples_per_category=100
)
```

## 📈 Advanced Options

### Using Python Script Directly

```bash
# Basic usage
python simple_classifier_cli.py --samples 100

# With specific categories
python simple_classifier_cli.py --samples 50 --categories email invoice

# Save confusion matrix
python simple_classifier_cli.py --samples 200 --save-plot

# Custom test path
python simple_classifier_cli.py --test-path /path/to/data --samples 100
```

## 🎯 Classification Rules

The classifier uses these simple, deterministic rules:

### 1. EMAIL Detection
```
IF white_space_ratio > 0.97 AND edge_density < 0.03
THEN classify as EMAIL
```

### 2. SCIENTIFIC_PUBLICATION Detection
```
IF text_component_count > 1,200
THEN classify as SCIENTIFIC_PUBLICATION
```

### 3. OTHER Category
```
ELSE classify as OTHER
```

## 📊 Feature Extraction

The classifier extracts four main features:

1. **White Space Ratio**: Percentage of white pixels after binarization
2. **Edge Density**: Ratio of edge pixels (Canny edge detection)
3. **Text Components**: Count of connected components (10-500 pixel area)
4. **Large Black Regions**: Count of large non-text areas (>5000 pixels)

## 🔍 Why These Categories?

**EMAIL** documents have:
- Extremely high white space (98.1% average)
- Very low edge density (0.0207 average)
- Minimal visual complexity

**SCIENTIFIC PUBLICATIONS** have:
- Exceptionally high text density (1,800 components average)
- Dense, multi-column layout
- 3x more text components than other categories

## 📋 Requirements

```bash
pip install opencv-python numpy scikit-learn matplotlib seaborn tqdm
```

## 🏗️ Dataset Structure

Expected directory structure:
```
data/test/
├── email/
│   ├── *.tif
├── scientific_publication/
│   ├── *.tif
├── advertisement/
│   ├── *.tif
├── invoice/
│   ├── *.tif
├── letter/
│   ├── *.tif
└── presentation/
    ├── *.tif
```

## 💡 Key Insights

This project demonstrates that **not all classification problems require complex ML models**. By identifying distinctive visual features through image processing, we can achieve reasonable accuracy with completely explainable rules.

The approach is particularly effective when:
- Categories have clear visual distinctions
- Interpretability is important
- Fast processing is required
- Training data is limited

## 📝 License

Academic use - Part of PhD Data Science research in Computer Vision.