import configparser
import os


config_file_path = os.path.join(os.path.dirname(__file__), '../config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)

secret_config_file_path = os.path.join(os.path.dirname(__file__), '../secret_config.ini')
secret_config = configparser.ConfigParser()
secret_config.read(secret_config_file_path)
