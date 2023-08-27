import os, sys

from flask import render_template, redirect, request, session, Blueprint, current_app, url_for

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.frontend import config
from src.frontend.utils.usage_logger import UsageLogger


# -------------------------------------------------------------------------------------------------------------------------------------------

logger = UsageLogger()

qr_blueprint = Blueprint('qr-blueprint', __name__, template_folder='../templates/qr')

@qr_blueprint.route('/qr-page')
def qr_page():
    # check if main page hasn't been skipped, if session-id is in the session
    session_id = session.get("session-id", None)
    if session_id == None: return redirect('/')

    logger.log_page_enter(session_id, "qr")


    qr_link_1 = "http://" + config.BASE_URL + url_for("movie-tinder-blueprint.movie_tinder", session_id=session_id, user_id=1)
    qr_link_2 = "http://" + config.BASE_URL + url_for("movie-tinder-blueprint.movie_tinder", session_id=session_id, user_id=2)

    return render_template("qr-page.html", qr_link_1=qr_link_1, qr_link_2=qr_link_2, base_url=config.BASE_URL, session_id=session_id)