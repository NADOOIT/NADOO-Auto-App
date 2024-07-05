import toga
from pathlib import Path
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
import asyncio
import logging
from dotenv import load_dotenv, set_key
from mentat.python_client.client import PythonClient
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.INFO)

class MentatApp(toga.App):
    def startup(self):
        self.env_file = os.path.expanduser("~/.mentat/.env")
        self.settings = self.load_env()

        self.main_window = toga.MainWindow(title=self.formal_name)

        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        file_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.file_label = toga.Label("No file or directory selected", style=Pack(flex=1))
        choose_file_button = toga.Button("Choose File", on_press=self.choose_file, style=Pack(padding=5))
        choose_dir_button = toga.Button("Choose Directory", on_press=self.choose_directory, style=Pack(padding=5))
        file_box.add(self.file_label)
        file_box.add(choose_file_button)
        file_box.add(choose_dir_button)

        chat_box = toga.Box(style=Pack(direction=COLUMN, padding=5, flex=10))
        self.chat_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        self.chat_input = toga.MultilineTextInput(style=Pack(direction=ROW, padding=10, flex=1))
        send_button = toga.Button("Send", on_press=self.send_message, style=Pack(padding=5))
        input_box = toga.Box(style=Pack(direction=ROW, padding=5))
        input_box.add(self.chat_input)
        input_box.add(send_button)

        chat_box.add(self.chat_display)
        chat_box.add(input_box)

        main_box.add(file_box)
        main_box.add(chat_box)

        settings_command = toga.Command(
            text='Settings',
            action=self.open_settings,
            group=toga.Group.FILE,
            order=3
        )

        self.commands.add(settings_command)

        self.main_window.content = main_box
        self.main_window.show()

        self.python_client = None

    def load_env(self):
        load_dotenv(self.env_file)

    def save_settings(self, api_key):
        os.makedirs(os.path.dirname(self.env_file), exist_ok=True)
        set_key(self.env_file, "OPENAI_API_KEY", api_key)
        self.load_env()
        self.main_window.info_dialog("Info", "Settings Saved")

    def get_api_key(self):
        return os.getenv("OPENAI_API_KEY")

    async def choose_file(self, widget):
        try:
            self.filepath = await self.main_window.open_file_dialog("Choose File")
            if self.filepath:
                self.file_label.text = f"Selected: {self.filepath}"
                await self.initialize_mentat()
            else:
                self.file_label.text = "No file selected"
        except Exception as e:
            self.main_window.error_dialog("Error", f"An error occurred while choosing a file: {e}")
            self.file_label.text = "Error selecting file"
    
    async def choose_directory(self, widget):
        try:
            self.filepath = await self.main_window.select_folder_dialog("Choose Directory")
            if self.filepath:
                self.file_label.text = f"Selected: {self.filepath}"
                await self.initialize_mentat()
            else:
                self.file_label.text = "No directory selected"
        except Exception as e:
            self.main_window.error_dialog("Error", f"An error occurred while choosing a directory: {e}")
            self.file_label.text = "Error selecting directory"


    async def initialize_mentat(self):
        api_key = self.get_api_key()
        if not api_key:
            self.main_window.error_dialog("Error", "No API key found. Please set it in the settings.")
            return

        os.environ["OPENAI_API_KEY"] = api_key

        self.python_client = PythonClient(
            cwd=Path(self.filepath).parent,
            paths=[self.filepath],
        )

        try:
            await self.python_client.startup()
            self.chat_display.value += "Mentat initialized. You can start chatting now.\n\n"
        except Exception as e:
            logging.error(f"Error in initialize_mentat: {str(e)}")
            self.main_window.error_dialog("Error", f"Failed to initialize Mentat: {str(e)}")



    async def send_message(self, widget):
        if not self.python_client:
            self.main_window.error_dialog("Error", "Please select a file or directory first.")
            return

        message = self.chat_input.value
        if not message:
            return

        self.chat_display.value += f"You: {message}\n"
        self.chat_input.value = ""

        self.chat_display.value += "Mentat is thinking...\n"

        try:
            response = await asyncio.wait_for(self.python_client.call_mentat(message), timeout=30)
            self.chat_display.value = self.chat_display.value.replace("Mentat is thinking...\n", "")
            self.chat_display.value += f"Mentat: {response}\n\n"
        except asyncio.TimeoutError:
            self.chat_display.value = self.chat_display.value.replace("Mentat is thinking...\n", "")
            self.chat_display.value += "Error: Mentat took too long to respond.\n\n"
        except Exception as e:
            logging.error(f"Error in send_message: {str(e)}")
            self.chat_display.value = self.chat_display.value.replace("Mentat is thinking...\n", "")
            self.chat_display.value += f"Error: {str(e)}\n\n"



    def open_settings(self, widget):
        settings_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        api_key_input = toga.TextInput(placeholder="API Key", value=os.getenv("OPENAI_API_KEY"), style=Pack(flex=1))

        save_button = toga.Button("Save", on_press=lambda x: self.save_settings(api_key_input.value), style=Pack(padding=5))

        settings_box.add(toga.Label("API Key:", style=Pack(padding=(0, 5))))
        settings_box.add(api_key_input)
        settings_box.add(save_button)

        settings_window = toga.Window(title="Settings")
        settings_window.content = settings_box
        settings_window.show()

def main():
    return MentatApp()

if __name__ == '__main__':
    main().main_loop()
