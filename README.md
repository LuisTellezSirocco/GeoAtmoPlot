# KML and HTML Generator for Meteorological Models

## Description

This application is a powerful and easy-to-use tool for generating KML and HTML files that show the nearest grid points of various global meteorological models for a specific location. It is ideal for meteorologists, researchers, and weather enthusiasts who need to visualize and compare different meteorological models.

## Technical Description

The core functionality of the application is implemented in the [`kmz_generator.py`](pyatmo/kmz_generator.py) script. This script handles the generation of KML and HTML files by processing the input data and interfacing with various meteorological models to retrieve the nearest grid points. The graphical interface allows users to input location data, select models, and generate the desired output files.

## How to Use the Application

1. **Start the application**: Run the main script to open the graphical interface.

    ```sh
    python pyatmo/kmz_generator.py
    ```

2. **Enter data**:
   - Asset name: Enter a name to identify your location.
   - Latitude: Enter the latitude of the location (in decimal degrees).
   - Longitude: Enter the longitude of the location (in decimal degrees).

3. **Select models**: Check the boxes of the meteorological models you want to include in your map.

4. **Number of points**: Select how many nearest grid points you want for each model.

5. **Generate files**:
   - Click "Generate KML" to create a KML file.
   - Click "Generate HTML" to create an interactive HTML map.

6. **Save file**: Choose a location on your computer to save the generated file.

## Supported Models

The application supports the following meteorological models:

- ECMWF
- GFS_0.5
- GFS_0.25
- UKMET
- NCEP
- DWD
- METEOFRANCE
- CMCC
- JMA
- ICON

## Advantages

1. **Multiple models**: Allows you to compare grid points from various global meteorological models on a single map.

2. **Clear visualization**: Points from different models are displayed in different colors for easy identification.

3. **Detailed information**: Clicking on a point on the HTML map shows detailed information about the model and exact coordinates.

4. **Flexibility**: You can choose how many grid points to display for each model.

5. **Versatile formats**: Generates KML files (for use in Google Earth) and HTML files (for web browser visualization).

6. **Intuitive interface**: Simple and easy-to-use design, ideal for both beginners and advanced users.

7. **Customization**: You can name your locations for easy tracking and organization.

## Future Development Roadmap

1. **Regional models**: Incorporate regional meteorological models for more detailed analysis in specific areas.

2. **Greater customization**: Allow users to modify the default model resolution and where the grid generation starts and ends.

3. **Data export**: Add an option to export grid point data in CSV or Excel format.

4. **Advanced customization**: Allow users to customize colors, icons, and styles of the generated maps.

6. **Performance optimization**: Improve efficiency to handle large amounts of points and models simultaneously.

---

> This roadmap is subject to change based on user feedback and emerging needs.
