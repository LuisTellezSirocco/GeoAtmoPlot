import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from map_points import create_map, create_map_kml
from pyatmo.logger import setup_logger
from pyatmo.settings import LOGGER_NAME
from pyatmo.kmz_generator_class import KMZGenerator

logger = setup_logger(LOGGER_NAME, "pyatmo_generator.log")


if __name__ == '__main__':
    logger.info("Starting KMZGenerator application")
    app = KMZGenerator()
    app.run()
    logger.info("KMZGenerator application finished")
