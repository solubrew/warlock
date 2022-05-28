from functools import wraps
import re, uuid, json, os, time
from datetime import datetime
from typing import cast, Optional, Any, Callable
from werkzeug.wrappers import Response

from typing import (cast, Dict, List, Optional)
from flask import current_app
from flask import render_template, request, jsonify, redirect, abort, make_response, current_app, g
from flask import abort, redirect, request, current_app

from flask_calendar.authorization import Authorization
from flask_calendar.authentication import Authentication
from flask_calendar.calendar_data import CalendarData
from flask_calendar.constants import SESSION_ID
from flask_calendar.gregorian_calendar import GregorianCalendar
from flask_calendar.app_utils import (previous_month_link, next_month_link, new_session_id, add_session, authenticated,
                                      get_session_username, authorized)
from cachelib.simple import SimpleCache
cache = SimpleCache()
# captures patterns like www.xxx xxx. plus querystring parameters
URLS_REGEX_PATTERN = r"((?:(?:https?):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.&]+)"
DECORATED_URL_FORMAT = "<a href=\"{}\" target=\"_blank\">{}</a>"
KEY_TASKS = "tasks"
KEY_USERS = "users"
KEY_NORMAL_TASK = "normal"
KEY_REPETITIVE_TASK = "repetition"
KEY_REPETITIVE_HIDDEN_TASK = "hidden_repetition"

def get_authentication() -> Authentication:
    auth = getattr(g, "_auth", None)
    if auth is None:
        auth = g._auth = Authentication(
            data_folder=current_app.config["USERS_DATA_FOLDER"],
            password_salt=current_app.config["PASSWORD_SALT"],
            failed_login_delay_base=current_app.config["FAILED_LOGIN_DELAY_BASE"],)
    return cast(Authentication, auth)
@authenticated
def index_action() -> Response:
    username = get_session_username(session_id=str(request.cookies.get(SESSION_ID)))
    authentication = get_authentication()
    user_data = authentication.user_data(username)
    return redirect("/{}/".format(user_data["default_calendar"]))
def login_action() -> Response:
    return cast(Response, render_template("login.html"))
def do_login_action() -> Response:
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    authentication = get_authentication()
    if authentication.is_valid(username, password):
        session_id = new_session_id()
        add_session(session_id, username)
        response = make_response(redirect("/"))
        # TODO: other params from http://flask.pocoo.org/docs/0.12/api/#flask.Response.set_cookie
        response.set_cookie(key=SESSION_ID, value=session_id, max_age=2678400)  # 1 month
        return cast(Response, response)
    else:
        return redirect("/login")
