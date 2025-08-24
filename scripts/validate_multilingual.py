#!/usr/bin/env python3
"""
Validate multilingual OCR capabilities of Kiro Smart OCR.

This script tests the OCR engine with sample documents in German, Japanese, and English
to validate the multilingual capabilities of the system.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import OCR engine
from ai_engine.ocr.multilingual_engine import MultilingualOCREngine
from ai_engine.llm.multilingual_llm_service import MultilingualLLMService
from backend.app.models.ocr import DocumentType, LanguageCode


def validate_ocr(sample_dir: str, output_dir: str, verbose: bool = False):
    """
    Validate OCR engine with sample documents.
    
    Args:
        sample_dir: Directory containing sample documents
        output_dir: Directory to save results
        verbose: Whether to print verbose output
    """
    print(f"Validating OCR engine with samples from {sample_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize OCR engine
    ocr_engine = MultilingualOCREngine()
    llm_service = MultilingualLLMService()
    
    # Find sample documents
    sample_files = []
    for lang in ['german', 'japanese', 'english']:
        lang_dir = os.path.join(sample_dir, lang)
        if os.path.exists(lang_dir):
            for doc_type in ['invoices', 'receipts', 'handwritten']:
                type_dir = os.path.join(lang_dir, doc_type)
                if os.path.exists(type_dir):
                    for file in os.listdir(type_dir):
                        if file.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                            sample_files.append({
                                'path': os.path.join(type_dir, file),
                                'language': lang,
                                'document_type': doc_type[:-1]  # Remove 's' from plural
                            })
    
    if not sample_files:
        print(f"No sample documents found in {sample_dir}")
        return
    
    print(f"Found {len(sample_files)} sample documents")
    
    # Process each sample document
    results = []
    for i, sample in enumerate(sample_files):
        print(f"Processing {i+1}/{len(sample_files)}: {os.path.basename(sample['path'])}")
        
        try:
            # Map language string to LanguageCode enum
            language_map = {
                'german': LanguageCode.GERMAN,
                'japanese': LanguageCode.JAPANESE,
                'english': LanguageCode.ENGLISH
            }
            target_language = language_map.get(sample['language'])
            
            # Map document type string to DocumentType enum
            doc_type_map = {
                'invoice': DocumentType.INVOICE,
                'receipt': DocumentType.RECEIPT,
                'handwritten': DocumentType.HANDWRITTEN
            }
            document_type = doc_type_map.get(sample['document_type'])
            
            # Process document
            start_time = datetime.now()
            ocr_result = ocr_engine.process_document(sample['path'], target_language)
            ocr_time = (datetime.now() - start_time).total_seconds()
            
            # Structure document
            start_time = datetime.now()
            document_id = f"test-{i+1}"
            structured_doc = llm_service.structure_document(ocr_result, document_type, document_id)
            llm_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate total processing time
            total_time = ocr_time + llm_time
            
            # Get ground truth file if available
            ground_truth_path = os.path.splitext(sample['path'])[0] + '.json'
            ground_truth = None
            if os.path.exists(ground_truth_path):
                with open(ground_truth_path, 'r', encoding='utf-8') as f:
                    ground_truth = json.load(f)
            
            # Calculate accuracy if ground truth is available
            accuracy = None
            if ground_truth:
                # Simple accuracy calculation based on field extraction
                correct_fields = 0
                total_fields = len(ground_truth['fields'])
                
                for field_name, field_data in ground_truth['fields'].items():
                    if field_name in structured_doc.fields:
                        extracted_value = structured_doc.fields[field_name].value
                        expected_value = field_data['value']
                        
                        # Simple string comparison (in a real implementation, this would be more sophisticated)
                        if str(extracted_value).strip() == str(expected_value).strip():
                            correct_fields += 1
                
                accuracy = correct_fields / total_fields if total_fields > 0 else 0
            
            # Create result entry
            result = {
                'file': os.path.basename(sample['path']),
                'language': sample['language'],
                'document_type': sample['document_type'],
                'detected_language': ocr_result.language.value,
                'ocr_confidence': ocr_result.confidence,
                'structured_confidence': structured_doc.confidence_score,
                'ocr_time': ocr_time,
                'llm_time': llm_time,
                'total_time': total_time,
                'field_count': len(structured_doc.fields),
                'accuracy': accuracy
            }
            
            results.append(result)
            
            if verbose:
                print(f"  Detected language: {ocr_result.language.value}")
                print(f"  OCR confidence: {ocr_result.confidence:.2f}")
                print(f"  Structured confidence: {structured_doc.confidence_score:.2f}")
                print(f"  Processing time: {total_time:.2f}s (OCR: {ocr_time:.2f}s, LLM: {llm_time:.2f}s)")
                print(f"  Fields extracted: {len(structured_doc.fields)}")
                if accuracy is not None:
                    print(f"  Accuracy: {accuracy:.2f}")
                print()
        
        except Exception as e:
            print(f"  Error processing {sample['path']}: {str(e)}")
            results.append({
                'file': os.path.basename(sample['path']),
                'language': sample['language'],
                'document_type': sample['document_type'],
                'error': str(e)
            })
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = os.path.join(output_dir, f'multilingual_validation_{timestamp}.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'sample_count': len(sample_files),
            'results': results
        }, f, indent=2)
    
    print(f"Results saved to {results_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total samples: {len(sample_files)}")
    
    successful = [r for r in results if 'error' not in r]
    print(f"Successful: {len(successful)}/{len(sample_files)} ({len(successful)/len(sample_files)*100:.1f}%)")
    
    if successful:
        avg_ocr_confidence = sum(r['ocr_confidence'] for r in successful) / len(successful)
        avg_structured_confidence = sum(r['structured_confidence'] for r in successful) / len(successful)
        avg_total_time = sum(r['total_time'] for r in successful) / len(successful)
        
        print(f"Average OCR confidence: {avg_ocr_confidence:.2f}")
        print(f"Average structured confidence: {avg_structured_confidence:.2f}")
        print(f"Average processing time: {avg_total_time:.2f}s")
        
        # Print language-specific stats
        for lang in ['german', 'japanese', 'english']:
            lang_results = [r for r in successful if r['language'] == lang]
            if lang_results:
                avg_lang_confidence = sum(r['structured_confidence'] for r in lang_results) / len(lang_results)
                print(f"{lang.capitalize()} samples: {len(lang_results)}, Avg confidence: {avg_lang_confidence:.2f}")
        
        # Print accuracy stats if available
        accuracy_results = [r for r in successful if r.get('accuracy') is not None]
        if accuracy_results:
            avg_accuracy = sum(r['accuracy'] for r in accuracy_results) / len(accuracy_results)
            print(f"Average accuracy: {avg_accuracy:.2f}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate multilingual OCR capabilities')
    parser.add_argument('--sample-dir', default='testing/datasets', help='Directory containing sample documents')
    parser.add_argument('--output-dir', default='testing/results', help='Directory to save results')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    args = parser.parse_args()
    
    validate_ocr(args.sample_dir, args.output_dir, args.verbose)


if __name__ == '__main__':
    main()