import argparse
import logging
import sys
from typing import List

from .requirement_loader import load_requirements
from .schema_loader import load_schema_from_url, extract_fields
from .matcher import compare_requirement_to_schema
from .report_writer import write_report

LOG = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def run(req_path: str, schema_url: str, out_path: str, fmt: str = "excel", fail_on: bool = True, debug: bool = False) -> int:
    setup_logging(debug)
    LOG.info("Loading requirements from %s", req_path)
    reqs = load_requirements(req_path)
    LOG.info("Fetching schema from %s", schema_url)
    schema_json = load_schema_from_url(schema_url)
    LOG.info("Extracting fields from schema")
    schema_fields = extract_fields(schema_json)
    LOG.info("Found %d schema fields", len(schema_fields))

    rows: List[dict] = []
    counts = {"MATCHED": 0, "MISMATCH": 0, "MISSING": 0, "POSSIBLE_MATCH": 0}
    for r in reqs:
        rep = compare_requirement_to_schema(r, schema_fields)
        rows.append(rep)
        st = rep.get("status")
        if st == "MATCHED":
            counts["MATCHED"] += 1
        elif st == "MISMATCH":
            counts["MISMATCH"] += 1
        elif st == "POSSIBLE_MATCH":
            counts["POSSIBLE_MATCH"] += 1
        elif st == "MISSING":
            counts["MISSING"] += 1

    LOG.info("Writing report to %s", out_path)
    write_report(rows, out_path, fmt=fmt)

    # print summary
    print(f"MATCHED: {counts['MATCHED']}")
    print(f"MISMATCH: {counts['MISMATCH']}")
    print(f"MISSING: {counts['MISSING']}")
    print(f"POSSIBLE_MATCH: {counts['POSSIBLE_MATCH']}")

    if fail_on and (counts["MISMATCH"] > 0 or counts["MISSING"] > 0):
        LOG.error("Failing because mismatches or missing fields found")
        return 2
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare requirements with schema JSON and produce a report")
    parser.add_argument("--req", required=True, help="Path to requirements CSV/XLSX")
    parser.add_argument("--schema-url", required=True, help="URL to schema JSON")
    parser.add_argument("--out", required=True, help="Output report path (xlsx or csv)")
    parser.add_argument("--format", choices=["excel", "csv"], default=None, help="Output format")
    parser.add_argument("--no-fail", dest="fail", action="store_false", help="Do not exit non-zero on mismatch/missing")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args(argv)
    fmt = args.format or ("csv" if args.out.lower().endswith('.csv') else "excel")
    code = run(args.req, args.schema_url, args.out, fmt=fmt, fail_on=args.fail, debug=args.debug)
    sys.exit(code)


__all__ = ["main", "run"]
