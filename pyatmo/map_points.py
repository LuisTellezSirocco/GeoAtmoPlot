import os
from collections import defaultdict
from typing import Dict, List, Tuple

import folium
import numpy as np
import pandas as pd
import simplekml


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
        models: List[str] = ["ECMWF", "GFS_0.5"],
    ):
        closest_points = {
            model: self.model_selectors[model].select_closest_points(latitude, longitude, n_points)
            for model in models
        }

        m = folium.Map(location=[latitude, longitude], zoom_start=6)

        # Agrupar puntos coincidentes
        point_groups = defaultdict(list)
        for model, points in closest_points.items():
            for point in points:
                point_groups[point].append(model)

        colors = self._get_color_map()
        
        # Crear marcadores para cada grupo de puntos
        for point, models_list in point_groups.items():
            popup_text = "<br>".join([f"{model}: ({point[0]:.2f}, {point[1]:.2f})" for model in models_list])
            folium.Marker(
                location=[point[0], point[1]],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=self._get_group_color(models_list, colors))
            ).add_to(m)

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
        models: List[str] = ["ECMWF", "GFS_0.5"],
    ):
        closest_points = {
            model: self.model_selectors[model].select_closest_points(latitude, longitude, n_points)
            for model in models
        }

        # Agrupar puntos coincidentes
        point_groups = defaultdict(list)
        for model, points in closest_points.items():
            for point in points:
                point_groups[point].append(model)

        kml = simplekml.Kml()
        color_map = self._get_color_map()

        for point, models_list in point_groups.items():
            description = ", ".join(models_list)
            placemark = kml.newpoint(name=f"({point[0]:.2f}, {point[1]:.2f})", coords=[(point[1], point[0])])
            placemark.description = description
            placemark.style.iconstyle.color = simplekml.Color.rgb(*self._get_kml_color(models_list, color_map))

        # Punto objetivo
        kml.newpoint(name="OBJECTIVE", coords=[(longitude, latitude)])

        filename = self._get_full_path(filename, path_file, "kml")
        kml.save(filename)

    @staticmethod
    def _get_group_color(models, color_map):
        if len(models) == 1:
            return color_map[models[0]]
        return "purple"  # Color para puntos que coinciden en múltiples modelos
    
    @staticmethod
    def _get_kml_color(models, color_map):
        if len(models) == 1:
            return [int(x) for x in bytes.fromhex(color_map[models[0]][1:])]
        return [128, 0, 128]  # Purple for multiple models
    
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
            "NCEP": "orange",
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

