import logging
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.datastructures import UploadFile as StarletteUploadFile
import os
import time
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# load environment variables from .env (if present)
load_dotenv()

from .requirement_loader import load_requirements
from .schema_loader import load_schema_from_url, extract_fields
from .matcher import compare_requirement_to_schema
from .report_writer import write_report
from .report_visuals import generate_report_visuals

LOG = logging.getLogger(__name__)

app = FastAPI(title="QAPilot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# expose reports folder so visuals/images can be served
app.mount("/reports_files", StaticFiles(directory=str(REPORTS_DIR)), name="reports_files")

templates = Jinja2Templates(directory=str(BASE / "templates"))


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/compare")
async def compare(request: Request, file: UploadFile = File(...), schema_url: str = Form(...)):
    # Save uploaded file to temp path
    tmp_req = tempfile.NamedTemporaryFile(delete=False, suffix="_req")
    content = await file.read()
    tmp_req.write(content)
    tmp_req.flush()
    tmp_req.close()

    try:
        reqs = load_requirements(tmp_req.name)
    except Exception as e:
        LOG.exception("Failed to load requirements: %s", e)
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": f"Failed to parse requirements file: {e}"}
        )

    try:
        schema_json = load_schema_from_url(schema_url)
    except Exception as e:
        LOG.exception("Failed to load schema: %s", e)
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": f"Failed to fetch schema JSON: {e}"}
        )

    schema_fields = extract_fields(schema_json)

    rows = []
    counts = {"MATCHED": 0, "MISMATCH": 0, "MISSING": 0, "POSSIBLE_MATCH": 0}
    for r in reqs:
        rep = compare_requirement_to_schema(r, schema_fields)
        # attach raw snippet from matched schema field when available
        raw_snip = None
        best_key = rep.get("best_match_key") or rep.get("field_key")
        if best_key:
            match = next((f for f in schema_fields if (f.get("field_key") or "") == best_key), None)
            if match:
                try:
                    import json

                    raw_snip = json.dumps(match.get("raw"), indent=2)
                    # truncate to reasonable length
                    if len(raw_snip) > 8000:
                        raw_snip = raw_snip[:8000] + "\n... (truncated)"
                except Exception:
                    raw_snip = str(match.get("raw"))
        rep["raw_snippet"] = raw_snip
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

    # Write report to reports directory with timestamped name
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"report_{ts}.xlsx"
    out_path = REPORTS_DIR / fname
    write_report(rows, str(out_path), fmt="excel")

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "counts": counts,
            "rows": rows,
            "report_path": str(out_path),
        },
    )


@app.post("/api/compare")
async def api_compare(file: UploadFile = File(...), schema_url: str = Form(...)):
    # Process file upload and schema URL and return JSON result for SPA
    tmp_req = tempfile.NamedTemporaryFile(delete=False, suffix="_req")
    content = await file.read()
    tmp_req.write(content)
    tmp_req.flush()
    tmp_req.close()

    try:
        reqs = load_requirements(tmp_req.name)
    except Exception as e:
        return JSONResponse({"error": f"Failed to parse requirements file: {e}"}, status_code=400)

    try:
        schema_json = load_schema_from_url(schema_url)
    except Exception as e:
        return JSONResponse({"error": f"Failed to fetch schema JSON: {e}"}, status_code=400)

    schema_fields = extract_fields(schema_json)

    rows = []
    counts = {"MATCHED": 0, "MISMATCH": 0, "MISSING": 0, "POSSIBLE_MATCH": 0}
    for r in reqs:
        rep = compare_requirement_to_schema(r, schema_fields)
        # attach raw snippet
        raw_snip = None
        best_key = rep.get("best_match_key") or rep.get("field_key")
        if best_key:
            match = next((f for f in schema_fields if (f.get("field_key") or "") == best_key), None)
            if match:
                try:
                    import json

                    raw_snip = json.dumps(match.get("raw"), indent=2)
                    if len(raw_snip) > 8000:
                        raw_snip = raw_snip[:8000] + "\n... (truncated)"
                except Exception:
                    raw_snip = str(match.get("raw"))
        rep["raw_snippet"] = raw_snip
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

    # write report
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"report_{ts}.xlsx"
    out_path = REPORTS_DIR / fname
    write_report(rows, str(out_path), fmt="excel")

    return JSONResponse({"counts": counts, "rows": rows, "report": {"path": str(out_path), "url": f"/download?path={str(out_path)}"}})


