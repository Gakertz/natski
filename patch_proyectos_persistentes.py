from pathlib import Path

p = Path(r".\src\art_timelapse\gui.py")
s = p.read_text(encoding="utf-8")

# ------------------------------------------------------------
# Asegurar import de datetime
# ------------------------------------------------------------
if "from datetime import datetime" not in s:
    marker = "import time\n"
    if marker not in s:
        raise SystemExit("No se encontro 'import time'. No se modifico nada.")
    s = s.replace(
        marker,
        "import time\nfrom datetime import datetime\n",
        1
    )

# ------------------------------------------------------------
# Agregar sistema de proyectos persistentes
# ------------------------------------------------------------
if "    def prepare_project_paths(self, base_name, source_path=''):" not in s:

    marker = "    async def record_sai(self):\n"

    if marker not in s:
        raise SystemExit("No se encontro record_sai. No se modifico nada.")

    helper = r'''    def prepare_project_paths(self, base_name, source_path=''):
        """
        Crea o recupera el proyecto persistente asociado a un archivo SAI.

        Si source_path existe:
            el mismo archivo .sai2 reutiliza siempre el mismo proyecto.

        Si source_path esta vacio:
            el canvas se considera temporal y se crea una sesion unica.
        """

        base_dir = Path.home() / 'Videos' / 'Art Timelapse'
        base_dir.mkdir(parents=True, exist_ok=True)

        # ----------------------------------------------------
        # Nombre visible y seguro para Windows
        # ----------------------------------------------------
        base_name = str(base_name or '').strip()

        if not base_name:
            base_name = 'ArtTimelapse'

        base_name = Path(base_name).stem.strip()

        if not base_name:
            base_name = 'ArtTimelapse'

        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            base_name = base_name.replace(char, '_')

        base_name = base_name.rstrip(' .')

        if not base_name:
            base_name = 'ArtTimelapse'

        # ----------------------------------------------------
        # Canvas sin guardar: no existe identidad persistente
        # ----------------------------------------------------
        source_path = str(source_path or '').strip()

        if not source_path:
            stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            project_name = f'{base_name}_{stamp}'
            project_dir = base_dir / project_name

            counter = 1
            while project_dir.exists():
                project_name = f'{base_name}_{stamp}_{counter:02d}'
                project_dir = base_dir / project_name
                counter += 1

            frames_dir = project_dir / 'frames'
            result_dir = project_dir / 'resultado'

            frames_dir.mkdir(parents=True, exist_ok=True)
            result_dir.mkdir(parents=True, exist_ok=True)

            self.frames_file_var.set(str(frames_dir))
            self.export_file_var.set(str(result_dir / project_name))

            logging.info(f'Temporary project created: {project_dir}')
            logging.info('Canvas has no saved path; this session cannot be resumed automatically.')
            logging.info(f'Frames path: {frames_dir}')
            logging.info(f'Export path: {result_dir / project_name}')

            return project_dir

        # ----------------------------------------------------
        # Canvas guardado: identidad = ruta del archivo SAI
        # ----------------------------------------------------
        source_identity = os.path.normcase(
            os.path.normpath(source_path)
        )

        index_path = base_dir / 'projects.json'
        projects = {}

        if index_path.exists():
            try:
                projects = json.loads(
                    index_path.read_text(encoding='utf-8')
                )
            except:
                projects = {}

        # ----------------------------------------------------
        # Proyecto ya conocido
        # ----------------------------------------------------
        if source_identity in projects:
            project_name = projects[source_identity]
            project_dir = base_dir / project_name
            is_existing_project = True

        # ----------------------------------------------------
        # Proyecto nuevo
        # ----------------------------------------------------
        else:
            project_name = base_name
            project_dir = base_dir / project_name

            used_names = set(projects.values())
            counter = 2

            while project_name in used_names or project_dir.exists():
                project_name = f'{base_name}_{counter:02d}'
                project_dir = base_dir / project_name
                counter += 1

            projects[source_identity] = project_name

            index_path.write_text(
                json.dumps(
                    projects,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding='utf-8'
            )

            is_existing_project = False

        frames_dir = project_dir / 'frames'
        result_dir = project_dir / 'resultado'

        frames_dir.mkdir(parents=True, exist_ok=True)
        result_dir.mkdir(parents=True, exist_ok=True)

        self.frames_file_var.set(str(frames_dir))
        self.export_file_var.set(str(result_dir / project_name))

        if is_existing_project:
            logging.info(f'Continuing existing project: {project_dir}')
        else:
            logging.info(f'New persistent project created: {project_dir}')

        logging.info(f'SAI source: {source_path}')
        logging.info(f'Frames path: {frames_dir}')
        logging.info(f'Export path: {result_dir / project_name}')

        return project_dir

'''

    s = s.replace(marker, helper + marker, 1)

# ------------------------------------------------------------
# Modificar SOLO record_sai()
# ------------------------------------------------------------

start = s.find("    async def record_sai(self):")
end = s.find("    async def record_psd(self):", start)

if start == -1 or end == -1:
    raise SystemExit("No se encontro el bloque record_sai.")

block = s[start:end]

# Quitar versiones anteriores de prepare_session_paths
block_lines = block.splitlines(keepends=True)

cleaned = []
for line in block_lines:
    if "self.prepare_session_paths(" in line:
        continue
    if "self.prepare_project_paths(" in line:
        continue
    cleaned.append(line)

block = "".join(cleaned)

target = "            canvas = canvases[self.sai_canvas_box.get_index()]\n"

if target not in block:
    raise SystemExit(
        "No se encontro la asignacion del canvas. "
        "No se modifico record_sai."
    )

replacement = """            canvas = canvases[self.sai_canvas_box.get_index()]
            self.prepare_project_paths(
                canvas.get_name(),
                canvas.get_short_path()
            )
"""

block = block.replace(target, replacement, 1)

s = s[:start] + block + s[end:]

p.write_text(s, encoding="utf-8")

print("PROYECTOS PERSISTENTES SAI agregados correctamente.")
