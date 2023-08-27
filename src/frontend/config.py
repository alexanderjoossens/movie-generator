import socket
import os, sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

root_path = os.path.join(os.getcwd(), "..","..")
env_path = os.path.join(root_path, "env")
docker_path = os.path.join(root_path, "Docker")

env_file_path = os.path.join(env_path, ".env")
load_dotenv(dotenv_path=env_file_path)

docker_env_file_path = os.path.join(docker_path, ".env")
load_dotenv(dotenv_path=docker_env_file_path)

PORT = os.getenv('PORT')
MIN_LIKES = int(os.getenv('MIN_LIKES'))

IN_DOCKER = os.getenv('IN_DOCKER', None)

if (IN_DOCKER == None):
    HOST_ADDR = socket.gethostbyname(socket.gethostname())
else:
    HOST_ADDR = os.getenv('IP_ADDR', None)


# Some configuration (see config.py)
BASE_URL = HOST_ADDR + ":" + str(PORT)

HEALTHCHECK_UUID_FRONTEND = os.getenv('HEALTHCHECK_UUID_FRONTEND')
HEALTHCHECK_UUID_BACKEND = os.getenv('HEALTHCHECK_UUID_BACKEND')