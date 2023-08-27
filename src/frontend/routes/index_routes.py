import os, sys
import time

from flask import render_template, redirect, request, session, Blueprint, current_app, url_for

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.frontend.utils.usage_logger import UsageLogger


# -------------------------------------------------------------------------------------------------------------------------------------------

logger = UsageLogger()

index_blueprint = Blueprint('index-blueprint', __name__, template_folder='../templates/index')

@index_blueprint.route('/')
def main_page():
    session.clear()

    logger.health_log_message("None", "Landed on homepage")

    return render_template("homepage.html")

@index_blueprint.route('/', methods=['POST'])
def main_page_post():
    session_id = request.form['session-id']
    session_timestamp = time.time()
    session_id_with_timestamp = session_id + "|" + str(session_timestamp)

    session["session-id"] = session_id_with_timestamp

    logger.init_session(session_id_with_timestamp)
    logger.log_page_enter(session_id_with_timestamp, "index")
    logger.health_log_message(session_id, "Filled in session ID: [" + session_id + "] with Timestamp: [" + str(session_timestamp) + "]")

    return redirect("/qr-page")