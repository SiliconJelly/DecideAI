#!/usr/bin/env python3
"""
Test script to verify RAG integration in the AI Employee Decision System.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_employee_decision_system.services import AIService, RetrievalService


def test_retrieval_service():
    """Test the retrieval service initialization."""
    print("=" * 60)
    print("Testing Retrieval Service")
    print("=" * 60)
    
    try:
        retrieval_service = RetrievalService.from_env()
        print(f"✓ Retrieval service created")
        print(f"  Available: {retrieval_service.is_available()}")
        
        if retrieval_service.is_available():
            # Test search
            test_query = "employee performance review"
            results = retrieval_service.search(test_query, top_k=3)
            print(f"\n✓ Search executed for query: '{test_query}'")
            print(f"  Results found: {len(results)}")
            
            for i, result in enumerate(results[:2], 1):
                print(f"\n  Result {i}:")
                print(f"    Score: {result['score']:.4f}")
                print(f"    Text: {result['text'][:100]}...")
                if result.get('metadata'):
                    print(f"    Metadata: {result['metadata']}")
        else:
            print("\n⚠ Index not available - this is expected if no documents have been indexed yet")
            print("  To enable RAG, you need to:")
            print("  1. Create the index directory: data/workspaces/sample-tenant/index")
            print("  2. Index some documents using the ingestion pipeline")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_ai_service_with_rag():
    """Test the AI service with RAG integration."""
    print("\n" + "=" * 60)
    print("Testing AI Service with RAG")
    print("=" * 60)
    
    try:
        ai_service = AIService()
        print("✓ AI service created")
        print(f"  RAG available: {ai_service.retrieval_service is not None}")
        
        # Test query without RAG
        print("\n--- Testing query without RAG ---")
        result = ai_service.process_query(
            "What are the key skills for a data scientist?",
            use_rag=False
        )
        print(f"✓ Query processed (without RAG)")
        print(f"  Response keys: {list(result.keys())}")
        print(f"  RAG enabled: {result.get('rag_enabled', 'N/A')}")
        
        # Test query with RAG (if available)
        if ai_service.retrieval_service:
            print("\n--- Testing query with RAG ---")
            result_with_rag = ai_service.process_query(
                "What are the key skills for a data scientist?",
                use_rag=True,
                top_k=3
            )
            print(f"✓ Query processed (with RAG)")
            print(f"  Response keys: {list(result_with_rag.keys())}")
            print(f"  RAG enabled: {result_with_rag.get('rag_enabled', 'N/A')}")
        else:
            print("\n⚠ Skipping RAG test - retrieval service not available")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAG Integration Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test retrieval service
    results.append(("Retrieval Service", test_retrieval_service()))
    
    # Test AI service with RAG
    results.append(("AI Service with RAG", test_ai_service_with_rag()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + ("=" * 60))
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())