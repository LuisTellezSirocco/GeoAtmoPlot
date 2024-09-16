import os
import folium
import simplekml
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict

class GridPointSelector:
    def __init__(
        self,
        lat_range: Tuple[float, float],
        lon_range: Tuple[float, float],
        step: float,
    ):
        self.lats = np.arange(*lat_range, step)
        self.lons = np.arange(*lon_range, step)
        self.points = [(lat, lon) for lat in self.lats for lon in self.lons]

    def select_closest_points(
        self, latitude: float, longitude: float, n_points: int = 4
    ) -> List[Tuple[float, float]]:
        distances = [
            np.sqrt((point[0] - latitude) ** 2 + (point[1] - longitude) ** 2)
            for point in self.points
        ]
        closest_indices = np.argsort(distances)[:n_points]
        return [self.points[i] for i in closest_indices]

class MapGenerator:
    def __init__(self):
        # TODO: Garantizar que los modelos y resolución sean correctos
        self.model_selectors = {
            "ECMWF": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1),
            "GFS_0.5": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.5),
            "GFS_0.25": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.25),
            "UKMET": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.2),
            "NCEP": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.25),
            "DWD": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1),
            "METEOFRANCE": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1),
            "CMCC": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.25),
            "JMA": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.2),
        }

    def create_map(
        self,
        latitude: float,
        longitude: float,
        n_points: int = 4,
        filename: str = "closest_points_map.html",
        path_file: str = None,
        models: List[str] = ["ECMWF", "GFS"],
    ):
        closest_points = {
            model: self.model_selectors[model].select_closest_points(latitude, longitude, n_points)
            for model in models
        }
        common_points = set.intersection(*[set(points) for points in closest_points.values()])

        m = folium.Map(location=[latitude, longitude], zoom_start=6)

        colors = self._get_color_map()
        for model, points in closest_points.items():
            self._add_markers(m, points, common_points, colors[model], model)
        
        self._add_markers(m, common_points, set(), colors["COMMON"], "COMMON")
        folium.Marker(location=[latitude, longitude], popup="POINT").add_to(m)

        filename = self._get_full_path(filename, path_file, "html")
        m.save(filename)

    def create_map_kml(
        self,
        latitude: float,
        longitude: float,
        n_points: int = 4,
        filename: str = "closest_points_map.kml",
        path_file: str = None,
        models: List[str] = ["ECMWF", "GFS"],
    ):
        closest_points = {
            model: self.model_selectors[model].select_closest_points(latitude, longitude, n_points)
            for model in models
        }
        common_points = set.intersection(*[set(points) for points in closest_points.values()])

        data = self._prepare_kml_data(closest_points, common_points, latitude, longitude)
        color_map = self._get_color_map()

        kml = simplekml.Kml()
        self._add_kml_placemarks(kml, data, color_map)

        filename = self._get_full_path(filename, path_file, "kml")
        kml.save(filename)

    @staticmethod
    def _add_markers(m, points, common_points, color, label):
        for point in points:
            if point in common_points:
                continue
            folium.Marker(
                location=[point[0], point[1]],
                popup=f"({point[0]:.2f}, {point[1]:.2f}) {label}",
                icon=folium.Icon(color=color),
            ).add_to(m)

    @staticmethod
    def _prepare_kml_data(closest_points, common_points, latitude, longitude):
        data = []
        for model, points in closest_points.items():
            data.extend([(point, model) for point in points if point not in common_points])
        data.extend([(point, "COMMON") for point in common_points])
        data.append(((latitude, longitude), "OBJECTIVE"))

        df = pd.DataFrame(data, columns=["COORDS", "TYPE"])
        df["LAT"] = df["COORDS"].apply(lambda x: x[0])
        df["LON"] = df["COORDS"].apply(lambda x: x[1])
        return df

    @staticmethod
    def _get_color_map():
        return {
            "GFS_0.5": "red",
            "GFS_0.25": "darkred",
            "ECMWF": "green",
            "UKMET": "blue",
            "NCEP": "purple",
            "DWD": "orange",
            "METEOFRANCE": "darkred",
            "CMCC": "darkgreen",
            "JMA": "darkblue",
            "COMMON": "cadetblue",
            "OBJECTIVE": "black",
        }

    @staticmethod
    def _add_kml_placemarks(kml, data, color_map):
        for _, row in data.iterrows():
            placemark = kml.newpoint(
                name=row["TYPE"], coords=[(row["LON"], row["LAT"])]
            )
            placemark.style.labelstyle.color = simplekml.Color.red
            placemark.style.iconstyle.color = simplekml.Color.rgb(
                *[int(x) for x in bytes.fromhex(color_map[row["TYPE"]][1:])]
            )

    @staticmethod
    def _get_full_path(filename, path_file, extension):
        if path_file is not None:
            if filename is None:
                filename = f"closest_points_map.{extension}"
            elif not filename.lower().endswith(f".{extension}"):
                filename = f"{filename}.{extension}"
            return os.path.join(path_file, filename)
        return (
            filename
            if filename.lower().endswith(f".{extension}")
            else f"{filename}.{extension}"
        )

def create_map(
    latitude: float,
    longitude: float,
    n_points: int = 4,
    filename: str = "closest_points_map.html",
    path_file: str = None,
    models: List[str] = ["ECMWF", "GFS_0.5", "GFS_0.25"],
):
    MapGenerator().create_map(
        latitude, longitude, n_points, filename, path_file, models
    )

def create_map_kml(
    latitude: float,
    longitude: float,
    n_points: int = 4,
    filename: str = "closest_points_map.kml",
    path_file: str = None,
    models: List[str] = ["ECMWF", "GFS_0.5", "GFS_0.25"],
):
    MapGenerator().create_map_kml(
        latitude, longitude, n_points, filename, path_file, models
    )

