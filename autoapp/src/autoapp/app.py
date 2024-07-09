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
import json
from mentat.config import Config
from argparse import Namespace
from collections import deque

warnings.filterwarnings("ignore", category=DeprecationWarning)

logging.basicConfig(level=logging.INFO)

class MentatApp(toga.App):
    def startup(self):
        self.env_file = os.path.expanduser("~/.mentat/.env")
        self.load_env()
        self.selected_provider = None
        self.selected_model = None
        self.message_queue = deque()  # Initialize message queue

        # Load the last saved settings
        configs_path = Path.home() / ".mentat/configs.json"
        if configs_path.exists():
            with open(configs_path, "r") as f:
                configs = json.load(f)
                self.selected_provider = configs.get("provider")
                self.selected_model = configs.get("model")

        self.main_window = toga.MainWindow(title=self.formal_name)

        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        file_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.file_label = toga.Label("No file or directory selected", style=Pack(flex=1))
        choose_file_button = toga.Button("Choose File", on_press=self.choose_file, style=Pack(padding=5))
        choose_dir_button = toga.Button("Choose Directory", on_press=self.choose_directory, style=Pack(padding=5))
        run_mentat_button = toga.Button("Run Mentat", on_press=self.run_mentat, style=Pack(padding=5))  # Add Run Mentat button
        file_box.add(self.file_label)
        file_box.add(choose_file_button)
        file_box.add(choose_dir_button)
        file_box.add(run_mentat_button)  # Add button to file_box

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
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)

    def open_settings(self, widget):
        settings_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        module_options = {
            "openai": ["gpt-3.5-turbo", "gpt-4-0125-preview", "gpt-4-turbo-preview"],
            "anthropic": ["claude-v1", "claude-3-5-sonnet-20240620"],
            "azure": ["gpt-35-turbo"]
        }

        self.provider_select = toga.Selection(items=list(module_options.keys()), on_select=self.select_provider, style=Pack(flex=1))
        self.model_select = toga.Selection(items=[], enabled=False, style=Pack(flex=1))  # Initialize model_select

        if self.selected_provider:
            self.provider_select.value = self.selected_provider
            self.model_select.items = module_options[self.selected_provider]  # Set items here
            self.model_select.enabled = True
            if self.selected_model:
                self.model_select.value = self.selected_model

        api_key_value = os.getenv(f"{self.selected_provider}_API_KEY", "") if self.selected_provider else ""
        self.api_key_input = toga.TextInput(placeholder="API Key", value=api_key_value, style=Pack(flex=1))

        save_button = toga.Button("Save", on_press=lambda x: self.save_settings(self.api_key_input.value, self.selected_provider, self.model_select.value), style=Pack(padding=5))

        settings_box.add(toga.Label("Provider:", style=Pack(padding=(0, 5))))
        settings_box.add(self.provider_select)
        settings_box.add(toga.Label("Model:", style=Pack(padding=(0, 5))))
        settings_box.add(self.model_select)
        settings_box.add(toga.Label("API Key:", style=Pack(padding=(0, 5))))
        settings_box.add(self.api_key_input)
        settings_box.add(save_button)

        settings_window = toga.Window(title="Settings")
        settings_window.content = settings_box
        settings_window.show()

    def select_provider(self, widget):
        self.selected_provider = widget.value
        module_options = {
            "openai": ["gpt-3.5-turbo", "gpt-4-0125-preview", "gpt-4-turbo-preview"],
            "anthropic": ["claude-v1", "claude-3-5-sonnet-20240620"],
            "azure": ["gpt-35-turbo"]
        }
        if self.selected_provider in module_options:
            self.model_select.items = module_options[self.selected_provider]
            self.model_select.enabled = True
        else:
            self.model_select.items = []
            self.model_select.enabled = False

    def save_settings(self, api_key, provider, model):
        if not provider:
            self.main_window.error_dialog("Error", "No provider selected.")
            return

        os.makedirs(os.path.dirname(self.env_file), exist_ok=True)
        set_key(self.env_file, f"{provider.upper()}_API_KEY", api_key)
        self.load_env()

        # Save provider and model in configs.json
        configs_path = Path.home() / ".mentat/configs.json"
        configs = {}
        if configs_path.exists():
            with open(configs_path, "r") as f:
                configs = json.load(f)

        configs["provider"] = provider
        configs["model"] = model
        with open(configs_path, "w") as f:
            json.dump(configs, f, indent=4)

        # Save only model in .mentat/.mentat_config.json
        mentat_config_path = Path.home() / ".mentat/.mentat_config.json"
        mentat_config = {}
        if mentat_config_path.exists():
            with open(mentat_config_path, "r") as f:
                mentat_config = json.load(f)

        mentat_config["model"] = model
        with open(mentat_config_path, "w") as f:
            json.dump(mentat_config, f, indent=4)

        self.main_window.info_dialog("Info", "Settings Saved")

    def get_api_key(self):
        return os.getenv(f"{self.selected_provider}_API_KEY")

    async def choose_file(self, widget):
        try:
            self.filepath = await self.main_window.open_file_dialog("Choose File")
            if self.filepath:
                self.file_label.text = f"Selected: {self.filepath}"
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
            else:
                self.file_label.text = "No directory selected"
        except Exception as e:
            self.main_window.error_dialog("Error", f"An error occurred while choosing a directory: {e}")
            self.file_label.text = "Error selecting directory"

    async def run_mentat(self, widget):
        if not self.filepath:
            self.main_window.error_dialog("Error", "Please select a file or directory first.")
            return

        api_key = self.get_api_key()
        if not api_key:
            self.main_window.error_dialog("Error", "No API key found. Please set it in the settings.")
            return

        os.environ[f"{self.selected_provider}_API_KEY"] = api_key

        
        config = Config()
        config.model = self.selected_model
        config.provider = self.selected_provider
        print(
            config.model,
            config.provider
            )

        self.python_client = PythonClient(
            cwd=Path(self.filepath).parent,
            paths=[self.filepath],
            config=config,
        )

        try:
            await self.python_client.startup()
            self.chat_display.value += "Mentat initialized. You can start chatting now.\n\n"
        except Exception as e:
            logging.error(f"Error in run_mentat: {str(e)}")
            self.main_window.error_dialog("Error", f"Failed to initialize Mentat: {str(e)}")

    async def process_message_queue(self):
        while self.message_queue:
            message = self.message_queue.popleft()
            self.chat_display.value += f"You: {message}\n"
            self.chat_display.value += "Mentat is thinking...\n"

            try:
                response = await asyncio.wait_for(self.python_client.call_mentat(message), timeout=30)
                self.chat_display.value = self.chat_display.value.replace("Mentat is thinking...\n", "")
                self.chat_display.value += f"Mentat: {response}\n\n"
            except asyncio.TimeoutError:
                self.chat_display.value = self.chat_display.value.replace("Mentat is thinking...\n", "")
                self.chat_display.value += "Error: Mentat took too long to respond.\n\n"
            except Exception as e:
                logging.error(f"Error in process_message_queue: {str(e)}")
                self.chat_display.value = self.chat_display.value.replace("Mentat is thinking...\n", "")
                self.chat_display.value += f"Error: {str(e)}\n\n"

    async def send_message(self, widget):
        if not self.python_client:
            self.main_window.error_dialog("Error", "Please select a file or directory and run Mentat first.")
            return

        message = self.chat_input.value
        if not message:
            return

        self.message_queue.append(message)
        self.chat_input.value = ""

        if len(self.message_queue) == 1:
            await self.process_message_queue()

def main():
    return MentatApp()

if __name__ == '__main__':
    main().main_loop()
