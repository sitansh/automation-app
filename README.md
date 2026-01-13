
# Requirement vs Schema Comparator

Compare requirements (CSV/XLSX) with a JSON schema and generate detailed mismatch reports. Includes a FastAPI backend and a React frontend for easy use and visualization.

---

## Features
- **CLI Tool**: Compare requirements with schema and generate Excel/CSV reports.
- **Web UI**: Upload requirements, specify schema URL, and view results interactively.
- **Downloadable Reports**: Get Excel reports and visual summaries.

---

## Backend (FastAPI)

### Setup
1. (Recommended) Create a virtual environment:
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```
2. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
3. Start the backend server:
	```bash
	uvicorn src.ui:app --reload --host 0.0.0.0 --port 8000
	```

### CLI Usage
Run comparisons directly from the command line:
```bash
python main.py --req requirements.csv --schema-url <url> --out report.xlsx
```
Options:
- `--format` : `excel` or `csv` output (auto by file extension)
- `--no-fail` : do not exit non-zero on mismatch/missing
- `--debug` : enable debug logging

---

## Frontend (React + Vite)

### Setup
1. Go to the frontend directory:
	```bash
	cd frontend
	npm install
	npm run dev
	```
2. The dev server runs at [http://localhost:3000](http://localhost:3000) and proxies API requests to the backend.

### Build for Production
```bash
cd frontend
npm run build
```
Serve the `dist/` folder with any static server or configure FastAPI to serve static files.

---

## Example Schema URL
```
https://cdn-prod-static.phenompeople.com/CareerConnectResources/VERIGLOBAL/workday/external/careersite/singlepage/schema/form_schema.json
```

---

## Project Structure

- `src/` - Backend Python modules
- `frontend/` - React frontend app
- `reports/` - Generated reports
- `requirements.txt` - Python dependencies
- `README.md` - This file

---

## License
MIT
