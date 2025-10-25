## Deterministic Document Classifier - Implementation Plan

### Dataset Overview
- **Test data location**: `rvlp/data/test/`
- **16 Document Categories**: advertisement, budget, email, file_folder, form, handwritten, invoice, letter, memo, news_article, presentation, questionnaire, resume, scientific_publication, scientific_report, specification
- **Format**: TIF images (~40,000 files total)

### Classification Approach Using Digital Image Processing

#### Phase 1: Feature Extraction Pipeline
1. **Document Layout Analysis**
   - Extract text/non-text region ratios
   - Detect column structure (single vs multi-column)
   - Measure white space distribution
   - Identify header/footer regions

2. **Visual Complexity Features**
   - Edge density analysis (Canny/Sobel operators)
   - Texture patterns using Local Binary Patterns (LBP)
   - Histogram of Oriented Gradients (HOG) for structural patterns
   - Frequency domain analysis (FFT) for periodic patterns

3. **Graphical Elements Detection**
   - Logo/image region detection (high contrast regions)
   - Table/grid structure detection (line intersections)
   - Chart/graph detection (geometric shapes)
   - Handwriting vs printed text discrimination

4. **Typography Features**
   - Font size variations (via connected component analysis)
   - Text density per page region
   - Line spacing patterns
   - Alignment patterns (left, center, justified)

#### Phase 2: Rule-Based Classifier Design

**Document Category Rules:**
1. **Advertisement**: High image-to-text ratio, varied font sizes, non-uniform layout
2. **Budget/Invoice**: Table structures, numerical patterns, grid alignment
3. **Email**: Header pattern detection, consistent margins, specific layout
4. **Form**: Checkbox/field patterns, regular spacing, horizontal lines
5. **Handwritten**: High edge irregularity, non-uniform stroke patterns
6. **Letter/Memo**: Formal header, consistent margins, single column
7. **News Article**: Multi-column layout, dense text, headline detection
8. **Presentation**: Slide-like layout, bullet points, large fonts
9. **Resume**: Specific sections, consistent formatting, name prominence
10. **Scientific Publication**: Two-column layout, abstract section, references
11. **Questionnaire**: Repeated patterns, checkbox structures, numbered items
12. **Specification**: Hierarchical numbering, technical diagrams, dense text

#### Phase 3: Implementation Steps
1. **Preprocessing Module**
   - Noise reduction (morphological operations)
   - Skew correction
   - Contrast normalization
   - Binarization (Otsu's method)

2. **Feature Extraction Module**
   - Implement each feature extractor
   - Create feature vectors
   - Normalize features

3. **Decision Tree Classifier**
   - Build hierarchical decision rules
   - First level: Handwritten vs Printed
   - Second level: Layout complexity (simple/complex)
   - Third level: Specific document features

4. **Evaluation Framework**
   - Confusion matrix generation
   - Per-category accuracy metrics
   - Feature importance analysis

### Key Advantages of This Approach
- **Deterministic**: No ML training required, purely rule-based
- **Interpretable**: Clear decision paths for each classification
- **Fast**: Image processing operations are computationally efficient
- **Robust**: Based on structural document properties

### Tools & Libraries
- OpenCV for image processing operations
- NumPy for numerical computations
- scikit-image for advanced image analysis
- matplotlib for visualization

### Next Steps
1. Load and visualize sample images from each category
2. Implement preprocessing pipeline
3. Develop feature extractors
4. Create decision rules based on feature analysis
5. Build the complete classifier
6. Evaluate on test set