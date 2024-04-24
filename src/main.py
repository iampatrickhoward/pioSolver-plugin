from nicegui import ui, events
import os
from __future__ import annotations

ui.label("Upload File")
ui.label('(Drag and drop into the box below, or use the "+" button to select a file)')


def handle_upload(file: events.UploadEventArguments) -> None:
    ui.notify(f"uploaded {file.name} to {os.getcwd()}")
    data = file.content.read()
    with open(file.name, "wb") as f:
        f.write(data)
    lines = [line for line in data.splitlines() if line.strip()]
    ui.label("Lines uploaded:")
    for line in lines:
        ui.label(line.decode())

ui.upload(on_upload=handle_upload, auto_upload=True).classes("max-w-full")

ui.run(title="Submit File")
