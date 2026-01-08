#!/usr/bin/env python3
"""
Test script for stock search functionality
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.kis_client import kis_client

def test_search(query):
    print(f"\n=== Searching for: {query} ===")
    try:
        results = kis_client.search_stock(query)
        if results:
            print(f"Found {len(results)} result(s):")
            for i, stock in enumerate(results, 1):
                print(f"{i}. {stock.get('name', 'N/A')} ({stock.get('code', 'N/A')})")
                print(f"   Price: {stock.get('price', 0)}")
        else:
            print("No results found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test cases
    test_search("그린광학")
    test_search("삼성전자")
    test_search("005930")  # Samsung Electronics code
    test_search("0015G0")  # Green Optical (checks if allowed)
