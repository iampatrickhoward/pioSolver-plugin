#!/usr/bin/env python3
from filePicker import local_file_picker
from nicegui import ui


async def pick_file() -> None:
    result = await local_file_picker('~', multiple=True)
    ui.notify(f'You chose {result}')


def main():
    ui.button('Choose file', on_click=pick_file, icon='folder')
    ui.run()
    
if __name__ in {"__main__", "__mp_main__"}:
    main()


