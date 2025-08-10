import pandas as pd
import numpy as np
import math
import csv

def _to_gtfs_time(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return ""
        parts = s.split(":")
        if len(parts) == 3:
            try:
                h, m, sec_part = parts
                h = int(h); m = int(m); ssec = int(float(sec_part))
                return f"{h:02d}:{m:02d}:{ssec:02d}"
            except:
                pass
        try:
            td = pd.to_timedelta(s)
            total = int(td.total_seconds())
            h = total // 3600
            m = (total % 3600) // 60
            s = total % 60
            return f"{h:02d}:{m:02d}:{s:02d}"
        except:
            return s
    if isinstance(v, pd.Timedelta):
        total = int(v.total_seconds())
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    import datetime as _dt
    if isinstance(v, pd.Timestamp):
        t = v.to_pydatetime().time()
        return f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"
    if isinstance(v, _dt.datetime):
        t = v.time()
        return f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"
    if isinstance(v, _dt.time):
        return f"{v.hour:02d}:{v.minute:02d}:{v.second:02d}"
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
    return str(v)

def _to_gtfs_date(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return ""
        if len(s) == 8 and s.isdigit():
            return s
        try:
            ts = pd.to_datetime(s, errors="raise")
            return ts.strftime("%Y%m%d")
        except:
            return s
    if isinstance(v, (pd.Timestamp, )):
        return v.strftime("%Y%m%d")
    import datetime as _dt
    if isinstance(v, _dt.datetime):
        return v.strftime("%Y%m%d")
    if isinstance(v, _dt.date):
        return v.strftime("%Y%m%d")
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
        return s
    if isinstance(v, (bool, np.bool_)):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer, float, np.floating)):
        return "1" if int(round(float(v))) != 0 else "0"
    return str(v)

def _to_int_str(v):
    if pd.isna(v):
        return ""
    try:
        return str(int(round(float(v))))
    except:
        s = str(v).strip()
        return "" if s.lower() in {"nan","none"} else s

def _to_float_str(v):
    if pd.isna(v):
        return ""
    try:
        return f"{float(v):.12f}".rstrip("0").rstrip(".")
    except:
        return str(v)

def _identity_str(v):
    if pd.isna(v):
        return ""
    return str(v)

def format_df_for_gtfs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a GTFS dataframe to correct string formatting for CSV export.
    Also extracts stop_lat/stop_lon from GeoPandas Point geometries if present.
    """
    out = df.copy()

    # If geometry column exists, extract lat/lon
    if "geometry" in out.columns:
        try:
            from shapely.geometry import Point
            lats = []
            lons = []
            for g in out["geometry"]:
                if g is None or pd.isna(g):
                    lats.append(np.nan)
                    lons.append(np.nan)
                elif hasattr(g, "x") and hasattr(g, "y"):
                    lats.append(g.y)  # lat
                    lons.append(g.x)  # lon
                else:
                    lats.append(np.nan)
                    lons.append(np.nan)
            out["stop_lat"] = (
                out.get("stop_lat", pd.Series(index=out.index, dtype="float64"))
                .fillna(pd.Series(lons, index=out.index, dtype="float64"))
                )

            out["stop_lon"] = (
                out.get("stop_lon", pd.Series(index=out.index, dtype="float64"))
                .fillna(pd.Series(lons, index=out.index, dtype="float64"))
                )
            out = out.drop(columns=["geometry"])
        except ImportError:
            pass  # If shapely isn't installed

    time_cols = {"arrival_time","departure_time","start_time","end_time"}
    date_cols = {"date","start_date","end_date"}
    zero_one_cols = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday",
                     "pickup_type","drop_off_type","wheelchair_accessible","bikes_allowed"}
    int_cols = {"stop_sequence","direction_id","route_type","exception_type","location_type","transfer_type"}
    float_cols = {"stop_lat","stop_lon","shape_dist_traveled","shape_pt_lat","shape_pt_lon"}

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

    return out.astype(str)
