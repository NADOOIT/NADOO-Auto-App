# NADOO-Auto-App

## Overview
Nadoo_Auto_App is a Toga-based application designed to interact with various AI APIs, 
including Anthropic and OpenAI, using the Mentat AI Library. It allows users to select files or directories,
initialize the Mentat client, and engage in a chat with the Mentat library. 
The application also provides a settings interface to configure API keys and models.

```
Nadoo_Auto_App/
│
├── src/
│   └── autoapp/
│       ├── __main__.py
│       ├── app.py
│       ├── config.py
│       ├── constants.py
│       ├── settings.py
│       ├── views.py
│       └── resources/
│
└── project.toml
```


### Root Folder
- `project.toml`: Configuration file for Briefcase.

### src/autoapp Folder

- `__main__.py`: Entry point of the application.
- `app.py`: Main application logic and Toga app definition.
- `config.py`: Configuration class for setting up AI provider and model.
- `constants.py`: Constant values used throughout the application.
- `settings.py`: Functions for managing application settings, including saving and loading environment variables.
- `views.py`: User interface components, including the main window and settings window.


### Files and Their Functions
#### `__main__.py`
This is the entry point of the application.
```
    from .app import MentatApp
    
    def main():
        return MentatApp()
    
    if __name__ == "__main__":
        main().main_loop()
```

#### `app.py`
This file contains the main application logic and Toga app definition. It includes methods for initialization, file selection, chat interaction, and settings.

#### Key Components:

- `MentatApp class`: Defines the Toga application, handling startup, file selection, settings, and interaction with the Mentat Python Client.
#### `config.py`
Defines the configuration for the application.

#### Key Components:

- `AppConfig class`: Inherits from mentat.config.Config and sets the AI provider and model.
#### `constants.py`
Defines constant values used in the application.

Key Constants:

- `ANTHROPIC_API_KEY`
- `PROVIDER`
- `MODEL`
#### `settings.py`
Handles saving and loading of settings using environment variables stored in .mentat/.env. 
Users can update the settings through the GUI or manually edit the .env file.

#### Key Functions:

- `save_settings()`: Saves settings to the .mentat/.env file.
- `get_api_key()`: Retrieves the API key from the .mentat/.env file.
- `get_provider()`: Retrieves the AI provider from the .mentat/.env file.
- `get_model()`: Retrieves the AI model from the .mentat/.env file.
- `load_env_file()`: Loads the environment variables from the .mentat/.env file.
- `env_file()`: Returns the path to the .mentat/.env file.

#### Configuring Settings
- Access the settings window via the "Settings" menu.
- Enter your API key, provider, and model, then click "Save" to update the settings.
- Alternatively, you can manually edit the .mentat/.env file located in your home directory to update the settings directly. 
- The .env file should include the following variables:
```
    ANTHROPIC_API_KEY=your_api_key_here
    PROVIDER=your_provider_here
    MODEL=your_model_here
```

#### `views.py`
Contains the user interface components for the application.

#### Key Functions:

- `create_main_box()`: Creates the main user interface with file selection and chat components.
- `create_settings_window()`: Creates the settings window for configuring API keys, providers, and models.


## Usage
### Running the Application
To run the application, execute the following command from the root directory:
```
cd autoapp
briefcase dev
```
### Selecting Files or Directories
- Use the "Choose File" button to select a file.
- Use the "Choose Directory" button to select a directory.
- The selected file or directory will be displayed in the main window.