@authenticated
@authorized
def main_calendar_action(calendar_id: str) -> Response:
    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]
    if current_app.config["HIDE_PAST_TASKS"]:
        view_past_tasks = False
    else:
        view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])
    try:
        data = calendar_data.load_calendar(calendar_id)
    except FileNotFoundError:
        abort(404)
    tasks = calendar_data.tasks_from_calendar(year, month, data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(year, month, data, tasks)
    if not view_past_tasks:
        calendar_data.hide_past_tasks(year, month, tasks)
    return cast(Response, render_template("calendar.html", calendar_id=calendar_id,
        								year=year, month=month, month_name=month_name,
        								current_year=current_year, current_month=current_month,
        								current_day=current_day, month_days=GregorianCalendar.month_days(year, month),
        								previous_month_link=previous_month_link(year, month),
        								next_month_link=next_month_link(year, month), base_url=current_app.config["BASE_URL"],
        								tasks=tasks, display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"]))
@authenticated
@authorized
def new_task_action(calendar_id: str, year: int, month: int) -> Response:
    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = max(min(int(year), current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = max(min(int(month), 12), 1)
    month_names = GregorianCalendar.MONTH_NAMES
    if current_month == month and current_year == year:
        day = current_day
    else:
        day = 1
    day = int(request.args.get("day", day))
    task = {"date": CalendarData.date_for_frontend(year, month, day),
        	"is_all_day": True,"repeats": False, "details": ""}
    return cast(Response, render_template(
        "task.html",
        calendar_id=calendar_id,
        year=year,
        month=month,
        min_year=current_app.config["MIN_YEAR"],
        max_year=current_app.config["MAX_YEAR"],
        month_names=month_names,
        task=task,
        base_url=current_app.config["BASE_URL"],
        editing=False,
        emojis_enabled=current_app.config.get("EMOJIS_ENABLED", False))
    )
@authenticated
@authorized
def edit_task_action(calendar_id: str, year: int, month: int, day: int, task_id: int) -> Response:
    month_names = GregorianCalendar.MONTH_NAMES
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])

    repeats = request.args.get("repeats") == "1"
    try:
        if repeats:
            task = calendar_data.repetitive_task_from_calendar(
                calendar_id=calendar_id, year=year, month=month, task_id=int(task_id)
            )
        else:
            task = calendar_data.task_from_calendar(
                calendar_id=calendar_id, year=year, month=month, day=day, task_id=int(task_id)
            )
    except (FileNotFoundError, IndexError):
        abort(404)
    if task["details"] == "&nbsp;":
        task["details"] = ""
    return cast(Response, render_template("task.html", calendar_id=calendar_id,
        									year=year, month=month, day=day,
        									min_year=current_app.config["MIN_YEAR"],
        									max_year=current_app.config["MAX_YEAR"],
        									month_names=month_names, task=task,
        									base_url=current_app.config["BASE_URL"],
        									editing=True, emojis_enabled=current_app.config.get("EMOJIS_ENABLED", False)))
@authenticated
@authorized
def update_task_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    # Logic is same as save + delete, could refactor but can wait until need to change any save/delete logic
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])
    # For creation of "updated" task use only form data
    title = request.form["title"].strip()
    date = request.form.get("date", "")
    if len(date) > 0:
        fragments = re.split("-", date)
        updated_year = int(fragments[0])  # type: Optional[int]
        updated_month = int(fragments[1])  # type: Optional[int]
        updated_day = int(fragments[2])  # type: Optional[int]
    else:
        updated_year = updated_month = updated_day = None
    is_all_day = request.form.get("is_all_day", "0") == "1"
    due_time = request.form["due_time"]
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form["color"]
    has_repetition = request.form.get("repeats", "0") == "1"
    repetition_type = request.form.get("repetition_type", "")
    repetition_subtype = request.form.get("repetition_subtype", "")
    repetition_value = int(request.form["repetition_value"])  # type: int
	calendar_data.create_task(calendar_id=calendar_id, year=updated_year, month=updated_month,
                              day=updated_day, title=title, is_all_day=is_all_day, due_time=due_time,
                              details=details, color=color, has_repetition=has_repetition,
                              repetition_type=repetition_type, repetition_subtype=repetition_subtype,
                              repetition_value=repetition_value)
    # For deletion of old task data use only url data
    calendar_data.delete_task(calendar_id=calendar_id, year_str=year,
								month_str=month, day_str=day, task_id=int(task_id))
    if updated_year is None:
        return redirect("{}/{}/".format(current_app.config["BASE_URL"], calendar_id), code=302)
    else:
        return redirect("{}/{}/?y={}&m={}".format(
            current_app.config["BASE_URL"], calendar_id, updated_year, updated_month), code=302
        )
@authenticated
@authorized
def save_task_action(calendar_id: str) -> Response:
    title = request.form["title"].strip()
    date = request.form.get("date", "")
    if len(date) > 0:
        date_fragments = re.split("-", date)
        year = int(date_fragments[0])  # type: Optional[int]
        month = int(date_fragments[1])  # type: Optional[int]
        day = int(date_fragments[2])  # type: Optional[int]
    else:
        year = month = day = None
    is_all_day = request.form.get("is_all_day", "0") == "1"
    due_time = request.form["due_time"]
    details = request.form["details"].replace("\r", "").replace("\n", "<br>")
    color = request.form["color"]
    has_repetition = request.form.get("repeats", "0") == "1"
    repetition_type = request.form.get("repetition_type")
    repetition_subtype = request.form.get("repetition_subtype")
    repetition_value = int(request.form["repetition_value"])
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])
    calendar_data.create_task(calendar_id=calendar_id, year=year, month=month,
                              day=day, title=title, is_all_day=is_all_day, due_time=due_time,
                              details=details, color=color, has_repetition=has_repetition,
                              repetition_type=repetition_type, repetition_subtype=repetition_subtype,
                              repetition_value=repetition_value)
    if year is None:
        return redirect("{}/{}/".format(current_app.config["BASE_URL"], calendar_id), code=302)
    else:
        return redirect("{}/{}/?y={}&m={}".format(current_app.config["BASE_URL"], calendar_id, year, month), code=302)
