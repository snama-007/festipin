#!/usr/bin/env python3
"""
Comprehensive Test Runner for Hybrid Input System

Usage:
    python run_tests.py                    # Run all non-LLM tests
    python run_tests.py --all              # Run all tests including LLM
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --performance      # Run performance benchmarks
    python run_tests.py --security         # Run security tests
    python run_tests.py --real-world       # Run real-world scenarios
    python run_tests.py --stress           # Run stress tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --fast             # Skip slow tests
"""

import sys
import subprocess
import argparse
from pathlib import Path


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def run_command(cmd, description):
    """Run a command and handle output"""
    print_info(f"Running: {description}")
    print(f"{Colors.BOLD}Command: {' '.join(cmd)}{Colors.ENDC}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print_success(f"{description} completed successfully\n")
        return True
    else:
        print_error(f"{description} failed with exit code {result.returncode}\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for Hybrid Input System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Test suite selection
    parser.add_argument('--all', action='store_true', help='Run all tests including LLM tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance benchmarks')
    parser.add_argument('--security', action='store_true', help='Run security tests')
    parser.add_argument('--real-world', action='store_true', help='Run real-world scenario tests')
    parser.add_argument('--stress', action='store_true', help='Run stress tests')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive test suite')

    # Test options
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--fast', action='store_true', help='Skip slow tests')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--markers', type=str, help='Run tests with specific markers')
    parser.add_argument('--keyword', '-k', type=str, help='Run tests matching keyword')

    args = parser.parse_args()

    # Build pytest command
    base_cmd = ['pytest']

    # Add test files based on selection
    test_files = []

    if args.unit or not any([args.all, args.integration, args.performance, args.security, args.real_world, args.comprehensive]):
        test_files.append('tests/test_hybrid_input_system.py')

    if args.integration or args.all:
        test_files.append('tests/test_hybrid_input_system.py')

    if args.comprehensive or args.all:
        test_files.append('tests/test_hybrid_comprehensive.py')

    if args.real_world or args.all:
        test_files.append('tests/test_real_world_scenarios.py')

    if args.performance or args.all:
        test_files.append('tests/test_performance_benchmarks.py')

    if args.security or args.all:
        test_files.append('tests/test_security_validation.py')

    # If no specific test selected, run basic tests
    if not test_files:
        test_files = ['tests/test_hybrid_input_system.py']

    base_cmd.extend(test_files)

    # Add options
    if args.verbose:
        base_cmd.append('-v')
    else:
        base_cmd.append('-q')

    if args.all:
        base_cmd.append('--llm')  # Enable LLM tests

    if args.stress:
        base_cmd.extend(['-m', 'stress'])

    if args.markers:
        base_cmd.extend(['-m', args.markers])

    if args.keyword:
        base_cmd.extend(['-k', args.keyword])

    if args.fast:
        base_cmd.extend(['-m', 'not slow'])

    if args.parallel:
        base_cmd.extend(['-n', 'auto'])

    if args.coverage:
        # Run with coverage
        coverage_cmd = [
            'pytest',
            '--cov=app/services',
            '--cov-report=html',
            '--cov-report=term',
            *test_files
        ]
        if args.verbose:
            coverage_cmd.append('-v')

        print_header("RUNNING TESTS WITH COVERAGE")
        success = run_command(coverage_cmd, "Coverage Analysis")

        if success:
            print_success("Coverage report generated in htmlcov/index.html")
    else:
        # Run normal tests
        print_header("RUNNING HYBRID INPUT SYSTEM TESTS")

        if args.all:
            print_info("Running ALL tests (including LLM tests - requires API key)")
        elif args.comprehensive:
            print_info("Running comprehensive test suite")
        elif args.performance:
            print_info("Running performance benchmarks")
        elif args.security:
            print_info("Running security tests")
        elif args.real_world:
            print_info("Running real-world scenarios")
        else:
            print_info("Running standard test suite")

        success = run_command(base_cmd, "Test Execution")

    # Print summary
    print_header("TEST SUMMARY")

    if success:
        print_success("All tests passed!")
        print()
        print(f"{Colors.OKGREEN}{'✓' * 70}{Colors.ENDC}")
        return 0
    else:
        print_error("Some tests failed!")
        print()
        print(f"{Colors.FAIL}{'✗' * 70}{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
