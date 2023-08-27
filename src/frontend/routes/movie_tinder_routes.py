import os, sys

from flask import render_template, redirect, request, session, Blueprint, current_app, url_for
from flask_qrcode import QRcode
from flask_session import Session
from flask_socketio import SocketIO

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.frontend.utils.input_movies import get_movie_index, get_movie_title_list, get_movie_index_list, get_movie_poster_list, get_movie_genres_list
from src.frontend import config
from src.frontend.utils.usage_logger import UsageLogger


# -------------------------------------------------------------------------------------------------------------------------------------------

logger = UsageLogger()

movie_tinder_blueprint = Blueprint('movie-tinder-blueprint', __name__, template_folder='../templates/movie_tinder')

socketio = SocketIO(current_app)

movie_title_list = get_movie_title_list()
movie_index_list = get_movie_index_list()
movie_poster_list = get_movie_poster_list()
movie_genres_list = get_movie_genres_list()

@movie_tinder_blueprint.route('/movie-tinder')
def movie_tinder():
    # session.clear()

    session_id = request.args.get('session_id')
    user_id = request.args.get('user_id')

    logger.log_page_enter(session_id, "tinder_index_" + user_id)
    logger.log_scan_time(session_id, user_id)

    session["session-id"] = session_id
    session["user-id"] = user_id

    session["movie_tinder_index"] = 0
    session["dislike_list"] = []
    session["like_list"] = []
    session["superlike_list"] = []
    session["nolike_list"] = []

    return redirect('/movie-tinder/start')

@movie_tinder_blueprint.route('/movie-tinder/start')
def movie_tinder_start():

    session_id = session["session-id"]
    user_id = session["user-id"]

    socketio.emit(
        'qr-scanned', 
        {
            'session_id': session_id,
            'user_id': user_id
        })

    socketio.emit(
        'tinder-state', 
        {
            'session_id': session_id,
            'user_id': user_id,
            'tinder_state': "Inputting username ..."
        })

    return render_template("movie-tinder-start-form.html")
    
@movie_tinder_blueprint.route('/movie-tinder/start', methods=['POST'])
def movie_tinder_start_post():
    user_name = request.form['user-name']
    session["user-name"] = user_name

    session_id = session["session-id"]
    user_id = session["user-id"]

    logger.log_page_enter(session_id, "tinder_start_post_" + user_id)
    logger.log_user_name(session_id, user_id, user_name)

    print("USERNAME:", user_name)

    socketio.emit(
        'new-user', 
        {
            'session_id': session_id,
            'user_id': user_id,
            'user_name': user_name
        })

    return redirect("/movie-tinder/info")

#  new
@movie_tinder_blueprint.route('/movie-tinder/info')
def movie_tinder_info():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')

    logger.log_page_enter(session_id, "tinder_info_" + user_id)

    socketio.emit(
        'tinder-state', 
        {
            'session_id': session_id,
            'user_id': user_id,
            'tinder_state': "Reading info ..."
        })

    return render_template("/movie-tinder-info.html")

# new
# @movie_tinder_blueprint.route('/movie-tinder/info')
# def movie_tinder_start_post():
#     return redirect("/movie-tinder/movies")

@movie_tinder_blueprint.route('/movie-tinder/movies')
def movie_tinder_movies():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')

    movie_tinder_index = session.get("movie_tinder_index", None)
    if (movie_tinder_index == None) :
        session["movie_tinder_index"] = 0
        movie_tinder_index = 0

    logger.log_page_enter(session_id, "tinder_movies_" + user_id + "_" + str(movie_tinder_index))
    
    movie_title = movie_title_list[movie_tinder_index]
    movie_index = movie_index_list[movie_tinder_index]
    movie_width = [185, 300, 400, 500][1]
    movie_image = "https://image.tmdb.org/t/p/w" + str(movie_width) + movie_poster_list[movie_tinder_index][1] #"movie"  + str(movie_tinder_index+1) + ".jpg"
    movie_genres = movie_genres_list[movie_tinder_index]


    logger.log_input_movie(session_id, user_id, movie_title, movie_index)

    session["movie_tinder_index"] += 1

    dislike_link = "/movie-tinder/movies/dislike?movie_title=" + str(movie_index)
    like_link = "/movie-tinder/movies/like?movie_title=" + str(movie_index)
    superlike_link = "/movie-tinder/movies/superlike?movie_title=" + str(movie_index)
    no_link = "/movie-tinder/movies/nolike?movie_title=" + str(movie_index) # best ook een route om de film bij te houden zodat niet 2x zelfde geven

    socketio.emit(
        'tinder-state', 
        {
            'session_id': session_id,
            'user_id': user_id,
            'tinder_state': "Liking movies (" + str(movie_tinder_index*10) + "%) ..."
        })

    return render_template(
        "movie-tinder-movie.html", 
        movie_title=movie_title,
        movie_index=movie_index,
        dislike_link=dislike_link, 
        like_link=like_link, 
        superlike_link=superlike_link,
        no_link=no_link,
        movie_image=movie_image)

