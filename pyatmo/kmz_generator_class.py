import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from map_points import create_map, create_map_kml
from pyatmo.logger import setup_logger
from pyatmo.settings import LOGGER_NAME

logger = setup_logger(LOGGER_NAME, "pyatmo_generator.log")


class KMZGenerator:
    def __init__(self):
        logger.info("Initializing KMZGenerator")
        self.root = tk.Tk()
        self.root.title('Generador de KML y HTML')
        self.root.configure(bg='#E8E8E8')
        self._set_window_position()
        self._set_style()
        self.team_var = tk.StringVar(value="SIROCCO")
        self._create_widgets()

    def _set_window_position(self):
        logger.info("Setting window position")
        window_width = 400
        window_height = 600  # Aumentado a 600 para asegurar que haya espacio suficiente
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def _set_style(self):
        logger.info("Setting style")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#E8E8E8')
        self.style.configure('TLabel', background='#E8E8E8', font=('Helvetica', 12))
        self.style.configure('TEntry', fieldbackground='white', font=('Helvetica', 12))
        self.style.configure('TButton', background='#4CAF50', foreground='white', font=('Helvetica', 12, 'bold'))
        self.style.configure('TCheckbutton', background='#E8E8E8', font=('Helvetica', 12))
        self.style.map('TButton', background=[('active', '#45a049')])

    def _create_widgets(self):
        logger.info("Creating widgets")
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Generador de KML y HTML", font=('Helvetica', 16, 'bold')).pack(pady=(0, 20))

        # Añadir selector de equipo
        ttk.Label(main_frame, text="Equipo:").pack(anchor='w', pady=(10, 0))
        team_combo = ttk.Combobox(main_frame, textvariable=self.team_var, values=["SIROCCO", "NEBBO"])
        team_combo.pack(fill='x', pady=(5, 10))
        team_combo.bind("<<ComboboxSelected>>", self._update_models)

        self._create_input_field(main_frame, 'Nombre del asset:')
        
        # Crear etiquetas de latitud y longitud con nombres de atributos
        self.latitud_label = ttk.Label(main_frame, text="Latitud:")
        self.latitud_label.pack(anchor='w', pady=(10, 0))
        self.latitud = ttk.Entry(main_frame, width=40)
        self.latitud.pack(fill='x', pady=(5, 10))

        self.longitud_label = ttk.Label(main_frame, text="Longitud:")
        self.longitud_label.pack(anchor='w', pady=(10, 0))
        self.longitud = ttk.Entry(main_frame, width=40)
        self.longitud.pack(fill='x', pady=(5, 10))

        # Modelos disponibles
        self.models_frame = ttk.LabelFrame(main_frame, text="Modelos", style='TFrame')
        self.models_frame.pack(fill='x', pady=(10, 0))

        self.model_vars = {}
        self._update_models()  # Ahora llamamos a _update_models después de crear models_frame

        # Número de puntos
        points_frame = ttk.Frame(main_frame, style='TFrame')
        points_frame.pack(fill='x', pady=(10, 0))
        ttk.Label(points_frame, text="Número de puntos:").pack(side=tk.LEFT, padx=(0, 5))
        self.points_var = tk.StringVar(value="4")
        ttk.Spinbox(points_frame, from_=1, to=10, textvariable=self.points_var, width=5).pack(side=tk.LEFT)

        # Botones
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(pady=(20, 0), fill='x')

        self._create_button(button_frame, 'Generar KML', self.generate_kml)
        self._create_button(button_frame, 'Generar HTML', self.generate_html)

    def _update_models(self, event=None):
        selected_team = self.team_var.get()
        logger.info(f"Updating models for team: {selected_team}")
        models = self._get_models_for_team(selected_team)

        # Actualizar etiquetas de latitud y longitud
        self._update_lat_lon_labels(selected_team)

        # Limpiar modelos existentes
        for widget in self.models_frame.winfo_children():
            widget.destroy()

        # Crear nuevos checkbuttons para los modelos
        for i, model in enumerate(models):
            var = tk.BooleanVar(value=model in ["ECMWF", "GFS_0.5"])
            ttk.Checkbutton(self.models_frame, text=model, variable=var).grid(row=i//3, column=i%3, sticky='w', padx=5, pady=2)
            self.model_vars[model] = var
    
    def _update_lat_lon_labels(self, team):
        if team == "NEBBO":
            self.latitud_label.config(text="Latitud (-90 a 90):")
            self.longitud_label.config(text="Longitud (0 a 360):")
        elif team == "SIROCCO":
            self.latitud_label.config(text="Latitud (-90 a 90):")
            self.longitud_label.config(text="Longitud (-180 a 180):")
        else:
            self.latitud_label.config(text="Latitud:")
            self.longitud_label.config(text="Longitud:")

    def _get_models_for_team(self, team):
        logger.info(f"Getting models for team: {team}")
        if team == "SIROCCO":
            return ["ECMWF", "GFS_0.5", "GFS_0.25", "UKMET", "NCEP", "DWD", "METEOFRANCE", "CMCC", "JMA", "ICON"]
        elif team == "NEBBO":
            return ["ECMWF", "GFS_0.5", "GFS_0.25", "UKMET", "NCEP", "DWD", "METEOFRANCE", "CMCC", "JMA", "ECCC"]  # Añadir más modelos si es necesario

    def _create_input_field(self, parent, label_text):
        logger.info(f"Creating input field: {label_text}")
        ttk.Label(parent, text=label_text).pack(anchor='w', pady=(10, 0))
        entry = ttk.Entry(parent, width=40)
        entry.pack(fill='x', pady=(5, 10))
        setattr(self, label_text.lower().replace(' ', '_').replace(':', ''), entry)

    def _create_button(self, parent, text, command):
        logger.info(f"Creating button: {text}")
        ttk.Button(parent, text=text, command=command, width=15).pack(side=tk.LEFT, padx=5, pady=5, expand=True)

    def run(self):
        logger.info("Running KMZGenerator")
        self.root.mainloop()

    def _get_input_values(self):
        logger.info("Getting input values")
        asset_name = self.nombre_del_asset.get().strip()
        if not asset_name:
            logger.error("Invalid asset name")
            messagebox.showerror('Error', 'Introduce un nombre de asset válido.')
            return None, None, None, None, None, None
        try:
            lat = float(self.latitud.get())
            lon = float(self.longitud.get())
            models = [model for model, var in self.model_vars.items() if var.get()]
            n_points = int(self.points_var.get())
            team = self.team_var.get()

            # Validate coordinates based on team
            if team == "SIROCCO":
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Coordinates out of range for team SIROCCO")
            elif team == "NEBBO":
                if not (-90 <= lat <= 90) or not (0 <= lon <= 360):
                    raise ValueError("Coordinates out of range for team NEBBO")

            logger.info(f"Input values: asset_name={asset_name}, lat={lat}, lon={lon}, models={models}, n_points={n_points}, team={team}")
            return asset_name, lat, lon, models, n_points, team
        except ValueError as e:
            logger.error(f"Invalid input values: {e}")
            messagebox.showerror('Error', f'Introduce valores válidos para latitud, longitud y número de puntos. {e}')
            return None, None, None, None, None, None

    def _generate_file(self, file_type, create_function):
        logger.info(f"Generating {file_type.upper()} file")
        asset_name, lat, lon, models, n_points, team = self._get_input_values()
        if not asset_name:
            return

        initial_dir = os.path.expanduser('~')
        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title=f"Guardar archivo {file_type.upper()}",
            filetypes=[(f"{file_type.upper()} files", f"*.{file_type}")],
            defaultextension=f".{file_type}",
            initialfile=f"{asset_name}.{file_type}"
        )

        if not file_path:
            logger.info("File save operation cancelled")
            return

        if os.path.exists(file_path):
            overwrite = messagebox.askyesno('Archivo existente', 'El archivo ya existe. ¿Desea sobrescribirlo?')
            if not overwrite:
                logger.info("File overwrite cancelled")
                return

        # Filtrar los modelos válidos para el equipo seleccionado
        valid_models = [model for model in models if model in self._get_models_for_team(team)]
        
        create_function(lat, lon, n_points, asset_name, os.path.dirname(file_path), models=valid_models, team=team)
        
        logger.info(f"{file_type.upper()} file generated at {file_path}")
        messagebox.showinfo('Éxito', f'{file_type.upper()} generado en {file_path}')

    def generate_kml(self):
        logger.info("Generating KML")
        self._generate_file('kml', create_map_kml)

    def generate_html(self):
        logger.info("Generating HTML")
        self._generate_file('html', create_map)


if __name__ == '__main__':
    logger.info("Starting KMZGenerator application")
    app = KMZGenerator()
    app.run()
    logger.info("KMZGenerator application finished")
