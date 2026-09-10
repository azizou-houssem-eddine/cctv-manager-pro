"""
Automated E2E Test Suite Runner for CCTV Manager Pro.
Executes test suites across Tiers 1-4, tracks execution duration,
and formats a clean summary report.
"""

import os
import sys
import time
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TierCollectorPlugin:
    """Pytest plugin to classify test results across Tiers 1-4."""

    def __init__(self):
        self.results = {
            "Tier 1 (Feature Coverage)": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Tier 2 (Boundary & Corner)": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Tier 3 (Cross-Feature)": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Tier 4 (Real-World Scenarios)": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
            "Other": {"passed": 0, "failed": 0, "skipped": 0, "tests": []},
        }
        self.failures = []

    def get_tier(self, name: str) -> str:
        name_lower = name.lower()
        if "tier1" in name_lower:
            return "Tier 1 (Feature Coverage)"
        elif "tier2" in name_lower:
            return "Tier 2 (Boundary & Corner)"
        elif "tier3" in name_lower:
            return "Tier 3 (Cross-Feature)"
        elif "tier4" in name_lower:
            return "Tier 4 (Real-World Scenarios)"
        return "Other"

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            tier = self.get_tier(report.nodeid)
            if report.passed:
                self.results[tier]["passed"] += 1
                self.results[tier]["tests"].append((report.nodeid, "PASSED", report.duration))
            elif report.failed:
                self.results[tier]["failed"] += 1
                self.results[tier]["tests"].append((report.nodeid, "FAILED", report.duration))
                self.failures.append((report.nodeid, report.longreprtext))
            elif report.skipped:
                self.results[tier]["skipped"] += 1
                self.results[tier]["tests"].append((report.nodeid, "SKIPPED", report.duration))
        elif report.when == "setup" and report.skipped:
            tier = self.get_tier(report.nodeid)
            self.results[tier]["skipped"] += 1
            self.results[tier]["tests"].append((report.nodeid, "SKIPPED", report.duration))


def main():
    print("=" * 70)
    print("  CCTV MANAGER PRO — AUTOMATED E2E TEST SUITE RUNNER")
    print("=" * 70)
    print(f"Working Directory: {PROJECT_ROOT}")
    print(f"Python Version:    {sys.version.split()[0]}")
    print("-" * 70)

    collector = TierCollectorPlugin()
    tests_dir = os.path.join(PROJECT_ROOT, "tests")

    start_time = time.time()
    exit_code = pytest.main(
        [tests_dir, "-v", "--tb=short", "-p", "no:warnings"],
        plugins=[collector]
    )
    duration = time.time() - start_time

    print("\n" + "=" * 70)
    print("  TEST EXECUTION SUMMARY BY TIER")
    print("=" * 70)
    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for tier_name, data in collector.results.items():
        p, f, s = data["passed"], data["failed"], data["skipped"]
        total = p + f + s
        if total > 0:
            total_passed += p
            total_failed += f
            total_skipped += s
            status_str = f"PASSED: {p:2d} | FAILED: {f:2d} | SKIPPED: {s:2d} (Total: {total:2d})"
            print(f"  [{tier_name:<30}]  {status_str}")

    print("-" * 70)
    total_all = total_passed + total_failed + total_skipped
    print(f"  TOTAL EXECUTED: {total_all}")
    print(f"  TOTAL PASSED:   {total_passed}")
    print(f"  TOTAL FAILED:   {total_failed}")
    print(f"  TOTAL SKIPPED:  {total_skipped}")
    print(f"  TOTAL DURATION: {duration:.2f} seconds")
    print("=" * 70)

    if collector.failures:
        print("\n" + "!" * 70)
        print("  FAILURES DETECTED (ESCALATION REPORT):")
        print("!" * 70)
        for nodeid, trace in collector.failures:
            print(f"\n[-] FAILURE: {nodeid}")
            # Print brief trace
            lines = trace.strip().splitlines()
            for line in lines[-10:]:
                print(f"    {line}")
        print("!" * 70)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
