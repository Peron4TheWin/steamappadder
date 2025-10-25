import json
import pyuac
import os
import sys
import subprocess
import winreg
import requests
import zipfile


def get_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        return steam_path.strip('"')
    except (FileNotFoundError, OSError):
        return None


def download_file(url, destination):
    print(f"Downloading from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded to {destination}")
        return True
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return False


def extract_zip(zip_path, extract_to):
    print(f"Extracting archive to {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction completed")
        return True
    except zipfile.BadZipFile as e:
        print(f"Error extracting ZIP: {e}")
        return False


def create_startup_shortcut(target_path):
    startup_folder = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_folder, "SteamTools.lnk")

    powershell_cmd = f"""
    $s = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}')
    $s.TargetPath = '{target_path}'
    $s.Save()
    """

    try:
        subprocess.run([
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_cmd
        ], check=True, capture_output=True)
        print(f"Created startup shortcut at {shortcut_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating shortcut: {e}")
        return False


def install_steambrew():
    url = "https://api.github.com/repos/SteamClientHomebrew/Millennium/releases/latest"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    url=""
    for i in data["assets"]:
        if str(i["browser_download_url"]).__contains__("windows"):
            url = str(i["browser_download_url"])
    return url



def install_steam_tools():
    program_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
    steamtools_folder = os.path.join(program_files, 'SteamTools')
    os.makedirs(steamtools_folder, exist_ok=True)

    source_url = "https://github.com/Peron4TheWin/steamappadder/releases/download/release/steamtools.zip"
    zip_file = os.path.join(steamtools_folder, "steamtools.zip")

    if not download_file(source_url, zip_file):
        print("Failed to download SteamTools")
        return False

    if not extract_zip(zip_file, steamtools_folder):
        print("Failed to extract SteamTools")
        return False

    try:
        os.remove(zip_file)
        print("Deleted temporary ZIP file")
    except OSError as e:
        print(f"Warning: Could not delete temporary file: {e}")

    steamtools_exe = os.path.join(steamtools_folder, "SteamTools.exe")
    create_startup_shortcut(steamtools_exe)

    # Start SteamTools
    try:
        subprocess.Popen([steamtools_exe])
        print("Started SteamTools")
    except OSError as e:
        print(f"Could not start SteamTools: {e}")

    return True


def install_steam_plugins(steam_path):
    plugins_folder = os.path.join(steam_path, "plugins")
    os.makedirs(plugins_folder, exist_ok=True)

    print(f"Installing plugins to: {plugins_folder}")

    source_url = "https://github.com/Peron4TheWin/steamappadder/releases/download/release/release.zip"
    zip_file = os.path.join(plugins_folder, "download.zip")

    if not download_file(source_url, zip_file):
        print("Failed to download plugins")
        return False

    if not extract_zip(zip_file, plugins_folder):
        print("Failed to extract plugins")
        return False

    try:
        os.remove(zip_file)
        print("Deleted temporary ZIP file")
    except OSError as e:
        print(f"Warning: Could not delete temporary file: {e}")

    print(f"Plugins installed successfully to: {plugins_folder}")
    return True

def config_millenium(steam_path):
    # Define file contents
    millennium_ini_content = """[PackageManager]
    devtools = no
    dev_packages = no
    auto_update_dev_packages = yes
    use_pip = yes
    
    [Settings]
    check_for_updates = yes
    enabled_plugins = core|steam-app-adder
    """

    config_json_content = {
        "general": {
            "injectJavascript": True,
            "injectCSS": True,
            "checkForMillenniumUpdates": True,
            "checkForPluginAndThemeUpdates": True,
            "onMillenniumUpdate": 2,
            "shouldShowThemePluginUpdateNotifications": True,
            "accentColor": "DEFAULT_ACCENT_COLOR"
        },
        "misc": {
            "hasShownWelcomeModal": True
        },
        "themes": {
            "activeTheme": "default",
            "allowedStyles": True,
            "allowedScripts": True,
            "conditions": {}
        },
        "notifications": {
            "showNotifications": True,
            "showUpdateNotifications": True,
            "showPluginNotifications": True
        }
    }

    # Ensure the "ext" folder exists
    ext_folder = os.path.join(steam_path, "ext")
    os.makedirs(ext_folder, exist_ok=True)

    # Write millennium.ini
    millennium_path = os.path.join(ext_folder, "millennium.ini")
    with open(millennium_path, "w", encoding="utf-8") as f:
        f.write(millennium_ini_content)

    # Write config.json
    config_path = os.path.join(ext_folder, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_json_content, f, indent=2)


def reg_import():
    key_path = r"SOFTWARE\Valve\Steamtools"
    values = {
        "fScreenIndex": (winreg.REG_DWORD, 0),
        "fPosition": (winreg.REG_SZ, "@Point(67 104)"),
        "AlwaysStayUnlocked": (winreg.REG_SZ, "true"),
        "ActivateUnlockMode": (winreg.REG_SZ, "true"),
        "notUnlockDepot": (winreg.REG_SZ, "true"),
        "LaunchwithSteam": (winreg.REG_SZ, "true"),
        "FloatingVisible": (winreg.REG_SZ, "false"),
    }
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        for name, (reg_type, value) in values.items():
            winreg.SetValueEx(key, name, 0, reg_type, value)


def dns_change():
    # Change DNS settings
    try:
        dns_command = 'wmic nicconfig where (IPEnabled=TRUE) call SetDNSServerSearchOrder ("94.140.14.14", "94.140.15.15")'
        subprocess.run(dns_command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def main():
    dns_change()
    os.system("cls")
    input("Press Enter to continue...")
    print("Steam Tools Installer - Python Version")

    if sys.platform != 'win32':
        print("This script is designed for Windows only.")
        return 1

    steam_path = get_steam_path()
    if not steam_path:
        print("Steam not found in registry.")
        return 1

    print(f"Steam found at: {steam_path}")
    if not install_steambrew():
        print("Warning: SteamBrew installation failed")
        return 1


    config_millenium(steam_path)
    reg_import()
    program_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
    steamtools_folder = os.path.join(program_files, 'SteamTools')

    if not os.path.exists(steamtools_folder):
        print("Installing SteamTools...")
        if not install_steam_tools():
            print("SteamTools installation failed")
            return 1
    else:
        print("SteamTools folder already exists, skipping installation")

    # Install plugins
    print("Installing Steam plugins...")
    if not install_steam_plugins(steam_path):
        print("Plugin installation failed")
        return 1

    config_folder = os.path.join(steam_path, "config")
    stplugin_folder = os.path.join(config_folder, "stplug-in")
    os.makedirs(stplugin_folder, exist_ok=True)
    print(f"Created stplug-in folder: {stplugin_folder}")
    print("\n\nInstallation completed successfully!")
    input("Press Enter to continue...")

    return 0


if __name__ == "__main__":
    print(install_steambrew())
    """
    try:
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin(wait=False)
            sys.exit(1)
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    """