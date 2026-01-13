# Requirement vs Schema Comparator

CLI tool to compare a requirements CSV/XLSX with an application form schema JSON and generate a mismatch report.

Usage:

```
python main.py --req requirements.csv --schema-url <url> --out report.xlsx
```

Options:
- `--format` : `excel` or `csv` output (auto by file extension)
- `--no-fail` : do not exit non-zero on mismatch/missing
- `--debug` : enable debug logging

Example schema URL (provided):
https://cdn-prod-static.phenompeople.com/CareerConnectResources/VERIGLOBAL/workday/external/careersite/singlepage/schema/form_schema.json
