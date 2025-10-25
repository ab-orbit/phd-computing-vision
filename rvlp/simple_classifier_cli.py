import cv2
import numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import sys
import argparse

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

        # Feature 4: Large black regions (for additional discrimination)
        large_black_regions = 0
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 5000:  # Large non-text regions
                large_black_regions += 1

        return {
            'white_space_ratio': white_space_ratio,
            'edge_density': edge_density,
            'text_components': text_components,
            'large_black_regions': large_black_regions
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
            return 'other', 0.0, features

        # Rule 1: EMAIL detection
        if features['white_space_ratio'] > 0.97 and features['edge_density'] < 0.03:
            # Calculate confidence based on how well it matches the pattern
            white_conf = min(features['white_space_ratio'] / 0.981, 1.0)
            edge_conf = min(0.03 / max(features['edge_density'], 0.001), 1.0)
            confidence = (white_conf + edge_conf) / 2
            return 'email', confidence, features

        # Rule 2: SCIENTIFIC_PUBLICATION detection
        if features['text_components'] > 1200:
            # Calculate confidence based on text density
            text_conf = min(features['text_components'] / 1800, 1.0)
            confidence = text_conf
            return 'scientific_publication', confidence, features

        # Rule 3: OTHER category
        return 'other', 0.5, features

    def evaluate_on_dataset(self, test_path, categories_to_test=None, samples_per_category=100):
        """Evaluate classifier on test dataset"""
        if categories_to_test is None:
            categories_to_test = ['email', 'scientific_publication', 'advertisement',
                                 'invoice', 'letter', 'presentation']

        y_true = []
        y_pred = []
        confidences = []

        print("\nEvaluating classifier performance...")
        print("-" * 60)

        for category in categories_to_test:
            category_path = Path(test_path) / category
            image_files = list(category_path.glob('*.tif'))[:samples_per_category]

            print(f"\nProcessing {category}: {len(image_files)} images")

            for img_path in tqdm(image_files, desc=f"  {category}"):
                # Get prediction
                prediction, confidence, features = self.classify(img_path)

                # Map actual category to our three classes
                if category == 'email':
                    true_label = 'email'
                elif category == 'scientific_publication':
                    true_label = 'scientific_publication'
                else:
                    true_label = 'other'

                y_true.append(true_label)
                y_pred.append(prediction)
                confidences.append(confidence)

        return y_true, y_pred, confidences

    def print_evaluation_report(self, y_true, y_pred, confidences, save_plot=False):
        """Print detailed evaluation metrics"""
        print("\n" + "=" * 70)
        print("CLASSIFICATION RESULTS")
        print("=" * 70)

        # Overall accuracy
        accuracy = np.mean(np.array(y_true) == np.array(y_pred))
        print(f"\nOverall Accuracy: {accuracy:.2%}")
        print(f"Average Confidence: {np.mean(confidences):.2%}")

        # Per-class metrics
        print("\n" + "-" * 70)
        print("Detailed Classification Report:")
        print("-" * 70)
        print(classification_report(y_true, y_pred, zero_division=0))

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=['email', 'scientific_publication', 'other'])

        # Calculate per-class accuracy
        print("\n" + "-" * 70)
        print("Per-Category Accuracy:")
        print("-" * 70)

        for i, category in enumerate(['email', 'scientific_publication', 'other']):
            if cm[i].sum() > 0:
                class_accuracy = cm[i, i] / cm[i].sum()
                print(f"{category:25s}: {class_accuracy:.2%} ({cm[i, i]}/{cm[i].sum()})")

        # Save confusion matrix plot if requested
        if save_plot:
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                        xticklabels=['email', 'sci_pub', 'other'],
                        yticklabels=['email', 'sci_pub', 'other'])
            plt.title('Confusion Matrix - Simple Document Classifier')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.tight_layout()
            plt.savefig('confusion_matrix.png', dpi=150)
            print("\nConfusion matrix saved as 'confusion_matrix.png'")

        return cm

def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple Document Classifier')
    parser.add_argument('--samples', type=int, default=200,
                       help='Number of samples per category to test (default: 200)')
    parser.add_argument('--test-path', type=str, default='data/test',
                       help='Path to test data directory (default: data/test)')
    parser.add_argument('--save-plot', action='store_true',
                       help='Save confusion matrix plot as image')
    parser.add_argument('--categories', nargs='+',
                       default=['email', 'scientific_publication', 'advertisement',
                               'invoice', 'letter', 'presentation'],
                       help='Categories to test (default: all 6)')

    args = parser.parse_args()

    # Initialize classifier
    classifier = SimpleDocumentClassifier()

    print("\n" + "=" * 70)
    print("SIMPLE DOCUMENT CLASSIFIER")
    print("=" * 70)
    print(f"Test path: {args.test_path}")
    print(f"Samples per category: {args.samples}")
    print(f"Categories to test: {', '.join(args.categories)}")

    # Evaluate classifier
    y_true, y_pred, confidences = classifier.evaluate_on_dataset(
        args.test_path,
        args.categories,
        samples_per_category=args.samples
    )

    # Print results
    cm = classifier.print_evaluation_report(y_true, y_pred, confidences, args.save_plot)

    # Print summary
    print("\n" + "=" * 70)
    print("CLASSIFICATION RULES")
    print("=" * 70)
    print("1. EMAIL: white_space > 0.97 AND edge_density < 0.03")
    print("2. SCIENTIFIC_PUBLICATION: text_components > 1,200")
    print("3. OTHER: Everything else")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())