import Millennium, PluginUtils
import requests
import winreg
import re, os, shutil, zipfile
import subprocess
from io import BytesIO
logger = PluginUtils.Logger()

def getSteamPath() -> str:
    return Millennium.steam_path()
    #Need to check if that first one really returns the correct path
    #(winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"), "SteamPath")[0])

def download_and_extract(appid, lua_folder) -> bool:
    try:
        response = requests.get(f"http://api.perondepot.xyz/get_manifest?appid={appid}", stream=True)
        response.raise_for_status()  # error if download failed
        file_name = os.path.join(lua_folder, f"{appid}.lua")  # or generate a name dynamically
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(response.text)

        return True
    except Exception as e:
        logger.log(e)
        return False


class Backend:

    @staticmethod
    def print(message:str):
        logger.log(message)
        return True

    @staticmethod
    def checkpirated(id:str):
        steampath=(winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"), "SteamPath")[0])
        stplugin = os.path.join(steampath, "config\\stplug-in")
        lua = os.path.join(stplugin, id+".lua")
        return os.path.exists(lua)

    @staticmethod
    def deletelua(id:str):
        logger.log(id)
        steampath=(winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"), "SteamPath")[0])
        stplugin = os.path.join(steampath, "config\\stplug-in")
        lua = os.path.join(stplugin, id+".lua")
        if os.path.exists(lua):
            os.remove(lua)
            return True
        return False

    @staticmethod
    def restart():
        steampath=(winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"), "SteamPath")[0])
        cmd = f'taskkill /f /im steam.exe && start "" "{steampath}\\steam.exe"'
        DETACHED_PROCESS   = 0x00000008
        CREATE_NO_WINDOW   = 0x08000000
        flags = DETACHED_PROCESS | CREATE_NO_WINDOW
        subprocess.Popen(cmd, shell=True, creationflags=flags)
        return True

    @staticmethod 
    def receive_frontend_message(message: str):
        logger.log(f"received: {message}")
        m = re.search(r"store\.steampowered\.com/app/(\d+)/", message)
        if not m:
            return False
        luas=os.path.join(getSteamPath(),"config","stplug-in")
        return download_and_extract(int(m.group(1)),luas)
    




class Plugin:
    def _front_end_loaded(self):
        logger.log("Frontend loaded!")

    def _load(self):
        logger.log("Backend loaded")
        logger.log(f"Plugin base dir: {PLUGIN_BASE_DIR}")
        Millennium.ready()

    def _unload(self):

        logger.log("unloading")
