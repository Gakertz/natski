from pathlib import Path

p = Path(r".\src\art_timelapse\gui.py")
s = p.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1. Importar datetime
# ------------------------------------------------------------

if "from datetime import datetime" not in s:
    marker = "import time\n"

    if marker not in s:
        raise SystemExit("No se encontro 'import time'. No se modifico el archivo.")

    s = s.replace(
        marker,
        "import time\nfrom datetime import datetime\n",
        1
    )

# ------------------------------------------------------------
# 2. Agregar creador automatico de sesiones
# ------------------------------------------------------------

if "def prepare_session_paths(self):" not in s:

    marker = "    async def record_sai(self):\n"

    if marker not in s:
        raise SystemExit("No se encontro record_sai. No se modifico el archivo.")

    helper = """    def prepare_session_paths(self):
        # Carpeta principal de todas las sesiones
        base_dir = Path.home() / 'Videos' / 'Art Timelapse'

        # Nombre basado en fecha y hora local
        stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        session_name = stamp
        session_dir = base_dir / session_name

        # Evitar sobrescribir si existen dos sesiones
        # iniciadas dentro del mismo segundo
        counter = 1
        while session_dir.exists():
            session_name = f'{stamp}_{counter:02d}'
            session_dir = base_dir / session_name
            counter += 1

        frames_dir = session_dir / 'frames'
        result_dir = session_dir / 'resultado'

        frames_dir.mkdir(parents=True, exist_ok=False)
        result_dir.mkdir(parents=True, exist_ok=False)

        # Actualizar automaticamente los campos de la interfaz
        self.frames_file_var.set(str(frames_dir))
        self.export_file_var.set(str(result_dir / session_name))

        logging.info(
            f'Session folder created: {session_dir}'
        )
        logging.info(
            f'Frames path: {frames_dir}'
        )
        logging.info(
            f'Export path: {result_dir / session_name}'
        )

        return session_dir

"""

    s = s.replace(marker, helper + marker, 1)

# ------------------------------------------------------------
# 3. SAI Recording
# ------------------------------------------------------------

old = """            canvas = canvases[self.sai_canvas_box.get_index()]
            frames_path = self.frames_file_var.get()
"""

new = """            canvas = canvases[self.sai_canvas_box.get_index()]
            self.prepare_session_paths()
            frames_path = self.frames_file_var.get()
"""

if old in s and "canvas = canvases[self.sai_canvas_box.get_index()]\n            self.prepare_session_paths()" not in s:
    s = s.replace(old, new, 1)

# ------------------------------------------------------------
# 4. PSD Recording
# ------------------------------------------------------------

old = """    async def record_psd(self):
        frames_path = self.frames_file_var.get()
"""

new = """    async def record_psd(self):
        self.prepare_session_paths()
        frames_path = self.frames_file_var.get()
"""

if old in s:
    s = s.replace(old, new, 1)

# ------------------------------------------------------------
# 5. Screen Recording
# ------------------------------------------------------------

old = """        if window is None:
            return
        frames_path = self.frames_file_var.get()
"""

new = """        if window is None:
            return
        self.prepare_session_paths()
        frames_path = self.frames_file_var.get()
"""

if old in s:
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

print("SESIONES AUTOMATICAS agregadas correctamente.")