@movie_tinder_blueprint.route('/movie-tinder/movies/dislike')
def movie_tinder_movies_dislike():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')

    movie_title = request.args.get('movie_title')

    dislike_list = session.get("dislike_list", [])
    dislike_list.append(movie_title)
    session["dislike_list"] = dislike_list

    session_id = session["session-id"]
    user_id = session["user-id"]
    logger.log_feedback(session_id, user_id, "dislike", movie_title)

    return redirect('/movie-tinder/movies/likecount')

@movie_tinder_blueprint.route('/movie-tinder/movies/like')
def movie_tinder_movies_like():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')

    movie_title = request.args.get('movie_title')

    like_list = session.get("like_list", [])
    like_list.append(movie_title)
    session["like_list"] = like_list

    session_id = session["session-id"]
    user_id = session["user-id"]
    logger.log_feedback(session_id, user_id, "like", movie_title)

    return redirect('/movie-tinder/movies/likecount')

@movie_tinder_blueprint.route('/movie-tinder/movies/superlike')
def movie_tinder_movies_superlike():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')

    movie_title = request.args.get('movie_title')

    superlike_list = session.get("superlike_list", [])
    superlike_list.append(movie_title)
    session["superlike_list"] = superlike_list

    session_id = session["session-id"]
    user_id = session["user-id"]
    logger.log_feedback(session_id, user_id, "superlike", movie_title)

    return redirect('/movie-tinder/movies/likecount')

@movie_tinder_blueprint.route('/movie-tinder/movies/nolike')
def movie_tinder_movies_nolike():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')

    movie_title = request.args.get('movie_title')

    nolike_list = session.get("nolike_list", [])
    nolike_list.append(movie_title)
    session["nolike_list"] = nolike_list

    session_id = session["session-id"]
    user_id = session["user-id"]
    logger.log_feedback(session_id, user_id, "nolike", movie_title)

    return redirect('/movie-tinder/movies/likecount')

@movie_tinder_blueprint.route('/movie-tinder/movies/likecount')
def movie_tinder_movies_likecount():
    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    # Fool proof
    if session_id == None: return redirect('/')


    if session["movie_tinder_index"] >= len(movie_title_list):
        return redirect('/movie-tinder/end')
    else:
        return redirect('/movie-tinder/movies')


@movie_tinder_blueprint.route('/movie-tinder/end')
def movie_tinder_end():


    session_id = session.get("session-id", None)
    user_id = session.get("user-id", None)
    user_name = session.get("user-name", None)

    # Fool proof
    if session_id == None: return redirect('/')

    dislike_list = session.get("dislike_list", [])
    like_list = session.get("like_list", [])
    superlike_list = session.get("superlike_list", [])
    nolike_list = session.get("nolike_list", [])

    print(dislike_list)
    print(like_list)
    print(superlike_list)
    print(nolike_list)
    
    dislike_ids = [i.strip().split(",")[-1] for i in dislike_list]
    like_ids = [i.strip().split(",")[-1] for i in like_list]
    superlike_ids = [i.strip().split(",")[-1] for i in superlike_list]
    no_like_ids = [i.strip().split(",")[-1] for i in nolike_list]

    movie_ids_and_rating = []


    for i in range(10):
        if str(i) in dislike_ids:
            movie_ids_and_rating.append(str(i) + "_-1")
        if str(i) in like_ids:
            movie_ids_and_rating.append(str(i) + "_1")
        if str(i) in superlike_ids:
            movie_ids_and_rating.append(str(i) + "_2")
        if str(i) in no_like_ids:
            movie_ids_and_rating.append(str(i) + "_0")


    # for i in dislike_ids:
    #     movie_ids_and_rating.append(i + "_-1")
    # for i in like_ids:
    #     movie_ids_and_rating.append(i + "_1")
    # for i in superlike_ids:
    #     movie_ids_and_rating.append(i + "_2")
    # for i in no_like_ids:
    #     movie_ids_and_rating.append(i + "_0")

    like_string = "M".join(movie_ids_and_rating)

    logger.log_tinder_likes(session_id, user_id, dislike_list, like_list, superlike_list, nolike_list, like_string)

    redirect_link = url_for("result-blueprint.result_page")

    socketio.emit(
        'movie-tinder-end', 
        {
            'session_id': session_id,
            'user_id': user_id,
            'user_name': user_name,
            'redirect_link': redirect_link,
            'like_string': like_string
        })

    socketio.emit(
        'tinder-state', 
        {
            'session_id': session_id,
            'user_id': user_id,
            'tinder_state': "Done"
        })

    # return redirect('/end_page_visual/end_page')
    # return "dislike: " + str(session.get("dislike_list", [])) + " | like: " + str(session.get("like_list", [])) + " | superlike: " + str(session.get("superlike_list", []))
    return render_template("movie-tinder-final.html")

