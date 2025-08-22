import Millennium, PluginUtils # type: ignore
from logger import logger
import time
import requests

class Backend:
    @staticmethod 
    def receive_frontend_message(message: str):
        logger.log(f"receivsed: {[message]}")

        return True


def get_steam_path():
    logger.log("getting steam path")
    return Millennium.steam_path()

class Plugin:


    def _front_end_loaded(self):

        logger.log("The front end has loaded!")

        start_time = time.time()
        value = Millennium.call_frontend_method("classname.method", params=[18, "USA", False])
        end_time = time.time()
        
        logger.log(f"classname.method says -> {value} [{round((end_time - start_time) * 1000, 3)}ms]")


    def _load(self):
        logger.log(f"bootstrapping example plugin, millennium {Millennium.version()}")
        try:
            value = Millennium.call_frontend_method("classname.method", params=[18, "USA", False])
            logger.log(f"ponged message -> {value}")
        except ConnectionError as error:
            logger.error(f"Failed to ping frontend, {error}")
        Millennium.ready()


    def _unload(self):
        logger.log("unloading")