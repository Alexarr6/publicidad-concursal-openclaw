from datetime import date

import pandas as pd
import pytest

from publicidadconcursal_exporter.parsing.normalize import EmptyExportError, normalize_dataframe


def test_normalize_sorts_by_fecha_column() -> None:
    df = pd.DataFrame(
        {
            "fecha": ["05/03/2026", "03/03/2026", "04/03/2026"],
            "id": [3, 1, 2],
        }
    )

    out = normalize_dataframe(df, date(2026, 3, 5))

    assert out["id"].tolist() == [1, 2, 3]
    assert out["run_date"].nunique() == 1
    assert out["run_date"].iloc[0] == "2026-03-05"


def test_normalize_raises_on_empty() -> None:
    with pytest.raises(EmptyExportError):
        normalize_dataframe(pd.DataFrame(), date(2026, 3, 5))
