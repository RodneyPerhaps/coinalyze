import pandas as pd

from coinalyze.constants import COLS_MAPPING
from coinalyze.enums import HistoryEndpoint


def history_response_to_df(
    response: list[dict], endpoint: HistoryEndpoint, index_col: str | None = None
) -> pd.DataFrame:
    """
    Parse a history response to a DataFrame.

    Args:
        response: The JSON response from an history endpoint.
        endpoint: The endpoint to use for the mapping.
        index_col: The column to use as the index.
    """
    dfs = []
    for r in response:
        df = pd.DataFrame(r["history"])
        cols_mapping = {"t": "timestamp"}
        # Depending on the endpoint decide which mapping to use
        cols_mapping.update(COLS_MAPPING[endpoint])
        df = df.rename(columns=cols_mapping)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df.insert(0, "symbol", r["symbol"])
        if index_col:
            df = df.set_index(index_col)

        dfs.append(df)

    if len(dfs) == 0:
        raise ValueError("No data found")

    df = pd.concat(dfs, axis=0)
    if index_col is None:
        df = df.reset_index(drop=True)

    return df


def response_to_df(response: list[dict], data_type: str | None = None) -> pd.DataFrame:
    """Parse a Coinalyze response to a DataFrame."""
    df = pd.DataFrame(response)
    for col in ["expire_at", "update"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], unit="ms")
    if data_type:
        df.insert(0, "data_type", data_type)
    return df
