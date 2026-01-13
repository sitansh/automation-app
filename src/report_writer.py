import logging
from typing import List, Dict, Any
import pandas as pd

LOG = logging.getLogger(__name__)


def write_report(rows: List[Dict[str, Any]], out_path: str, fmt: str = "excel") -> None:
    df = pd.DataFrame(rows)
    if fmt == "csv" or out_path.lower().endswith('.csv'):
        df.to_csv(out_path, index=False)
    else:
        # excel
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="comparison")


__all__ = ["write_report"]
