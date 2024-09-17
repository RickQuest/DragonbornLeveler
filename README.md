
# DragonbornLeveler

Welcome to DragonbornLeveler, a Python-based Qt application designed to automate skill training in Skyrim. This GUI app allows users to easily start bots that train various skills, enhancing the gaming experience by efficiently leveling up character abilities.

## Features

- **User-Friendly Interface**: A clean and intuitive graphical interface that makes it easy to operate and monitor the bot's activities.
- **Skill Training Automation**: Currently supports the automated training of Armor, Illusion, and Conjuration. Additional skill support is planned for future releases.
- **Customizable Settings**: Users can configure the bot's behavior to suit specific training needs and preferences.
- **Real-Time Monitoring**: Watch the bot's progress in real-time with logs and status updates within the app.
- **Platform Support**: As of now, the application is compatible only with Windows operating systems.

## Installation

To get DragonbornLeveler up and running on your system, follow these steps:

### 1. **Clone the Repository**:
   Clone the repository to your local machine and navigate into the project directory:
   ```bash
   git clone https://github.com/RickQuest/DragonbornLeveler.git
   cd DragonbornLeveler
   ```

### 2. **Install Dependencies Using Make**:
   - Ensure you have **Conda** installed on your machine.
   - Use the `make` command to automate the setup process:
     ```bash
     make setup
     ```

   This command will:
   - Create or update the Conda environment using the `environment.yml` file.
   - Install **Tesseract** using the provided Python setup script.

### 3. **Activate the Environment**:
   After the setup is complete, activate the environment with:
   ```bash
   conda activate dragonbornleveler
   ```

## Usage

1. **Start the Application**: Open the application by running `main.py`.
2. **Configure the Bot**: Use the GUI to select which skill you'd like to train (Armor, Illusion, or Conjuration) and adjust any specific settings for the training routine.
3. **Start Training**: Hit the 'Start' or press the hotkey ('break' by default) button and let the bot train the selected skill in Skyrim.

## Building the Application

To build DragonbornLeveler into a standalone executable, use PyInstaller:
   ```bash
   pyinstaller main.spec
   ```
This will create an executable in the `dist` folder that you can distribute or use without needing a Python environment setup.

## Continuous Integration and GitHub Actions

This project utilizes **GitHub Actions** to automate testing, building, and releasing, ensuring the stability and quality of **DragonbornLeveler**.

### Workflows Overview

- **Test Workflow** (`.github/workflows/test.yml`): Runs automatically on pushes to the `main` branch and on pull requests targeting `main`. It sets up the environment, installs dependencies, and executes unit tests using `pytest` to verify code integrity.

- **Build and Release Workflow** (`.github/workflows/build-and-release.yml`): Triggered when a new version tag is pushed (e.g., `v1.0.0`). It builds the executable with `PyInstaller`, creates a GitHub release, and uploads the executable as a release asset.

### Key Benefits

- **Automated Testing**: Ensures all code changes are tested for reliability.
- **Consistent Builds**: Generates builds from specific tagged versions for consistency.
- **Streamlined Releases**: Automates the release process, making new versions available quickly.


## Contributing

Contributions to DragonbornLeveler are welcome! If you have suggestions for improvements or bug fixes, please fork the repository and submit a pull request.

- **Bug Reports**: Please use the GitHub issues tracker to submit any bugs or feature requests.
- **Feature Contributions**: For major changes, please open an issue first to discuss what you would like to change.

## License

DragonbornLeveler is licensed under the [MIT License](LICENSE).

**Disclaimer:**
Please note that the use of this software may violate the Terms of Service or End-User License Agreement of Skyrim or associated platforms. Users are responsible for ensuring compliance with all applicable agreements and laws. The author is not liable for any misuse of this software.


Thank you for using or contributing to DragonbornLeveler!
