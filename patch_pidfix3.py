from pathlib import Path

p = Path(r".\src\art_timelapse\timelapse.py")
s = p.read_text(encoding="utf-8")

start_marker = "    def on_click_callback(self, x, y, _button, is_pressed):"
end_marker = "    async def track_window(self):"

start = s.find(start_marker)
end = s.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit("No se encontro on_click_callback. No se modifico el archivo.")

new_function = """    def on_click_callback(self, x, y, _button, is_pressed):
        try:
            # SAI Recording:
            # no depender de ventana, coordenadas ni monitor.
            # Cada liberacion del mouse/lapiz solicita una captura.
            # sai_capture descarta automaticamente canvases sin cambios.
            if self.bbox is None:
                if not is_pressed:
                    self.emit_event()
                return

            # Screen Recording:
            # conservar el comportamiento basado en ventana/area.
            if is_pressed:
                window = pywinctl.getTopWindowAt(x, y)
                if window is None:
                    self.click_started_in_window = False
                    return

                self.click_started_in_window = (
                    window.getPID() == self.target_window.getPID()
                )

                if self.click_started_in_window:
                    self.click_started_in_window = point_in_bbox(
                        self.bbox, (x, y)
                    )

            if not is_pressed and self.click_started_in_window:
                self.click_started_in_window = False
                self.emit_event()

        except:
            pass

"""

s = s[:start] + new_function + s[end:]
p.write_text(s, encoding="utf-8")

print("PIDFIX3 aplicado correctamente.")
