import os
import toga
from mentat.python_client.client import PythonClient
import asyncio
import logging
from pathlib import Path
from .settings import get_api_key, get_provider, get_model
from .views import create_main_box, create_settings_window
from mentat.config import Config

logging.basicConfig(level=logging.INFO)


class MentatApp(toga.App):
    def __init__(self):
        super().__init__()
        self.send_button = None
        self.initialized = None
        self.main_box = None
        self.python_client = None
        self.filepath = None
        self.file_label = None
        self.chat_input = None
        self.chat_display = None

        # set the AI provider and model
        self.config = Config()
        self.config.provider = get_provider()
        self.config.model = get_model()

    def startup(self):
        self.initialized = False

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_box = create_main_box(self)

        self.main_window.content = self.main_box
        self.main_window.show()

        self.python_client = None
        self.filepath = None

    def open_settings(self, widget):
        settings_window = create_settings_window(self)
        settings_window.show()

    async def choose_file(self, widget):
        try:
            self.filepath = await self.main_window.open_file_dialog("Choose File")
            if self.filepath:
                self.file_label.text = f"Selected: {self.filepath}"
                await self.initialize_mentat()
            else:
                self.file_label.text = "No file selected"
        except Exception as e:
            await self.main_window.error_dialog(
                "Error", f"An error occurred while choosing a file: {e}"
            )
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
            await self.main_window.error_dialog(
                "Error", f"An error occurred while choosing a directory: {e}"
            )
            self.file_label.text = "Error selecting directory"

    async def initialize_mentat(self):
        api_key = get_api_key()
        if not api_key:
            await self.main_window.error_dialog(
                "Error", "No API key found. Please set it in the settings."
            )
            return

        os.environ["OPENAI_API_KEY"] = api_key

        self.python_client = PythonClient(
            cwd=Path(self.filepath).parent,
            paths=[self.filepath],
            config=self.config
        )

        try:
            await self.python_client.startup()
            self.chat_display.value += "Mentat initialized. You can start chatting now.\n\n"
            self.initialized = True
            self.chat_input.enabled = True
            self.send_button.enabled = True

        except Exception as e:
            logging.error(f"Error in initialize_mentat: {str(e)}")
            await self.main_window.error_dialog("Error", f"Failed to initialize Mentat: {str(e)}")

    async def send_message(self, widget):
        if not self.initialized:
            await self.main_window.error_dialog(
                "Error", "Please select a file or directory first and wait for initialization."
            )
            return

        message = self.chat_input.value
        if not message:
            return

        self.chat_display.value += f"You: {message}\n"
        self.chat_input.value = ""

        self.chat_display.value += "Mentat is thinking...\n"

        try:
            response = await self.python_client.call_mentat(message)
            response = await self.python_client.call_mentat(message)

            self.chat_display.value = self.chat_display.value.replace(
                "Mentat is thinking...\n", ""
            )
            self.chat_display.value += f"Mentat: {response}\n\n"

        except asyncio.TimeoutError:
            self.chat_display.value = self.chat_display.value.replace(
                "Mentat is thinking...\n", ""
            )
            self.chat_display.value += "Error: Mentat took too long to respond.\n\n"
        except Exception as e:
            logging.error(f"Error in send_message: {str(e)}")
            self.chat_display.value = self.chat_display.value.replace(
                "Mentat is thinking...\n", ""
            )
            self.chat_display.value += f"Error: {str(e)}\n\n"
