#!/usr/bin/python
import locale
import os
from typing import cast, Dict

from flask import Flask, Response, send_from_directory

import config  # noqa: F401

from flask_calendar.actions import (index_action, login_action, do_login_action, main_calendar_action, new_task_action,
                                    edit_task_action, update_task_action, save_task_action, delete_task_action,
                                    update_task_day_action, hide_repetition_task_instance_action)
from flask_calendar.app_utils import task_details_for_markup
import hashlib, json, os, time
from typing import cast, Dict
from cachelib.simple import SimpleCache

cache = SimpleCache()

from typing import Dict, Optional

from flask_calendar.calendar_data import CalendarData

class Authorization:
    def __init__(self, calendar_data: CalendarData) -> None:
        self.calendar_data = calendar_data
    def can_access(self, username: str, data: Optional[Dict] = None, calendar_id: Optional[str] = None) -> bool:
        if calendar_id is None:
            return username in self.calendar_data.users_list(data=data)
        else:
            return username in self.calendar_data.users_list(calendar_id=calendar_id)
class Authentication:
    USERS_FILENAME = "users.json"
    def __init__(self, data_folder: str, password_salt: str, failed_login_delay_base: int) -> None:
        self.contents = {}  # type: Dict
        with open(os.path.join(".", data_folder, self.USERS_FILENAME)) as file:
            self.contents = json.load(file)
        self.password_salt = password_salt
        self.failed_login_delay_base = failed_login_delay_base
        self.data_folder = data_folder
    def is_valid(self, username: str, password: str) -> bool:
        if username not in self.contents:
            self._failed_attempt(username)
            return False
        if self._hash_password(password) != self.contents[username]["password"]:
            self._failed_attempt(username)
            return False
        return True
    def user_data(self, username: str) -> Dict:
        return cast(Dict, self.contents[username])
    def add_user(self, username: str, plaintext_password: str, default_calendar: str) -> None:
        if username in self.contents:
            raise ValueError("Username {} already exists".format(username))
        hashed_password = self._hash_password(plaintext_password)
        self.contents[username] = {"username": username, "password": hashed_password,
		     						"default_calendar": default_calendar, "ics_key": "an_ics_key"}
        self._save()
    def delete_user(self, username: str) -> None:
        self.contents.pop(username)
        self._save()
    def _hash_password(self, plaintext_password: str) -> str:
        hash_algoritm = hashlib.new("sha256")
        hash_algoritm.update((plaintext_password + self.password_salt).encode("UTF-8"))
        return hash_algoritm.hexdigest()
    def _save(self) -> None:
        with open(os.path.join(".", self.data_folder, self.USERS_FILENAME), "w") as file:
            json.dump(self.contents, file)
    def _failed_attempt(self, username: str) -> None:
        key = "LF_{}".format(username)
        attempts = cache.get(key)
        if attempts is None:
            attempts = 0
        else:
            attempts = int(attempts) + 1
        wait = self.failed_login_delay_base**attempts
        cache.set(key, attempts, timeout=7200)  # Keep for 2h
        time.sleep(wait)

def create_app(config_overrides: Dict = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object('config')
    if config_overrides is not None:
        app.config.from_mapping(config_overrides)
    if app.config['LOCALE'] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config['LOCALE'])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config['LOCALE']))
    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route('/favicon.ico')
    def favicon() -> Response:
        return cast(Response, send_from_directory(
            os.path.join(cast(str, app.root_path), 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
        )
    app.add_url_rule("/", "index_action", index_action, methods=["GET"])
    app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
    app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
    app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.add_url_rule("/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"])
    app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/", "edit_task_action", edit_task_action, methods=["GET"])
    app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/task/<task_id>", "update_task_action", update_task_action, methods=["POST"])
    app.add_url_rule("/<calendar_id>/new_task", "save_task_action", save_task_action, methods=["POST"])
    app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/", "delete_task_action", delete_task_action, methods=["DELETE"])
    app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/", "update_task_day_action", update_task_day_action, methods=["PUT"])
    app.add_url_rule("/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/", "hide_repetition_task_instance_action", hide_repetition_task_instance_action, methods=["POST"])
    app.jinja_env.filters['task_details_for_markup'] = task_details_for_markup
    return app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config['DEBUG'], host=app.config['HOST_IP'])
