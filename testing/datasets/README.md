# Test Datasets for Kiro Smart OCR

This directory contains test datasets for validating the OCR and LLM components of Kiro Smart OCR. The datasets are organized by language and document type.

## Directory Structure

```
datasets/
├── german/
│   ├── invoices/
│   ├── receipts/
│   └── handwritten/
├── japanese/
│   ├── invoices/
│   ├── receipts/
│   └── handwritten/
├── english/
│   ├── invoices/
│   ├── receipts/
│   └── handwritten/
└── mixed/
    └── multilingual_documents/
```

## Dataset Sources

The test datasets should be sourced from:

1. **Synthetic Data**: Generated documents with known ground truth
2. **Public Datasets**: Open-source document datasets (properly attributed)
3. **Anonymized Real Data**: Real-world documents with sensitive information removed

## File Naming Convention

Files should follow this naming convention:

```
{language_code}_{document_type}_{id}_{quality}.{ext}
```

Examples:
- `de_invoice_001_clean.pdf`
- `ja_receipt_042_noisy.jpg`
- `en_handwritten_015_blurry.png`

## Ground Truth Format

Each test document should have a corresponding ground truth file in JSON format:

```json
{
  "document_id": "de_invoice_001",
  "language": "de",
  "document_type": "invoice",
  "fields": {
    "vendor_name": {
      "value": "Example GmbH",
      "bounding_box": [100, 200, 300, 250]
    },
    "invoice_number": {
      "value": "INV-2025-001",
      "bounding_box": [400, 200, 550, 250]
    },
    "date": {
      "value": "15.03.2025",
      "bounding_box": [400, 300, 550, 350]
    },
    "total_amount": {
      "value": "1250,00",
      "bounding_box": [700, 800, 800, 850]
    }
  },
  "raw_text": "Example GmbH\nRechnung\nNr. INV-2025-001\nDatum: 15.03.2025\n...",
  "metadata": {
    "quality": "clean",
    "source": "synthetic",
    "difficulty_level": "easy"
  }
}
```

## Usage

These datasets are used for:

1. **Training**: Fine-tuning OCR and LLM models
2. **Validation**: Evaluating model performance during development
3. **Testing**: Automated testing of the complete system
4. **Benchmarking**: Measuring accuracy and performance metrics

## Adding New Test Data

When adding new test data:

1. Place the document in the appropriate language and type directory
2. Create a corresponding ground truth JSON file with the same base name
3. Update the dataset inventory file if applicable
4. Ensure the data is properly anonymized if derived from real documents