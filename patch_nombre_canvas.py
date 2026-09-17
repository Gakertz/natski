from pathlib import Path

p = Path(r".\src\art_timelapse\gui.py")
s = p.read_text(encoding="utf-8")

old_start = s.find("    def prepare_session_paths(self):")
old_end = s.find("    async def record_sai(self):", old_start)

if old_start == -1 or old_end == -1:
    raise SystemExit("No se encontro prepare_session_paths. No se modifico el archivo.")

new_helper = r'''    def prepare_session_paths(self, base_name=None):
        # Carpeta principal de todas las sesiones
        base_dir = Path.home() / 'Videos' / 'Art Timelapse'

        # Nombre descriptivo de la sesion
        if not base_name:
            base_name = 'ArtTimelapse'

        # Quitar extension, si corresponde
        base_name = Path(str(base_name)).stem.strip()

        if not base_name:
            base_name = 'ArtTimelapse'

        # Reemplazar caracteres no permitidos en nombres de Windows
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            base_name = base_name.replace(char, '_')

        # Limpiar espacios y puntos finales
        base_name = base_name.rstrip(' .')

        # Fecha/hora como sufijo para distinguir varias sesiones
        stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        session_name = f'{base_name}_{stamp}'
        session_dir = base_dir / session_name

        # Protección adicional contra colisiones
        counter = 1
        while session_dir.exists():
            session_name = f'{base_name}_{stamp}_{counter:02d}'
            session_dir = base_dir / session_name
            counter += 1

        frames_dir = session_dir / 'frames'
        result_dir = session_dir / 'resultado'

        frames_dir.mkdir(parents=True, exist_ok=False)
        result_dir.mkdir(parents=True, exist_ok=False)

        self.frames_file_var.set(str(frames_dir))
        self.export_file_var.set(str(result_dir / session_name))

        logging.info(f'Session folder created: {session_dir}')
        logging.info(f'Frames path: {frames_dir}')
        logging.info(f'Export path: {result_dir / session_name}')

        return session_dir

'''

s = s[:old_start] + new_helper + s[old_end:]

# SAI: utilizar nombre original del canvas
old = """            canvas = canvases[self.sai_canvas_box.get_index()]
            self.prepare_session_paths()
"""

new = """            canvas = canvases[self.sai_canvas_box.get_index()]
            self.prepare_session_paths(canvas.get_name())
"""

if old not in s:
    raise SystemExit("No se encontro llamada de SAI. No se modifico el archivo.")

s = s.replace(old, new, 1)

# PSD: utilizar nombre del archivo PSD/PSB
old = """    async def record_psd(self):
        self.prepare_session_paths()
        frames_path = self.frames_file_var.get()
"""

new = """    async def record_psd(self):
        psd_file = self.psd_file_var.get()
        self.prepare_session_paths(Path(psd_file).stem if psd_file else 'PSD')
        frames_path = self.frames_file_var.get()
"""

if old in s:
    s = s.replace(old, new, 1)

# Evitar la segunda asignacion redundante de psd_file
old = """        image_size_limit = self.image_size_limit_var.get()
        psd_file = self.psd_file_var.get()
        auto_split = self.auto_split_psd_var.get()
"""

new = """        image_size_limit = self.image_size_limit_var.get()
        auto_split = self.auto_split_psd_var.get()
"""

if old in s:
    s = s.replace(old, new, 1)

# Screen Recording: nombre generico reconocible
old = """        self.prepare_session_paths()
        frames_path = self.frames_file_var.get()
"""

# Solo reemplazar la siguiente ocurrencia que queda, correspondiente a Screen
if old in s:
    s = s.replace(
        old,
        """        self.prepare_session_paths('ScreenRecording')
        frames_path = self.frames_file_var.get()
""",
        1
    )

p.write_text(s, encoding="utf-8")

print("NOMBRES DE SESION BASADOS EN CANVAS agregados correctamente.")
