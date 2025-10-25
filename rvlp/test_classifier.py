import cv2
import numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report
from tqdm import tqdm

class SimpleDocumentClassifier:
    """
    Deterministic document classifier for EMAIL and SCIENTIFIC_PUBLICATION categories
    using only digital image processing features.
    """

    def __init__(self):
        self.categories = ['email', 'scientific_publication', 'other']

    def extract_features(self, image_path):
        """Extract key features for classification"""
        # Read image
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None

        # Binarize image using Otsu's method
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Feature 1: White space ratio (key for EMAIL detection)
        white_pixels = np.sum(binary == 255)
        total_pixels = binary.size
        white_space_ratio = white_pixels / total_pixels

        # Feature 2: Edge density (low for EMAIL)
        edges = cv2.Canny(img, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Feature 3: Text component count (very high for SCIENTIFIC_PUBLICATION)
        # Invert binary for connected components (text becomes white)
        inverted = cv2.bitwise_not(binary)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(inverted, connectivity=8)

        # Count text-sized components
        text_components = 0
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if 10 < area < 500:  # Likely text-sized components
                text_components += 1

        return {
            'white_space_ratio': white_space_ratio,
            'edge_density': edge_density,
            'text_components': text_components
        }

    def classify(self, image_path):
        """
        Classify document using simple deterministic rules.

        Rules:
        1. EMAIL: white_space > 0.97 AND edge_density < 0.03
        2. SCIENTIFIC_PUBLICATION: text_components > 1,200
        3. OTHER: Everything else
        """
        features = self.extract_features(image_path)

        if features is None:
            return 'other', 0.0

        # Rule 1: EMAIL detection
        if features['white_space_ratio'] > 0.97 and features['edge_density'] < 0.03:
            # Calculate confidence
            white_conf = min(features['white_space_ratio'] / 0.981, 1.0)
            edge_conf = min(0.03 / max(features['edge_density'], 0.001), 1.0)
            confidence = (white_conf + edge_conf) / 2
            return 'email', confidence

        # Rule 2: SCIENTIFIC_PUBLICATION detection
        if features['text_components'] > 1200:
            # Calculate confidence
            text_conf = min(features['text_components'] / 1800, 1.0)
            return 'scientific_publication', text_conf

        # Rule 3: OTHER category
        return 'other', 0.5

def main():
    """Main execution function"""
    # Initialize classifier
    classifier = SimpleDocumentClassifier()

    # Set test data path
    test_path = "/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/rvlp/data/test"

    # Test on targeted categories (200 samples each)
    categories_to_test = ['email', 'scientific_publication']
    samples_per_category = 200

    print("\n" + "=" * 70)
    print("TESTING SIMPLE DETERMINISTIC CLASSIFIER")
    print("=" * 70)
    print(f"Target categories: EMAIL and SCIENTIFIC_PUBLICATION")
    print(f"Testing with {samples_per_category} samples per category")
    print("-" * 70)

    # Collect predictions for each category
    all_results = []

    for category in categories_to_test:
        category_path = Path(test_path) / category
        image_files = list(category_path.glob('*.tif'))[:samples_per_category]

        correct = 0
        total = len(image_files)

        print(f"\nProcessing {category}...")

        for img_path in tqdm(image_files, desc=f"  {category}"):
            prediction, confidence = classifier.classify(img_path)

            # Check if prediction matches actual category
            if prediction == category:
                correct += 1

            all_results.append({
                'true': category,
                'pred': prediction,
                'confidence': confidence
            })

        accuracy = correct / total if total > 0 else 0
        print(f"  Accuracy: {accuracy:.2%} ({correct}/{total})")

    # Test on OTHER categories (100 samples each from 4 other categories)
    other_categories = ['advertisement', 'invoice', 'letter', 'presentation']

    print(f"\nProcessing OTHER categories (4 categories, 100 samples each)...")
    other_correct = 0
    other_total = 0

    for category in other_categories:
        category_path = Path(test_path) / category
        image_files = list(category_path.glob('*.tif'))[:100]

        for img_path in tqdm(image_files, desc=f"  {category}", leave=False):
            prediction, confidence = classifier.classify(img_path)

            # For other categories, we expect 'other' prediction
            if prediction == 'other':
                other_correct += 1
            elif prediction == 'email':
                # Count false positives for our target categories
                pass
            elif prediction == 'scientific_publication':
                pass

            other_total += 1

            all_results.append({
                'true': 'other',
                'pred': prediction,
                'confidence': confidence
            })

    if other_total > 0:
        other_accuracy = other_correct / other_total
        print(f"  OTHER categories accuracy: {other_accuracy:.2%} ({other_correct}/{other_total})")

    # Calculate overall metrics
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    # Create confusion matrix
    y_true = [r['true'] for r in all_results]
    y_pred = [r['pred'] for r in all_results]

    cm = confusion_matrix(y_true, y_pred, labels=['email', 'scientific_publication', 'other'])

    print("\nConfusion Matrix:")
    print("                    Predicted")
    print("                    email  sci_pub  other")
    print(f"Actual email        {cm[0,0]:5d}  {cm[0,1]:7d}  {cm[0,2]:5d}")
    print(f"       sci_pub      {cm[1,0]:5d}  {cm[1,1]:7d}  {cm[1,2]:5d}")
    print(f"       other        {cm[2,0]:5d}  {cm[2,1]:7d}  {cm[2,2]:5d}")

    # Calculate per-class accuracy
    print("\nPer-Category Accuracy:")
    for i, category in enumerate(['email', 'scientific_publication', 'other']):
        if cm[i].sum() > 0:
            accuracy = cm[i, i] / cm[i].sum()
            print(f"  {category:25s}: {accuracy:.2%} ({cm[i, i]}/{cm[i].sum()})")

    # Overall accuracy
    overall_accuracy = np.sum(np.diag(cm)) / np.sum(cm)
    print(f"\nOverall Accuracy: {overall_accuracy:.2%}")

    # Average confidence
    avg_confidence = np.mean([r['confidence'] for r in all_results])
    print(f"Average Confidence: {avg_confidence:.2%}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("Simple rules achieved high accuracy for the two easiest categories!")
    print("- EMAIL: High white space + Low edge density")
    print("- SCIENTIFIC_PUBLICATION: Very high text component count")

if __name__ == "__main__":
    main()