import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from map_points import create_map, create_map_kml

class KMZGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Generador de KML y HTML')
        self.root.configure(bg='#E8E8E8')
        self._set_window_position()
        self._set_style()
        self._create_widgets()

    def _set_window_position(self):
        window_width = 400
        window_height = 450
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def _set_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#E8E8E8')
        self.style.configure('TLabel', background='#E8E8E8', font=('Helvetica', 12))
        self.style.configure('TEntry', fieldbackground='white', font=('Helvetica', 12))
        self.style.configure('TButton', background='#4CAF50', foreground='white', font=('Helvetica', 12, 'bold'))
        self.style.configure('TCheckbutton', background='#E8E8E8', font=('Helvetica', 12))
        self.style.map('TButton', background=[('active', '#45a049')])

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Generador de KML y HTML", font=('Helvetica', 16, 'bold')).pack(pady=(0, 20))

        self._create_input_field(main_frame, 'Nombre del asset:')
        self._create_input_field(main_frame, 'Latitud:')
        self._create_input_field(main_frame, 'Longitud:')

        # Opciones adicionales
        options_frame = ttk.Frame(main_frame, style='TFrame')
        options_frame.pack(fill='x', pady=(10, 0))

        self.ecmwf_var = tk.BooleanVar(value=True)
        self.gfs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="ECMWF", variable=self.ecmwf_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(options_frame, text="GFS", variable=self.gfs_var).pack(side=tk.LEFT)

        ttk.Label(options_frame, text="Número de puntos:").pack(side=tk.LEFT, padx=(20, 5))
        self.points_var = tk.StringVar(value="4")
        ttk.Spinbox(options_frame, from_=1, to=10, textvariable=self.points_var, width=5).pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(pady=(20, 0))

        self._create_button(button_frame, 'Generar KML', self.generate_kml)
        self._create_button(button_frame, 'Generar HTML', self.generate_html)

    def _create_input_field(self, parent, label_text):
        ttk.Label(parent, text=label_text).pack(anchor='w', pady=(10, 0))
        entry = ttk.Entry(parent, width=40)
        entry.pack(fill='x', pady=(5, 10))
        setattr(self, label_text.lower().replace(' ', '_').replace(':', ''), entry)

    def _create_button(self, parent, text, command):
        ttk.Button(parent, text=text, command=command, width=15).pack(side=tk.LEFT, padx=5, pady=5)

    def run(self):
        self.root.mainloop()
        
    def _get_input_values(self):
        asset_name = self.nombre_del_asset.get().strip()
        if not asset_name:
            messagebox.showerror('Error', 'Introduce un nombre de asset válido.')
            return None, None, None, None, None, None
        try:
            lat = float(self.latitud.get())
            lon = float(self.longitud.get())
            ecmwf = self.ecmwf_var.get()
            gfs = self.gfs_var.get()
            n_points = int(self.points_var.get())
            return asset_name, lat, lon, ecmwf, gfs, n_points
        except ValueError:
            messagebox.showerror('Error', 'Introduce valores válidos para latitud, longitud y número de puntos.')
            return None, None, None, None, None, None

    def _generate_file(self, file_type, create_function):
        asset_name, lat, lon, ecmwf, gfs, n_points = self._get_input_values()
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
            return

        if os.path.exists(file_path):
            overwrite = messagebox.askyesno('Archivo existente', 'El archivo ya existe. ¿Desea sobrescribirlo?')
            if not overwrite:
                return
        
        create_function(lat, lon, n_points, asset_name, os.path.dirname(file_path), ecmwf=ecmwf, gfs=gfs)
        
        messagebox.showinfo('Éxito', f'{file_type.upper()} generado en {file_path}')

    def generate_kml(self):
        self._generate_file('kml', create_map_kml)

    def generate_html(self):
        self._generate_file('html', create_map)

if __name__ == '__main__':
    app = KMZGenerator()
    app.run()

