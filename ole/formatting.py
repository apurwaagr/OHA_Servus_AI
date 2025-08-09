import pandas as pd
import numpy as np
import math
import csv

def _to_gtfs_time(v):
    """
    Accepts strings like '05:31:00', pandas Timestamp/Time/Timedelta,
    python datetime.time, or seconds as int/float.
    Returns 'HH:MM:SS' (supports >24h for Timedelta).
    """
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    # already a string and looks like H:M:S
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return ""
        # tolerate '5:3:0', pad to HH:MM:SS
        parts = s.split(":")
        if len(parts) == 3 and all(parts):
            try:
                h = int(parts[0])
                m = int(parts[1])
                sec_part = parts[2]
                # handle 'SS' or 'SS.s'
                ssec = int(float(sec_part))
                return f"{h:02d}:{m:02d}:{ssec:02d}"
            except Exception:
                pass  # fall through
        # Try parsing via pandas
        try:
            td = pd.to_timedelta(s)
            total = int(td.total_seconds())
            h = total // 3600
            m = (total % 3600) // 60
            s = total % 60
            return f"{h:02d}:{m:02d}:{s:02d}"
        except Exception:
            return s  # leave as-is
    # pandas Timedelta
    if isinstance(v, pd.Timedelta):
        total = int(v.total_seconds())
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    # pandas Timestamp or Python datetime/time
    try:
        import datetime as _dt
        if isinstance(v, pd.Timestamp):
            t = v.to_pydatetime().time()
            return f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"
        if isinstance(v, _dt.datetime):
            t = v.time()
            return f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"
        if isinstance(v, _dt.time):
            return f"{v.hour:02d}:{v.minute:02d}:{v.second:02d}"
    except Exception:
        pass
    # numeric seconds
    if isinstance(v, (int, np.integer)):
        total = int(v)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    if isinstance(v, (float, np.floating)) and not math.isnan(v):
        total = int(round(v))
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    # last resort
    return str(v)

def _to_gtfs_date(v):
    """
    Accepts string 'YYYYMMDD', pandas/py datetime/date, etc.
    Returns 'YYYYMMDD' or ''.
    """
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return ""
        # If already YYYYMMDD -> return as-is
        if len(s) == 8 and s.isdigit():
            return s
        # Try common date-ish strings
        try:
            ts = pd.to_datetime(s, errors="raise")
            return ts.strftime("%Y%m%d")
        except Exception:
            return s
    if isinstance(v, (pd.Timestamp, )):
        return v.strftime("%Y%m%d")
    try:
        import datetime as _dt
        if isinstance(v, _dt.datetime):
            return v.strftime("%Y%m%d")
        if isinstance(v, _dt.date):
            return v.strftime("%Y%m%d")
    except Exception:
        pass
    return str(v)

def _to_zero_one_str(v):
    if pd.isna(v):
        return ""
    if isinstance(v, str):
        s = v.strip()
        if s in {"0","1"}:
            return s
        if s.lower() in {"true","t","yes","y"}:
            return "1"
        if s.lower() in {"false","f","no","n"}:
            return "0"
        # if empty or other -> return as-is
        return s
    if isinstance(v, (bool, np.bool_)):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer, float, np.floating)):
        try:
            return "1" if int(round(float(v))) != 0 else "0"
        except Exception:
            return ""
    return str(v)

def _to_int_str(v):
    if pd.isna(v):
        return ""
    try:
        return str(int(round(float(v))))
    except Exception:
        s = str(v).strip()
        return "" if s.lower() in {"nan","none"} else s

def _to_float_str(v):
    if pd.isna(v):
        return ""
    try:
        # Avoid scientific notation; trim trailing zeros & dot.
        s = f"{float(v):.12f}".rstrip("0").rstrip(".")
        return s if s else "0"
    except Exception:
        return str(v)

def _identity_str(v):
    if pd.isna(v):
        return ""
    return str(v)

def format_df_for_gtfs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a copy of df with **all values converted to properly formatted strings**
    per GTFS conventions, preserving column order. Safe to write with:
        df_formatted.to_csv(path, index=False, quoting=csv.QUOTE_ALL, lineterminator='\\n')
    """
    out = df.copy()

    # If a geometry column exists and stop_lat/stop_lon are present, populate from Point geometries.
    if "geometry" in out.columns and {"stop_lat","stop_lon"}.issubset(out.columns):
        geom = out["geometry"]
        # Anything with x/y attributes (e.g., shapely Point) will work
        def _gx(g):
            try:
                return g.y if hasattr(g, "y") else (g.lat if hasattr(g, "lat") else np.nan)
            except Exception:
                return np.nan
        def _gy(g):
            try:
                return g.x if hasattr(g, "x") else (g.lon if hasattr(g, "lon") else np.nan)
            except Exception:
                return np.nan
        # Note: GTFS uses lat, lon; shapely Points are (x=lon, y=lat)
        out.loc[:, "stop_lat"] = out.get("stop_lat", pd.Series(index=out.index)).fillna(geom.map(_gx))
        out.loc[:, "stop_lon"] = out.get("stop_lon", pd.Series(index=out.index)).fillna(geom.map(_gy))

    # Buckets by GTFS column names
    time_cols = {"arrival_time","departure_time","start_time","end_time"}
    date_cols = {"date","start_date","end_date"}
    zero_one_cols = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday",
                     "pickup_type","drop_off_type","wheelchair_accessible","bikes_allowed"}
    int_cols = {"stop_sequence","direction_id","route_type","exception_type","location_type","transfer_type"}
    float_cols = {"stop_lat","stop_lon","shape_dist_traveled","shape_pt_lat","shape_pt_lon"}
    # You can expand the above sets as needed for your feed.

    # Apply conversions where relevant
    for c in out.columns:
        if c in time_cols:
            out[c] = out[c].map(_to_gtfs_time)
        elif c in date_cols:
            out[c] = out[c].map(_to_gtfs_date)
        elif c in zero_one_cols:
            out[c] = out[c].map(_to_zero_one_str)
        elif c in int_cols:
            out[c] = out[c].map(_to_int_str)
        elif c in float_cols:
            out[c] = out[c].map(_to_float_str)
        else:
            out[c] = out[c].map(_identity_str)

    # Ensure everything is dtype string for consistent CSV output
    return out.astype(str)

# Example usage:
# df_formatted = format_df_for_gtfs(df_trips_or_stops_or_calendar)
# df_formatted.to_csv("trips.txt", index=False, quoting=csv.QUOTE_ALL, lineterminator="\n")
