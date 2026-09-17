from pathlib import Path

p = Path(r".\src\art_timelapse\timelapse.py")
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

target = "self.click_started_in_window = window.getPID() == self.target_window.getPID()"

found = False

for i, line in enumerate(lines):
    if target not in line:
        continue

    # Buscar el bloque inmediatamente posterior
    for j in range(i + 1, min(i + 6, len(lines))):
        if "if self.click_started_in_window:" not in lines[j]:
            continue

        if j + 2 >= len(lines):
            continue

        if "bbox = window.rect if self.bbox is None else self.bbox" not in lines[j + 1]:
            continue

        if "self.click_started_in_window = point_in_bbox(bbox, (x, y))" not in lines[j + 2]:
            continue

        indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
        newline = "\r\n" if lines[j].endswith("\r\n") else "\n"

        replacement = [
            indent + "if self.click_started_in_window and self.bbox is not None:" + newline,
            indent + "    self.click_started_in_window = point_in_bbox(self.bbox, (x, y))" + newline,
        ]

        lines[j:j + 3] = replacement
        found = True
        break

    if found:
        break

if not found:
    raise SystemExit("No se encontro el bloque a modificar. No se cambio el archivo.")

p.write_text("".join(lines), encoding="utf-8")
print("PIDFIX2 aplicado correctamente.")
