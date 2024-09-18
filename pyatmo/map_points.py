import os
from collections import defaultdict
from typing import List, Tuple

import folium
import numpy as np
import pandas as pd
import simplekml

from pyatmo.logger import setup_logger
from pyatmo.settings import LOGGER_NAME

logger = setup_logger(LOGGER_NAME, "pyatmo.log")


class GridPointSelector:
    def __init__(
        self,
        lat_range: Tuple[float, float],
        lon_range: Tuple[float, float],
        step: float,
        name: str = "",
    ):
        self.name = name
        logger.info(
            f"Initializing GridPointSelector with name={name}, lat_range={lat_range}, lon_range={lon_range}, step={step}"
        )
        self.lats = np.arange(lat_range[0], lat_range[1] + step, step)
        self.lons = np.arange(lon_range[0], lon_range[1] + step, step)
        self.points = [(lat, lon) for lat in self.lats for lon in self.lons]

    def select_closest_points(
        self, latitude: float, longitude: float, n_points: int = 4
    ) -> List[Tuple[float, float]]:
        logger.info(
            f"Selecting {n_points} closest points to latitude={latitude}, longitude={longitude}"
        )
        distances = [
            np.sqrt((point[0] - latitude) ** 2 + (point[1] - longitude) ** 2)
            for point in self.points
        ]
        closest_indices = np.argsort(distances)[:n_points]
        closest_points = [self.points[i] for i in closest_indices]
        logger.debug(f"Closest points: {closest_points}")
        return closest_points


class MapGenerator:
    def __init__(self, team="SIROCCO"):
        self.team = team
        logger.info(f"Initializing MapGenerator with team={team}")
        self._update_model_selectors()

    def _update_model_selectors(self):
        logger.info("Updating model selectors")
        common_models = {
            "GFS_0.5": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.5),
            "GFS_0.25": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.25),
        }

        if self.team == "SIROCCO":
            self.model_selectors = {
                "ECMWF": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1),
                "UKMET": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.2),
                "NCEP": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.25),
                "DWD": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1),
                "METEOFRANCE": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1),
                "CMCC": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.25),
                "JMA": GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.2),
                **common_models,
            }
        elif self.team == "NEBBO":
            self.model_selectors = {
                "ECMWF": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                "UKMET": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                "NCEP": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                "DWD": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                "METEOFRANCE": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                "CMCC": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                "JMA": GridPointSelector((-90.0, 90.0), (0.0, 358.75), 1.25),
                "ECCC": GridPointSelector((-89.5, 89.5), (0.5, 359.5), 1.0),
                **common_models,
            }
        logger.debug(f"Model selectors: {self.model_selectors}")

    def create_map(self, latitude, longitude, n_points, filename, path_file, models):
        logger.info(
            f"Creating map for latitude={latitude}, longitude={longitude}, n_points={n_points}, filename={filename}, path_file={path_file}, models={models}"
        )
        closest_points = {}
        for model in models:
            if model in self.model_selectors:
                closest_points[model] = self.model_selectors[
                    model
                ].select_closest_points(latitude, longitude, n_points)
            else:
                logger.warning(f"Model {model} not available for team {self.team}")

        m = folium.Map(location=[latitude, longitude], zoom_start=6)

        # Agrupar puntos coincidentes
        point_groups = defaultdict(list)
        for model, points in closest_points.items():
            for point in points:
                point_groups[point].append(model)

        colors = self._get_color_map()

        # Crear marcadores para cada grupo de puntos
        for point, models_list in point_groups.items():
            popup_text = "<br>".join(
                [f"{model}: ({point[0]:.2f}, {point[1]:.2f})" for model in models_list]
            )
            folium.Marker(
                location=[point[0], point[1]],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=self._get_group_color(models_list, colors)),
            ).add_to(m)

        folium.Marker(location=[latitude, longitude], popup="POINT").add_to(m)

        filename = self._get_full_path(filename, path_file, "html")
        m.save(filename)
        logger.info(f"Map saved to {filename}")

    def create_map_kml(
        self,
        latitude: float,
        longitude: float,
        n_points: int = 4,
        filename: str = "closest_points_map.kml",
        path_file: str = None,
        models: List[str] = ["ECMWF", "GFS_0.5"],
    ):
        logger.info(
            f"Creating KML map for latitude={latitude}, longitude={longitude}, n_points={n_points}, filename={filename}, path_file={path_file}, models={models}"
        )
        closest_points = {
            model: self.model_selectors[model].select_closest_points(
                latitude, longitude, n_points
            )
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
            placemark = kml.newpoint(
                name=f"({point[0]:.2f}, {point[1]:.2f})", coords=[(point[1], point[0])]
            )
            placemark.description = description
            placemark.style.iconstyle.color = simplekml.Color.rgb(
                *self._get_kml_color(models_list, color_map)
            )

        # Punto objetivo
        kml.newpoint(name="OBJECTIVE", coords=[(longitude, latitude)])

        filename = self._get_full_path(filename, path_file, "kml")
        kml.save(filename)
        logger.info(f"KML map saved to {filename}")

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
        logger.debug(f"Adding markers with color={color} and label={label}")
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
        logger.debug("Preparing KML data")
        data = []
        for model, points in closest_points.items():
            data.extend(
                [(point, model) for point in points if point not in common_points]
            )
        data.extend([(point, "COMMON") for point in common_points])
        data.append(((latitude, longitude), "OBJECTIVE"))

        df = pd.DataFrame(data, columns=["COORDS", "TYPE"])
        df["LAT"] = df["COORDS"].apply(lambda x: x[0])
        df["LON"] = df["COORDS"].apply(lambda x: x[1])
        logger.debug(f"KML data prepared: {df}")
        return df

    @staticmethod
    def _get_color_map():
        logger.debug("Getting color map")
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
        logger.debug("Adding KML placemarks")
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
        logger.debug(
            f"Getting full path for filename={filename}, path_file={path_file}, extension={extension}"
        )
        if path_file is not None:
            if filename is None:
                filename = f"closest_points_map.{extension}"
            elif not filename.lower().endswith(f".{extension}"):
                filename = f"{filename}.{extension}"
            full_path = os.path.join(path_file, filename)
        else:
            full_path = (
                filename
                if filename.lower().endswith(f".{extension}")
                else f"{filename}.{extension}"
            )
        logger.debug(f"Full path: {full_path}")
        return full_path


# Modificar las funciones create_map y create_map_kml para que acepten el parámetro 'team'
def create_map(
    latitude: float,
    longitude: float,
    n_points: int = 4,
    filename: str = "closest_points_map.html",
    path_file: str = None,
    models: List[str] = ["ECMWF", "GFS_0.5", "GFS_0.25"],
    team: str = "SIROCCO",
):
    logger.info(f"Creating map with team={team}")
    MapGenerator(team).create_map(
        latitude, longitude, n_points, filename, path_file, models
    )


def create_map_kml(
    latitude: float,
    longitude: float,
    n_points: int = 4,
    filename: str = "closest_points_map.kml",
    path_file: str = None,
    models: List[str] = ["ECMWF", "GFS_0.5", "GFS_0.25"],
    team: str = "SIROCCO",
):
    logger.info(f"Creating KML map with team={team}")
    MapGenerator(team).create_map_kml(
        latitude, longitude, n_points, filename, path_file, models
    )

