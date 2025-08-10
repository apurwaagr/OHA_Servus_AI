import folium
from itertools import cycle

def plot_lines(lines_dict, zoom_start=13, outfile="lines_map.html", tiles="OpenStreetMap"):
    """
    Plot multiple labeled polylines on an interactive folium map.

    Parameters
    ----------
    lines_dict : dict[str, list[tuple[float,float]]]
        Keys are line labels; values are sequences of (lat, lon) pairs.
        (NumPy float types are fine; they’ll be cast to float.)
    zoom_start : int
        Initial zoom (only used before fit_bounds runs).
    outfile : str
        Path where the HTML map should be saved.
    tiles : str
        Folium basemap tiles (e.g., "OpenStreetMap", "CartoDB positron", "Stamen Terrain").
    """
    if not lines_dict:
        raise ValueError("lines_dict is empty.")

    # Flatten all points for centering / bounds
    all_pts = []
    for pts in lines_dict.values():
        all_pts.extend((float(lat), float(lon)) for lat, lon in pts)

    # Fallback center = mean of all points
    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lon = sum(p[1] for p in all_pts) / len(all_pts)

    m = folium.Map(location=(center_lat, center_lon), zoom_start=zoom_start, tiles=tiles)

    # Nice set of folium-compatible colors, will cycle if you have many lines
    palette = cycle([
        "blue","red","green","purple","orange","darkred","lightred","beige","darkblue",
        "darkgreen","cadetblue","darkpurple","pink","lightblue","lightgreen","gray","black","lightgray"
    ])

    # Add each line in its own Layer so you can toggle them
    for label, pts in lines_dict.items():
        pts_clean = [(float(lat), float(lon)) for lat, lon in pts]
        color = next(palette)

        layer = folium.FeatureGroup(name=label, show=True)
        folium.PolyLine(pts_clean, color=color, weight=3, opacity=0.9, tooltip=label).add_to(layer)

        # Optional: mark start/end
        if pts_clean:
            folium.CircleMarker(pts_clean[0], radius=4, tooltip=f"{label} start").add_to(layer)
            folium.CircleMarker(pts_clean[-1], radius=4, tooltip=f"{label} end").add_to(layer)

        layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    # Fit to all points
    m.fit_bounds([min(all_pts, key=lambda p: p[0]),
                  max(all_pts, key=lambda p: p[0])])  # folium accepts two corners just fine

    m.save(outfile)
    return m

def plot_lines_with_highlight(
    lines_dict, 
    zoom_start=13, 
    outfile="lines_map.html", 
    tiles="OpenStreetMap", 
    highlight=None
):
    """
    Like plot_lines, but all lines are black except those in highlight (red).
    highlight: list of labels to highlight (default: []).
    """
    if not lines_dict:
        raise ValueError("lines_dict is empty.")

    if highlight is None:
        highlight = []

    all_pts = []
    for pts in lines_dict.values():
        all_pts.extend((float(lat), float(lon)) for lat, lon in pts)

    center_lat = sum(p[0] for p in all_pts) / len(all_pts)
    center_lon = sum(p[1] for p in all_pts) / len(all_pts)

    m = folium.Map(location=(center_lat, center_lon), zoom_start=zoom_start, tiles=tiles)

    for label, pts in lines_dict.items():
        pts_clean = [(float(lat), float(lon)) for lat, lon in pts]
        if label in highlight:
            color = "red"
            weight = 4
            opacity = 1.0
        else:
            color = "black"
            weight = 3
            opacity = 0.7

        layer = folium.FeatureGroup(name=label, show=True)
        folium.PolyLine(pts_clean, color=color, weight=weight, opacity=opacity, tooltip=label).add_to(layer)

        if pts_clean:
            folium.CircleMarker(pts_clean[0], radius=4, tooltip=f"{label} start").add_to(layer)
            folium.CircleMarker(pts_clean[-1], radius=4, tooltip=f"{label} end").add_to(layer)

        layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.fit_bounds([min(all_pts, key=lambda p: p[0]),
                  max(all_pts, key=lambda p: p[0])])

    m.save(outfile)
    return m


def get_route_stop_positions_by_short_name(gtfs_data, route_short_name, skip_stop_ids=None):
    """
    gtfs_data: dict containing GTFS CSVs as pandas DataFrames:
        {
            "routes": DataFrame,
            "trips": DataFrame,
            "stop_times": DataFrame,
            "stops": DataFrame
        }
    route_short_name: string, the GTFS route_short_name
    
    Returns: list of (stop_lat, stop_lon) tuples in order
    """
    # 1. Get the route_id for this short name
    routes_df = gtfs_data["routes"]
    matching_routes = routes_df[routes_df["route_short_name"] == route_short_name]
    if matching_routes.empty:
        return []

    route_id = matching_routes.iloc[0]["route_id"]

    # 2. Find trips for the given route
    trips_for_route = gtfs_data["trips"][gtfs_data["trips"]["route_id"] == route_id]
    if trips_for_route.empty:
        return []

    # Pick the first trip as a representative
    trip_id = trips_for_route.iloc[0]["trip_id"]

    # 3. Get ordered stops for that trip
    stop_times = gtfs_data["stop_times"][gtfs_data["stop_times"]["trip_id"] == trip_id]


    stop_times_sorted = stop_times.sort_values("stop_sequence")

    # sort out skipped stops
    if skip_stop_ids is not None:
        stop_times_sorted = stop_times_sorted[~stop_times_sorted["stop_id"].isin(skip_stop_ids)]


    # 4. Get stop positions
    stops_df = gtfs_data["stops"].set_index("stop_id")
    ordered_positions = [
        (stops_df.loc[stop_id, "stop_lat"], stops_df.loc[stop_id, "stop_lon"])
        for stop_id in stop_times_sorted["stop_id"]
        if stop_id in stops_df.index
    ]

    return ordered_positions

def get_ordered_positions(gtfs_data, stop_ids):
    """
    Given a list of stop_ids and a mapping of stop_id to position,
    return a list of positions in the same order as stop_ids.
    """
    stops_df = gtfs_data["stops"].set_index("stop_id")
    return [(stops_df.loc[stop_id, "stop_lat"], stops_df.loc[stop_id, "stop_lon"]) for stop_id in stop_ids]


def get_multiple_routes_positions(gtfs_data, route_short_names, skip_stop_ids=None, addedRoutes=None):
    """
    gtfs_data: dict of GTFS DataFrames
    route_short_names: list of route_short_name strings
    
    Returns: dict mapping route_short_name -> list of (lat, lon) tuples
    """
    result = {}
    for short_name in route_short_names:
        result[short_name] = get_route_stop_positions_by_short_name(gtfs_data, short_name, skip_stop_ids=skip_stop_ids)
    if addedRoutes is not None:
        for short_name, stop_ids in addedRoutes.items():
            result[short_name] = get_ordered_positions(gtfs_data, stop_ids)
    if addedRoutes is not None:
        for short_name, stop_ids in addedRoutes.items():
            result[short_name] = get_ordered_positions(gtfs_data, stop_ids)

    return result

