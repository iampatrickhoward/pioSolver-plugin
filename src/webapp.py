
from menu import Command, PluginCommands
from inputs import InputType, Input
from global_var import solverPath
from tkinter.filedialog import askopenfilename
from easygui import *
from filePicker import local_file_picker
from nicegui import ui, Tailwind, tailwind_types
import os
import asyncio
from __future__ import annotations
import unittest



dark = ui.dark_mode()
switch = ui.switch("dark mode")
switch.bind_value_to(dark, 'value')
        
textStyle = Tailwind().align_self("center").margin("mt-20").font_size("3xl")
    
    
async def showMenu() :
  with ui.dialog() as dialog, ui.row().classes('place-self-center'):
    for c in PluginCommands:
      ui.button(c.name, on_click=lambda c=c: dialog.submit(c))

  choice = await dialog
  ui.notify(f'You chose {choice.name}')
  if choice == PluginCommands.NODELOCK:
    fPath = await getFilePath()
  await showMenu()


async def connectToSolver(button):
  solverPath = await getFilePath()
  button.delete()
  await showMenu()
        
async def getFilePath() -> str:
  result = await local_file_picker('~', multiple=True)
  ui.notify(f'You chose {result}')
    

            
    
#--------------------------------------------------------------------------------------------------
    
def main():
    
    style = Tailwind().margin('mt-5').align_self("center")
    ui.label("Hi!").tailwind(style)
    ui.label("Pick a piosolver executable to start")
    button = ui.button("Start", on_click = lambda: connectToSolver(button))
    button.tailwind(style)

    ui.run()
    
if __name__ in {"__main__", "__mp_main__"}:
    #unittest.main() 
    main()

