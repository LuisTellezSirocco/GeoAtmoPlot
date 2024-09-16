import os
import folium
import simplekml
import numpy as np
import pandas as pd
from typing import List, Tuple


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
        self.ecmwf_selector = GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.1)
        self.gfs_selector = GridPointSelector((-90.0, 90.0), (-180.0, 180.0), 0.5)

    def create_map(
        self,
        latitude: float,
        longitude: float,
        n_points: int = 4,
        filename: str = "closest_points_map.html",
        path_file: str = None,
        ecmwf: bool = True,
        gfs: bool = True,
    ):
        closest_points_gfs = (
            self.gfs_selector.select_closest_points(latitude, longitude, n_points)
            if gfs
            else []
        )
        closest_points_ecmwf = (
            self.ecmwf_selector.select_closest_points(latitude, longitude, n_points)
            if ecmwf
            else []
        )
        common_points = list(
            set(closest_points_gfs).intersection(set(closest_points_ecmwf))
        )

        m = folium.Map(location=[latitude, longitude], zoom_start=6)

        if gfs:
            self._add_markers(m, closest_points_gfs, common_points, "red", "GFS")
        if ecmwf:
            self._add_markers(m, closest_points_ecmwf, common_points, "green", "ECMWF")
        self._add_markers(m, common_points, [], "orange", "COMMON")
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
        ecmwf: bool = True,
        gfs: bool = True,
    ):
        closest_points_gfs = (
            self.gfs_selector.select_closest_points(latitude, longitude, n_points)
            if gfs
            else []
        )
        closest_points_ecmwf = (
            self.ecmwf_selector.select_closest_points(latitude, longitude, n_points)
            if ecmwf
            else []
        )
        common_points = list(
            set(closest_points_gfs).intersection(set(closest_points_ecmwf))
        )

        closest_points_gfs = [x for x in closest_points_gfs if x not in common_points]
        closest_points_ecmwf = [
            x for x in closest_points_ecmwf if x not in common_points
        ]

        data = self._prepare_kml_data(
            closest_points_gfs, closest_points_ecmwf, common_points, latitude, longitude
        )
        color_map = self._get_color_map()

        kml = simplekml.Kml()
        self._add_kml_placemarks(kml, data, color_map)

        filename = self._get_full_path(filename, path_file, "kml")
        kml.save(filename)

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
    def _prepare_kml_data(gfs_points, ecmwf_points, common_points, latitude, longitude):
        data = pd.DataFrame(
            {
                "COORDS": gfs_points
                + ecmwf_points
                + common_points
                + [(latitude, longitude)],
                "TYPE": ["GFS"] * len(gfs_points)
                + ["ECMWF"] * len(ecmwf_points)
                + ["COMMON"] * len(common_points)
                + ["OBJECTIVE"],
            }
        )
        data["LAT"] = data["COORDS"].apply(lambda x: x[0])
        data["LON"] = data["COORDS"].apply(lambda x: x[1])
        return data

    @staticmethod
    def _get_color_map():
        return {
            "GFS": (255, 0, 0),  # Red
            "ECMWF": (0, 255, 0),  # Green
            "COMMON": (0, 0, 255),  # Blue
            "OBJECTIVE": (255, 255, 0),  # Yellow
        }

    @staticmethod
    def _add_kml_placemarks(kml, data, color_map):
        for _, row in data.iterrows():
            placemark = kml.newpoint(
                name=row["TYPE"], coords=[(row["LON"], row["LAT"])]
            )
            placemark.style.labelstyle.color = simplekml.Color.red
            placemark.style.iconstyle.color = simplekml.Color.rgb(
                *color_map[row["TYPE"]]
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
    ecmwf: bool = True,
    gfs: bool = True,
):
    MapGenerator().create_map(
        latitude, longitude, n_points, filename, path_file, ecmwf, gfs
    )


def create_map_kml(
    latitude: float,
    longitude: float,
    n_points: int = 4,
    filename: str = "closest_points_map.kml",
    path_file: str = None,
    ecmwf: bool = True,
    gfs: bool = True,
):
    MapGenerator().create_map_kml(
        latitude, longitude, n_points, filename, path_file, ecmwf, gfs
    )
