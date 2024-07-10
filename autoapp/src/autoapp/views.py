import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .settings import save_settings, get_api_key, get_provider, get_model


def create_main_box(app):
    main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

    file_box = toga.Box(style=Pack(direction=ROW, padding=5))
    app.file_label = toga.Label("No file or directory selected", style=Pack(flex=1))
    choose_file_button = toga.Button(
        "Choose File", on_press=app.choose_file, style=Pack(padding=5)
    )
    choose_dir_button = toga.Button(
        "Choose Directory", on_press=app.choose_directory, style=Pack(padding=5)
    )
    file_box.add(app.file_label)
    file_box.add(choose_file_button)
    file_box.add(choose_dir_button)

    chat_box = toga.Box(style=Pack(direction=COLUMN, padding=5, flex=10))
    app.chat_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
    app.chat_input = toga.MultilineTextInput(
        style=Pack(direction=ROW, padding=10, flex=1)
    )
    app.send_button = toga.Button("Send", on_press=app.send_message, style=Pack(padding=5), enabled=False)
    input_box = toga.Box(style=Pack(direction=ROW, padding=5))
    input_box.add(app.chat_input)
    input_box.add(app.send_button)

    chat_box.add(app.chat_display)
    chat_box.add(input_box)

    main_box.add(file_box)
    main_box.add(chat_box)

    settings_command = toga.Command(
        text="Settings", action=app.open_settings, group=toga.Group.FILE, order=3
    )

    app.commands.add(settings_command)

    return main_box


def create_settings_window(app):
    settings_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

    api_key_label = toga.Label("API Key:", style=Pack(flex=1, padding=(0, 5)))
    api_key_input = toga.TextInput(
        placeholder="API Key", style=Pack(flex=1, padding=(0, 5)), value=get_api_key()
    )
    provider_label = toga.Label("Provider:", style=Pack(flex=1, padding=(0, 5)))
    provider_input = toga.TextInput(
        placeholder="Provider", style=Pack(flex=1, padding=(0, 5)), value=get_provider()
    )
    model_label = toga.Label("Model:", style=Pack(padding=(0, 5)))
    model_input = toga.TextInput(
        placeholder="Model", style=Pack(flex=1, padding=(0, 5)), value=get_model()
    )

    save_button = toga.Button(
        "Save",
        on_press=lambda x: save_settings(app, api_key_input.value, provider_input.value, model_input.value),
        style=Pack(padding=5),
    )

    settings_box.add(api_key_label)
    settings_box.add(api_key_input)

    settings_box.add(provider_label)
    settings_box.add(provider_input)

    settings_box.add(model_label)
    settings_box.add(model_input)

    settings_box.add(save_button)

    settings_window = toga.Window(title="Settings")
    settings_window.content = settings_box

    return settings_window
