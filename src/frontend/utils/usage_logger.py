
"""
- likes, dislikes, superlikes, nolikes
- tijd op elke pagina
- finale filmkeuze
"""

import sys, os
import threading
import json
import time
from collections import defaultdict
from datetime import datetime
from urllib import request, parse
import socket

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")

sys.path.append(root_path)

from src.frontend import config

logs_path = os.path.join(root_path, "logs")

lock = threading.Lock()

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class UsageLogger(object):
    __metaclass__ = Singleton


    def get_session_log_file(self, session_id):
        return os.path.join(logs_path, session_id + ".json")

    def disect_session_id(self, session_id_with_timestamp):
        (session_id, session_timestamp) = session_id_with_timestamp.strip().split("|")
        return session_id, session_timestamp

    # Initialises the folder structure
    def init_session(self, session_id_with_timestamp):

        (session_id, _) = self.disect_session_id(session_id_with_timestamp)

        # Create a folder for the current session if it doesn't exist yet
        # if not os.path.exists(self.get_session_path(session_id)):
        #     os.makedirs(self.get_session_path(session_id))

        if not os.path.exists(self.get_session_log_file(session_id)):

            json_object = {
                "session_id": session_id,
                "creation_time": time.ctime(time.time()),
            }
            
            with open(self.get_session_log_file(session_id), 'w+') as openfile:
                json.dump(json_object, openfile)


    def log_page_enter(self, session_id_with_timestamp, page):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)

        self.health_log_message(session_id, "Entered page [" + page + "]")
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        page_enter_object = timestamp_object.get("page_enters", {})

        page_enter_object[page] = time.time()

        timestamp_object["page_enters"] = page_enter_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_scan_time(self, session_id_with_timestamp, user_id):
        
        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        tinder_object = timestamp_object.get("tinder_sessions", {})

        user_object = tinder_object.get(user_id, {})

        user_object["scan_time"] = time.time()

        tinder_object[user_id] = user_object

        timestamp_object["tinder_sessions"] = tinder_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_user_name(self, session_id_with_timestamp, user_id, user_name):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        tinder_object = timestamp_object.get("tinder_sessions", {})

        user_object = tinder_object.get(user_id, {})

        user_object["name"] = user_name

        tinder_object[user_id] = user_object

        timestamp_object["tinder_sessions"] = tinder_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_input_movie(self, session_id_with_timestamp, user_id, movie_title, movie_index):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        tinder_object = timestamp_object.get("tinder_sessions", {})

        user_object = tinder_object.get(user_id, {})

        input_movie_list = user_object.get("input_movie_list", [])
        input_movie_list.append((movie_title, movie_index))
        user_object["input_movie_list"] = input_movie_list

        tinder_object[user_id] = user_object

        timestamp_object["tinder_sessions"] = tinder_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_feedback(self, session_id_with_timestamp, user_id, feedback, movie_title):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        tinder_object = timestamp_object.get("tinder_sessions", {})

        user_object = tinder_object.get(user_id, {})

        feedback_list = user_object.get("feedback_list", [])
        feedback_list.append((time.time(), feedback, movie_title))
        user_object["feedback_list"] = feedback_list

        tinder_object[user_id] = user_object

        timestamp_object["tinder_sessions"] = tinder_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_tinder_likes(self, session_id_with_timestamp, user_id, dislike_list, like_list, superlike_list, nolike_list, like_string):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        tinder_object = timestamp_object.get("tinder_sessions", {})

        user_object = tinder_object.get(user_id, {})

        user_object["dislike_list"] = dislike_list
        user_object["like_list"] = like_list
        user_object["superlike_list"] = superlike_list
        user_object["nolike_list"] = nolike_list
        user_object["like_string"] = like_string

        tinder_object[user_id] = user_object

        timestamp_object["tinder_sessions"] = tinder_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_result(self, session_id_with_timestamp, result):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        timestamp_object["result"] = result

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))

    def log_movie_refresh(self, session_id_with_timestamp, column, from_movie, to_movie):

        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        refresh_list = timestamp_object.get("refresh", [])

        refresh_list.append((time.time(), column, from_movie.name, to_movie.name))

        timestamp_object["refresh"] = refresh_list

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))
 
    def log_movie_choice(self, session_id_with_timestamp, chosen_movie):
        
        (session_id, session_timestamp) = self.disect_session_id(session_id_with_timestamp)
        
        with open(self.get_session_log_file(session_id), 'r') as openfile:
            json_object = json.load(openfile)

        sessions_object = json_object.get("session_timestamps", {})

        timestamp_object = sessions_object.get(session_timestamp, {})

        choice_object = timestamp_object.get("choice", {})

        choice_object["end_time"] = time.time()
        choice_object["choice"] = chosen_movie

        timestamp_object["choice"] = choice_object

        sessions_object[session_timestamp] = timestamp_object

        json_object["session_timestamps"] = sessions_object
        
        with open(self.get_session_log_file(session_id), 'w') as openfile:
            json.dump(json_object, openfile, sort_keys=True, indent=4, separators=(',', ': '))


    def health_log_message(self, session_id, message):
        message = session_id + " > " + message
        data = parse.urlencode({"data":message}).encode()
        try:
            request.urlopen("https://hc-ping.com/" + config.HEALTHCHECK_UUID_FRONTEND + "/log", timeout=10, data=message.encode('utf-8'))
        except socket.error as e:
            print("Healthcheck log failed: %s" % e)


    #def health_log_start        
