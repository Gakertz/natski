from pathlib import Path

gui_path = Path(r".\src\art_timelapse\gui.py")
time_path = Path(r".\src\art_timelapse\timelapse.py")

gui = gui_path.read_text(encoding="utf-8")
tim = time_path.read_text(encoding="utf-8")

# ------------------------------------------------------------
# GUI: variable persistente
# ------------------------------------------------------------
old = """        self.export_preview_duration = self.settings.get_var('export_preview_duration', 0.0)
        self.export_use_recording_var = self.settings.get_var('export_user_recording', True)
"""

new = """        self.export_preview_duration = self.settings.get_var('export_preview_duration', 0.0)
        self.export_final_frame_duration = self.settings.get_var('export_final_frame_duration', 0.0)
        self.export_use_recording_var = self.settings.get_var('export_user_recording', True)
"""

if old not in gui:
    raise SystemExit("No se encontro bloque GUI 1")

gui = gui.replace(old, new, 1)

# ------------------------------------------------------------
# GUI: campo visible
# ------------------------------------------------------------
old = """        export_preview_duration = EntryLabelRow(export_frame, _('Preview duration'), textvariable=self.export_preview_duration)
        export_user_recording = CheckbuttonLabelRow(export_frame, _('Use recording video type'), variable=self.export_use_recording_var)
"""

new = """        export_preview_duration = EntryLabelRow(export_frame, _('Preview duration'), textvariable=self.export_preview_duration)
        export_final_frame_duration = EntryLabelRow(export_frame, _('Final frame duration'), textvariable=self.export_final_frame_duration)
        export_user_recording = CheckbuttonLabelRow(export_frame, _('Use recording video type'), variable=self.export_use_recording_var)
"""

if old not in gui:
    raise SystemExit("No se encontro bloque GUI 2")

gui = gui.replace(old, new, 1)

# ------------------------------------------------------------
# GUI: tooltip
# ------------------------------------------------------------
old = """        add_tooltips(export_preview_duration, _('The duration of the preview frame in seconds. Enter 0 or leave blank to display for only a single frame. This adds on to the final export duration.'))
        add_tooltips(export_user_recording, _('Use the same video options as the recording tabs and ignore the below settings.'))
"""

new = """        add_tooltips(export_preview_duration, _('The duration of the preview frame in seconds. Enter 0 or leave blank to display for only a single frame. This adds on to the final export duration.'))
        add_tooltips(export_final_frame_duration, _('How many seconds to hold the finished artwork at the end of the exported video. Enter 0 for no additional pause.'))
        add_tooltips(export_user_recording, _('Use the same video options as the recording tabs and ignore the below settings.'))
"""

if old not in gui:
    raise SystemExit("No se encontro bloque GUI 3")

gui = gui.replace(old, new, 1)

# ------------------------------------------------------------
# GUI: leer valor al exportar
# ------------------------------------------------------------
old = """        export_preview_duration = self.export_preview_duration.get()
        export_fps = self.export_fps_var.get()
"""

new = """        export_preview_duration = self.export_preview_duration.get()
        export_final_frame_duration = self.export_final_frame_duration.get()
        export_fps = self.export_fps_var.get()
"""

if old not in gui:
    raise SystemExit("No se encontro bloque GUI 4")

gui = gui.replace(old, new, 1)

# ------------------------------------------------------------
# GUI: pasarlo a timelapse.export()
# ------------------------------------------------------------
old = """            await asyncio.to_thread(timelapse.export, progress_kill_check, export_time_limit, export_preview_last_frame, export_preview_duration, export_fps, frames_path, container, codec, output_path)
"""

new = """            await asyncio.to_thread(timelapse.export, progress_kill_check, export_time_limit, export_preview_last_frame, export_preview_duration, export_final_frame_duration, export_fps, frames_path, container, codec, output_path)
"""

if old not in gui:
    raise SystemExit("No se encontro bloque GUI 5")

gui = gui.replace(old, new, 1)

# ------------------------------------------------------------
# TIMELAPSE: nueva funcion para pausa final
# ------------------------------------------------------------
marker = """def export(progress_iter:function, export_time_limit:float, preview_last_frame:bool, preview_duration:float, fps:int, frames:Path, container:str, codec:str, output_path=''):
"""

replacement = """def write_final_frames(progress_iter:function, reader:VideoSequenceReader, writer:VideoSequenceWriter, final_duration:float, fps:int, reuse_arrays:dict):
    if final_duration <= 0:
        return
    last_frame = reader.get_last_frame()
    frame_count = int(final_duration * fps)
    for _ in progress_iter(range(frame_count), frame_count, unit='frames'):
        writer.write(last_frame, reuse_arrays=reuse_arrays)

def export(progress_iter:function, export_time_limit:float, preview_last_frame:bool, preview_duration:float, final_frame_duration:float, fps:int, frames:Path, container:str, codec:str, output_path=''):
"""

if marker not in tim:
    raise SystemExit("No se encontro funcion export")

tim = tim.replace(marker, replacement, 1)

# ------------------------------------------------------------
# TIMELAPSE: agregar pausa despues de todos los frames normales
# ------------------------------------------------------------
old = """                data = reader.read()
                index += 1
                writer.write(data, reuse_arrays=reuse_arrays)
"""

new = """                data = reader.read()
                index += 1
                writer.write(data, reuse_arrays=reuse_arrays)

            write_final_frames(
                progress_iter,
                reader,
                writer,
                final_frame_duration,
                fps,
                reuse_arrays
            )
"""

if old not in tim:
    raise SystemExit("No se encontro final del loop de exportacion")

tim = tim.replace(old, new, 1)

gui_path.write_text(gui, encoding="utf-8")
time_path.write_text(tim, encoding="utf-8")

print("FINAL FRAME DURATION agregado correctamente.")