@authenticated
@authorized
def delete_task_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])
    calendar_data.delete_task(calendar_id=calendar_id, year_str=year, month_str=month,
                              day_str=day, task_id=int(task_id))
    return cast(Response, jsonify({}))
@authenticated
@authorized
def update_task_day_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    new_day = request.data.decode("utf-8")

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])
    calendar_data.update_task_day(calendar_id=calendar_id, year_str=year, month_str=month,
                                  	day_str=day, task_id=int(task_id), new_day_str=new_day)
    return cast(Response, jsonify({}))
@authenticated
@authorized
def hide_repetition_task_instance_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"])
    calendar_data.hide_repetition_task_instance(calendar_id=calendar_id, year_str=year, month_str=month,
                                                day_str=day, task_id_str=task_id)
    return cast(Response, jsonify({}))



def authenticated(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        session_id = request.cookies.get(SESSION_ID)
        if session_id is None or not is_session_valid(str(session_id)):
            if request.headers.get("Content-Type", "") == "application/json":
                abort(401)
            return redirect("/login")
        return decorated_function(*args, **kwargs)
    return wrapper
def authorized(decorated_function: Callable) -> Any:
    @wraps(decorated_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        username = get_session_username(str(request.cookies.get(SESSION_ID)))
        authorization = Authorization(calendar_data=CalendarData(data_folder=current_app.config['DATA_FOLDER']))
        if "calendar_id" not in kwargs:
            raise ValueError("calendar_id")
        calendar_id = str(kwargs["calendar_id"])
        if not authorization.can_access(username=username, calendar_id=calendar_id):
            abort(403)
        return decorated_function(*args, **kwargs)
    return wrapper
def previous_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.previous_month_and_year(year=year, month=month)
    return (
        ""
        if year < current_app.config['MIN_YEAR'] or year > current_app.config['MAX_YEAR']
        else "?y={}&m={}".format(year, month))
def next_month_link(year: int, month: int) -> str:
    month, year = GregorianCalendar.next_month_and_year(year=year, month=month)
    return (
		""
        if year < current_app.config['MIN_YEAR'] or year > current_app.config['MAX_YEAR']
        else "?y={}&m={}".format(year, month))
def new_session_id() -> str:
    return str(uuid.uuid4())
def is_session_valid(session_id: str) -> bool:
    return cache.get(session_id) is not None
def add_session(session_id: str, username: str) -> None:
    cache.set(session_id, username, timeout=2678400)    # 1 month
def get_session_username(session_id: str) -> str:
    return str(cache.get(session_id))
def task_details_for_markup(details: str) -> str:
    if not current_app.config['AUTO_DECORATE_TASK_DETAILS_HYPERLINK']:
        return details
    decorated_fragments = []
    fragments = re.split(URLS_REGEX_PATTERN, details)
    for index, fragment in enumerate(fragments):
        if index % 2 == 1:
            decorated_fragments.append(DECORATED_URL_FORMAT.format(fragment, fragment))
        else:
            decorated_fragments.append(fragment)
    return "".join(decorated_fragments)


class CalendarData:
    REPETITION_TYPE_WEEKLY = "w"
    REPETITION_TYPE_MONTHLY = "m"
    REPETITION_SUBTYPE_WEEK_DAY = "w"
    REPETITION_SUBTYPE_MONTH_DAY = "m"
    def __init__(self, data_folder: str) -> None:
        self.data_folder = data_folder
    def load_calendar(self, filename: str) -> Dict:
        with open(os.path.join(".", self.data_folder, "{}.json".format(filename))) as file:
            contents = json.load(file)
        if type(contents) is not dict:
            raise ValueError("Error loading calendar from file '{}'".format(filename))
        return cast(Dict, contents)
    def users_list(self, data: Optional[Dict] = None, calendar_id: Optional[str] = None) -> List:
        if data is None:
            if calendar_id is None:
                raise ValueError("Need to provide either calendar_id or loaded data")
            else:
                data = self.load_calendar(calendar_id)
        if KEY_USERS not in data:
            raise ValueError("Incomplete data for calendar id '{}'".format(calendar_id))
        return cast(List, data[KEY_USERS])
    def user_details(self, username: str, data: Optional[Dict] = None, calendar_id: Optional[str] = None) -> Dict:
        if data is None:
            if calendar_id is None:
                raise ValueError("Need to provide either calendar_id or loaded data")
            else:
                data = self.load_calendar(calendar_id)
        if KEY_USERS not in data:
            raise ValueError("Incomplete data for calendar id '{}'".format(calendar_id))
        return cast(Dict, data[KEY_USERS][username])
    @staticmethod
    def is_past(year: int, month: int, current_year: int, current_month: int) -> bool:
        if year < current_year:
            return True
        elif year == current_year:
            if month < current_month:
                return True
        return False
    def tasks_from_calendar(self, year: int, month: int, data: Dict) -> Dict:
        if not data or KEY_TASKS not in data:
            raise ValueError("Incomplete data for calendar")
        if not all([
            KEY_NORMAL_TASK in data[KEY_TASKS],
            KEY_REPETITIVE_TASK in data[KEY_TASKS],
            KEY_REPETITIVE_HIDDEN_TASK in data[KEY_TASKS]
        ]):
            raise ValueError("Incomplete data for calendar")
        tasks = {}  # type: Dict
        current_day, current_month, current_year = GregorianCalendar.current_date()
        for day in GregorianCalendar.month_days(year, month):
            month_str = str(day.month)
            year_str = str(day.year)
            if (
                year_str in data[KEY_TASKS][KEY_NORMAL_TASK] and
                month_str in data[KEY_TASKS][KEY_NORMAL_TASK][year_str] and
                month_str not in tasks
            ):
                tasks[month_str] = data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]
        return tasks
    def hide_past_tasks(self, year: int, month: int, tasks: Dict) -> None:
        current_day, current_month, current_year = GregorianCalendar.current_date()
        for day in GregorianCalendar.month_days(year, month):
            month_str = str(day.month)
            if self.is_past(day.year, day.month, current_year, current_month):
                tasks[month_str] = {}
            for task_day_number in tasks[month_str]:
                if day.month == current_month and int(task_day_number) < current_day:
                    tasks[month_str][task_day_number] = []
    def task_from_calendar(self, calendar_id: str, year: int, month: int, day: int, task_id: int) -> Dict:
        data = self.load_calendar(calendar_id)
        year_str = str(year)
        month_str = str(month)
        day_str = str(day)
        for index, task in enumerate(data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str]):
            if task["id"] == task_id:
                task["repeats"] = False
                task["date"] = self.date_for_frontend(year, month, day)
                return cast(Dict, task)
        raise ValueError("Task id '{}' not found".format(task_id))
    def repetitive_task_from_calendar(self, calendar_id: str, year: int, month: int, task_id: int) -> Dict:
        data = self.load_calendar(calendar_id)
        task = [task for task in data[KEY_TASKS][KEY_REPETITIVE_TASK] if task["id"] == task_id][0]  # type: Dict
        task["repeats"] = True
        task["date"] = self.date_for_frontend(year, month, 1)
        return task
    @staticmethod
    def date_for_frontend(year: int, month: int, day: int) -> str:
        return "{0}-{1:02d}-{2:02d}".format(int(year), int(month), int(day))
    def add_repetitive_tasks_from_calendar(self, year: int, month: int, data: Dict, tasks: Dict) -> Dict:
        current_day, current_month, current_year = GregorianCalendar.current_date()
        repetitive_tasks = self._repetitive_tasks_from_calendar(year, month, data)
        for repetitive_tasks_month in repetitive_tasks:
            for day, day_tasks in repetitive_tasks[repetitive_tasks_month].items():
                if repetitive_tasks_month not in tasks:
                    tasks[repetitive_tasks_month] = {}
                if day not in tasks[repetitive_tasks_month]:
                    tasks[repetitive_tasks_month][day] = []
                for task in day_tasks:
                    tasks[repetitive_tasks_month][day].append(task)
        return tasks
    def delete_task(self, calendar_id: str, year_str: str, month_str: str, day_str: str, task_id: int) -> None:
        deleted = False
        data = self.load_calendar(calendar_id)
        if (year_str in data[KEY_TASKS][KEY_NORMAL_TASK] and
                month_str in data[KEY_TASKS][KEY_NORMAL_TASK][year_str] and
                day_str in data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]):
            for index, task in enumerate(data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str]):
                if task["id"] == task_id:
                    data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str].pop(index)
                    deleted = True
        if not deleted:
            for index, task in enumerate(data[KEY_TASKS][KEY_REPETITIVE_TASK]):
                if task["id"] == task_id:
                    data[KEY_TASKS][KEY_REPETITIVE_TASK].pop(index)
                    if str(task_id) in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
                        del(data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][str(task_id)])
        self._save_calendar(data, filename=calendar_id)
    def update_task_day(self, calendar_id: str, year_str: str, month_str: str, day_str: str, task_id: int,
                        new_day_str: str) -> None:
        data = self.load_calendar(calendar_id)
        task_to_update = None
        for index, task in enumerate(data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str]):
            if task["id"] == task_id:
                task_to_update = data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str].pop(index)
        if task_to_update is None:
            return
        if new_day_str not in data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]:
            data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][new_day_str] = []
        data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][new_day_str].append(task_to_update)
        self._save_calendar(data, filename=calendar_id)
    def create_task(self, calendar_id: str, year: Optional[int], month: Optional[int], day: Optional[int], title: str,
                    is_all_day: bool, due_time: str, details: str, color: str, has_repetition: bool,
                    repetition_type: Optional[str], repetition_subtype: Optional[str], repetition_value: int) -> bool:
        details = details if len(details) > 0 else "&nbsp;"
        data = self.load_calendar(calendar_id)
        new_task = {"id": int(time.time()), "color": color, "due_time": due_time,
            		"is_all_day": is_all_day, "title": title, "details": details}
        if has_repetition:
            if repetition_type == self.REPETITION_SUBTYPE_MONTH_DAY and repetition_value == 0:
                return False
            new_task["repetition_type"] = repetition_type
            new_task["repetition_subtype"] = repetition_subtype
            new_task["repetition_value"] = repetition_value
            data[KEY_TASKS][KEY_REPETITIVE_TASK].append(new_task)
        else:
            if year is None or month is None or day is None:
                return False
            year_str = str(year)
            month_str = str(month)
            day_str = str(day)
            if year_str not in data[KEY_TASKS][KEY_NORMAL_TASK]:
                data[KEY_TASKS][KEY_NORMAL_TASK][year_str] = {}
            if month_str not in data[KEY_TASKS][KEY_NORMAL_TASK][year_str]:
                data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str] = {}
            if day_str not in data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str]:
                data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str] = []
            data[KEY_TASKS][KEY_NORMAL_TASK][year_str][month_str][day_str].append(new_task)
        self._save_calendar(data, filename=calendar_id)
        return True
    def hide_repetition_task_instance(self, calendar_id: str, year_str: str, month_str: str, day_str: str, task_id_str: str) -> None:
        data = self.load_calendar(calendar_id)
        if task_id_str not in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str] = {}
        if year_str not in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str]:
            data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str] = {}
        if month_str not in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str]:
            data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str][month_str] = {}
        data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id_str][year_str][month_str][day_str] = True
        self._save_calendar(data, filename=calendar_id)
    @staticmethod
    def add_task_to_list(tasks: Dict, day_str: str, month_str: str, new_task: Dict) -> None:
        if day_str not in tasks[month_str]:
            tasks[month_str][day_str] = []
        tasks[month_str][day_str].append(new_task)
    def _repetitive_tasks_from_calendar(self, year: int, month: int, data: Dict) -> Dict:
        if KEY_TASKS not in data:
            ValueError("Incomplete data for calendar")
        if KEY_REPETITIVE_TASK not in data[KEY_TASKS]:
            ValueError("Incomplete data for calendar")
        repetitive_tasks = {}  # type: Dict
        year_and_months = set([(source_day.year, source_day.month) for source_day in GregorianCalendar.month_days(year, month)])
        for source_year, source_month in year_and_months:
            month_str = str(source_month)
            year_str = str(source_year)
            repetitive_tasks[month_str] = {}
            for task in data[KEY_TASKS][KEY_REPETITIVE_TASK]:
                id_str = str(task["id"])
                monthly_task_assigned = False
                for week in GregorianCalendar.month_days_with_weekday(source_year, source_month):
                    for weekday, day in enumerate(week):
                        if day == 0:
                            continue
                        day_str = str(day)
                        if (
                            task["repetition_type"] == self.REPETITION_TYPE_WEEKLY and
                            not self._is_repetition_hidden_for_day(data, id_str, year_str, month_str, str(day)) and
                            task["repetition_value"] == weekday
                        ):
                            self.add_task_to_list(repetitive_tasks, day_str, month_str, task)
                        elif (
                            task["repetition_type"] == self.REPETITION_TYPE_MONTHLY and
                            not self._is_repetition_hidden(data, id_str, year_str, month_str)
                        ):
                            if task["repetition_subtype"] == self.REPETITION_SUBTYPE_WEEK_DAY:
                                if task["repetition_value"] == weekday and not monthly_task_assigned:
                                    monthly_task_assigned = True
                                    self.add_task_to_list(repetitive_tasks, day_str, month_str, task)
                            else:
                                if task["repetition_value"] == day:
                                    self.add_task_to_list(repetitive_tasks, day_str, month_str, task)
        return repetitive_tasks
    @staticmethod
    def _is_repetition_hidden_for_day(data: Dict, id_str: str, year_str: str, month_str: str, day_str: str) -> bool:
        if id_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            if (year_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str] and
                    month_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str][year_str] and
                    day_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str][year_str][month_str]):
                return True
        return False
    @staticmethod
    def _is_repetition_hidden(data: Dict, id_str: str, year_str: str, month_str: str) -> bool:
        if id_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            if (year_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str] and
                    month_str in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][id_str][year_str]):
                return True
        return False
    def _save_calendar(self, data: Dict, filename: str) -> None:
        self._clear_empty_entries(data)
        self._clear_past_hidden_entries(data)
        with open(os.path.join(".", self.data_folder, "{}.json".format(filename)), "w+") as file:
            json.dump(data, file)
    @staticmethod
    def _clear_empty_entries(data: Dict) -> None:
        years_to_delete = []
        for year in data[KEY_TASKS][KEY_NORMAL_TASK]:
            months_to_delete = []
            for month in data[KEY_TASKS][KEY_NORMAL_TASK][year]:
                days_to_delete = []
                for day in data[KEY_TASKS][KEY_NORMAL_TASK][year][month]:
                    if len(data[KEY_TASKS][KEY_NORMAL_TASK][year][month][day]) == 0:
                        days_to_delete.append(day)
                for day in days_to_delete:
                    del(data[KEY_TASKS][KEY_NORMAL_TASK][year][month][day])
                if len(data[KEY_TASKS][KEY_NORMAL_TASK][year][month]) == 0:
                    months_to_delete.append(month)
            for month in months_to_delete:
                del(data[KEY_TASKS][KEY_NORMAL_TASK][year][month])
            if len(data[KEY_TASKS][KEY_NORMAL_TASK][year]) == 0:
                years_to_delete.append(year)
        for year in years_to_delete:
            del(data[KEY_TASKS][KEY_NORMAL_TASK][year])
    @staticmethod
    def _clear_past_hidden_entries(data: Dict) -> None:
        _, current_month, current_year = GregorianCalendar.current_date()
        # normalize to 1st day of month
        current_date = datetime(current_year, current_month, 1, 0, 0)
        tasks_to_delete = []

        for task_id in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK]:
            for year in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id]:
                for month in data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id][year]:
                    task_date = datetime(int(year), int(month), 1, 0, 0)
                    if (current_date - task_date).days > current_app.config['DAYS_PAST_TO_KEEP_HIDDEN_TASKS']:
                        tasks_to_delete.append((year, month, task_id))

        for task_info in tasks_to_delete:
            year, month, task_id = task_info
            del(data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id][year][month])
            if len(data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id]) == 0:
                del(data[KEY_TASKS][KEY_REPETITIVE_HIDDEN_TASK][task_id])