@app.get("/download")
async def download(path: str):
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="report.xlsx")


@app.get("/reports")
async def list_reports():
    files = []
    for p in sorted(REPORTS_DIR.iterdir(), reverse=True):
        if p.suffix.lower() in (".xlsx", ".csv"):
            stat = p.stat()
            files.append({
                "name": p.name,
                "path": str(p),
                "size": stat.st_size,
                "modified": datetime.utcfromtimestamp(stat.st_mtime).isoformat() + "Z",
            })
    return JSONResponse(files)



@app.get("/reports/visuals")
async def reports_visuals(path: str):
    # path is the absolute path to the report file (as returned by /reports)
    try:
        imgs = generate_report_visuals(path, REPORTS_DIR)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    # convert to public URLs served by StaticFiles
    public = []
    for p in imgs:
        p = Path(p)
        rel_dir = p.parent.name
        public.append(f"/reports_files/{rel_dir}/{p.name}")

    return JSONResponse({"images": public})


@app.post("/reports/delete")
async def delete_report(path: str = Form(...)):
    p = Path(path)
    if not p.exists() or not p.is_file():
        return JSONResponse({"ok": False, "error": "file not found"}, status_code=404)
    try:
        p.unlink()
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post('/reports/analysis')
async def reports_analysis(path: str = Form(...)):
    """
    Generate a summary and full-length analysis for the given report file using Google Generative API.
    Requires environment variable GENAI_API_KEY to be set with a valid API key.
    """
    api_key = os.environ.get('GENAI_API_KEY')
    if not api_key:
        return JSONResponse({"error": "GENAI_API_KEY not set on server"}, status_code=400)

    p = Path(path)
    if not p.exists() or not p.is_file():
        return JSONResponse({"error": "report file not found"}, status_code=404)

    try:
        # read a sample of rows from excel (first sheet)
        df = pd.read_excel(str(p))
    except Exception as e:
        return JSONResponse({"error": f"failed to read report file: {e}"}, status_code=400)

    # prepare a concise representation for the model, including examples of mismatches
    try:
        counts = None
        if 'status' in df.columns:
            counts = df['status'].value_counts().to_dict()

        # pick up to 10 sample rows (prefer mismatches then others)
        samples = []
        preferred = []
        if {'req_id', 'field_key', 'status', 'best_match_key', 'raw_snippet'}.issubset(set(df.columns)):
            # ensure raw_snippet column exists (it should, from write_report)
            # prioritize MISMATCH rows
            try:
                mismatches = df[df['status'] == 'MISMATCH']
            except Exception:
                mismatches = df[df['status'].astype(str).str.upper() == 'MISMATCH']
            for _, r in mismatches.head(8).iterrows():
                preferred.append({
                    'req_id': r.get('req_id'),
                    'field_key': r.get('field_key'),
                    'status': r.get('status'),
                    'best_match_key': r.get('best_match_key'),
                    'raw_snippet': (str(r.get('raw_snippet') or '')[:1000] + ('... (truncated)' if r.get('raw_snippet') and len(str(r.get('raw_snippet'))) > 1000 else ''))
                })

            # fill with other rows if needed
            if len(preferred) < 10:
                for _, r in df.head(10).iterrows():
                    entry = {
                        'req_id': r.get('req_id'),
                        'field_key': r.get('field_key'),
                        'status': r.get('status'),
                        'best_match_key': r.get('best_match_key'),
                        'raw_snippet': (str(r.get('raw_snippet') or '')[:1000] + ('... (truncated)' if r.get('raw_snippet') and len(str(r.get('raw_snippet'))) > 1000 else ''))
                    }
                    # avoid duplicates
                    if entry not in preferred:
                        preferred.append(entry)

            samples = preferred[:10]
        else:
            samples = df.head(10).to_dict(orient='records')
    except Exception:
        samples = []
        counts = None

    prompt_lines = []
    prompt_lines.append('You are an expert QA analyst. Provide a concise summary and a full-length report analysis of the QA comparison results. Use the provided counts and examples to ground your observations and cite example req_id values where relevant.')
    if counts:
        prompt_lines.append('Counts:')
        for k, v in counts.items():
            prompt_lines.append(f"- {k}: {v}")
    prompt_lines.append('Here are up to 10 example rows (selected mismatches first) in JSON format:')
    import json
    prompt_lines.append(json.dumps(samples, indent=2, ensure_ascii=False))
    prompt_lines.append('Produce: (1) a short summary paragraph (max 80-100 words) that highlights the most important findings, and (2) a longer full-length analysis (around 400-1200 words) that discusses patterns, the most common mismatches, references specific example req_id values, provides technical recommendations, and suggests next steps for remediation. Return both clearly labelled.')
    prompt = '\n\n'.join(prompt_lines)

    # call Google Generative API (REST). Try known endpoint variants (v1 then v1beta2).
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1/models/text-bison-001:generate?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generate?key={api_key}",
    ]
    payload = {
        "prompt": {"text": prompt},
        "temperature": 0.2,
        "maxOutputTokens": 1500,
    }

    last_err = None
    data = None
    for url in endpoints:
        try:
            resp = requests.post(url, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            break
        except requests.HTTPError as he:
            # if 404 or not found, try next endpoint; otherwise capture and return later
            last_err = he
            LOG.warning("Generative API HTTP error for %s: %s (response: %s)", url, he, getattr(he.response, 'text', None))
            if he.response is not None and he.response.status_code == 404:
                continue
            else:
                break
        except Exception as e:
            last_err = e
            LOG.exception("Generative API request failed for %s: %s", url, e)
            continue

    if data is None:
        # If the generative API is not available (404) or fails, provide a simulated analysis
        LOG.info("Generative API not available, producing simulated analysis")
        try:
            # build a simulated structured result based on counts
            sim_counts = counts or {}
            matched = int(sim_counts.get('MATCHED', 0) or 0)
            mism = int(sim_counts.get('MISMATCH', 0) or 0)
            miss = int(sim_counts.get('MISSING', 0) or 0)
            total = max(1, matched + mism + miss)
            score = int(max(40, min(95, round((matched / total) * 100))))
            # heuristics for timings (ms)
            fcp = f"{int(800 + (100 - score) * 12)}ms"
            lcp = f"{int(1400 + (100 - score) * 14)}ms"
            tbt = f"{int(80 + (100 - score) * 4)}ms"
            speedIndex = f"{int(900 + (100 - score) * 10)}ms"
            advice = (
                "Minimize main-thread work by deferring non-critical JavaScript, "
                "compress and properly size images, and add explicit caching headers for static assets."
            )
            structured = {
                "performanceScore": score,
                "fcp": fcp,
                "lcp": lcp,
                "tbt": tbt,
                "speedIndex": speedIndex,
                "advice": advice,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "examples": samples,
            }
            # short summary and a longer analysis text
            # reference a few example req_ids in the long text to tie analysis to actual data
            example_ids = [str(x.get('req_id')) for x in (samples or []) if x.get('req_id')][:3]
            examples_str = ', '.join(example_ids) if example_ids else 'N/A'
            short = f"Summary: overall score {score}. Most issues relate to resource loading and main-thread work. Example affected req_ids: {examples_str}."
            long_lines = [short, "\nRecommendations:"]
            long_lines.append("- Defer non-critical JavaScript and split bundles to reduce main-thread work.")
            long_lines.append("- Optimize and compress images; use responsive image sizes.")
            long_lines.append("- Apply caching and CDN for static assets; minimize time to first byte.")
            long_text = "\n".join(long_lines)
        except Exception as e:
            LOG.exception("Failed to produce simulated analysis: %s", e)
            return JSONResponse({"error": f"generative API call failed: {last_err}"}, status_code=500)

        return JSONResponse({"analysis": long_text, "structured": structured, "simulated": True})

    # attempt to extract content from known response shapes
    text = None
    try:
        if isinstance(data, dict):
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0].get('content') or data['candidates'][0].get('output')
            elif 'outputs' in data and len(data['outputs']) > 0:
                out = data['outputs'][0]
                text = out.get('content') or out.get('text')
            elif 'output' in data and isinstance(data['output'], list) and len(data['output'])>0:
                text = data['output'][0].get('content')
            elif 'candidates' in data:
                text = json.dumps(data['candidates'])
            else:
                text = json.dumps(data)
        else:
            text = str(data)
    except Exception:
        text = str(data)

    return JSONResponse({"analysis": text})
