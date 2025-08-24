#!/usr/bin/env python3
"""
Run tests for Kiro Smart OCR.

This script runs tests for the Kiro Smart OCR project.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime


def run_tests(test_type, coverage=False, verbose=False):
    """
    Run tests of the specified type.
    
    Args:
        test_type: Type of tests to run (unit, integration, all)
        coverage: Whether to generate coverage report
        verbose: Whether to print verbose output
    """
    print(f"Running {test_type} tests...")
    
    # Determine test command
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=backend", "--cov=ai-engine", "--cov-report=term", "--cov-report=html"])
    
    if test_type == "unit":
        cmd.append("backend/tests/")
    elif test_type == "integration":
        cmd.append("testing/integration/")
    elif test_type == "multilingual":
        cmd.append("testing/multilingual/")
    elif test_type == "all":
        cmd.extend(["backend/tests/", "testing/"])
    
    # Run tests
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"{test_type.capitalize()} tests passed!")
    else:
        print(f"{test_type.capitalize()} tests failed!")
        sys.exit(result.returncode)


def run_benchmarks(benchmark_type, output_dir="testing/results"):
    """
    Run benchmarks of the specified type.
    
    Args:
        benchmark_type: Type of benchmarks to run (accuracy, performance, all)
        output_dir: Directory to save benchmark results
    """
    print(f"Running {benchmark_type} benchmarks...")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine benchmark command
    if benchmark_type == "accuracy":
        cmd = ["python", "-m", "testing.benchmarks.run_accuracy"]
    elif benchmark_type == "performance":
        cmd = ["python", "-m", "testing.benchmarks.run_performance"]
    elif benchmark_type == "multilingual":
        cmd = ["python", "-m", "testing.benchmarks.run_multilingual"]
    elif benchmark_type == "all":
        cmd = ["python", "-m", "testing.benchmarks.run_all"]
    
    # Add output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{benchmark_type}_benchmark_{timestamp}.json")
    cmd.extend(["--output", output_file])
    
    # Run benchmark
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"{benchmark_type.capitalize()} benchmarks completed!")
        print(f"Results saved to {output_file}")
    else:
        print(f"{benchmark_type.capitalize()} benchmarks failed!")
        sys.exit(result.returncode)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run tests for Kiro Smart OCR')
    parser.add_argument('--type', choices=['unit', 'integration', 'multilingual', 'all'], default='all',
                      help='Type of tests to run')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--benchmark', choices=['accuracy', 'performance', 'multilingual', 'all'],
                      help='Run benchmarks instead of tests')
    parser.add_argument('--output-dir', default='testing/results',
                      help='Directory to save benchmark results')
    args = parser.parse_args()
    
    if args.benchmark:
        run_benchmarks(args.benchmark, args.output_dir)
    else:
        run_tests(args.type, args.coverage, args.verbose)


if __name__ == '__main__':
    main()