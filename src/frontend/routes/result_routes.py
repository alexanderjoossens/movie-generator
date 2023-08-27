import os, sys
import zmq
import zlib
import pickle
from dataclasses import asdict

from flask import render_template, redirect, request, session, Blueprint, current_app, url_for

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.frontend import config
from src.backend import my_dataclasses
from src.frontend.utils.usage_logger import UsageLogger
from src.frontend.utils.input_movies import get_movie_index, get_movie_title_list, get_movie_index_list


# -------------------------------------------------------------------------------------------------------------------------------------------

logger = UsageLogger()

result_blueprint = Blueprint('result-blueprint', __name__, template_folder='../templates/end_page_visual')

FAKE_REQUEST = True # Whether a fake like string should be used, otherwise looks at like string inside query parameters coming from the smartphones
NEW_PICKLE = False  # Whether a new pickle file should be creates (needs the backend)
USING_PICKLE = False # Whether the pickle file should be used for the result (otherwise makes request to backens)
WITH_STATE = False   # Needed for reload functionality, uses cookies mmm

DEPLOY = True
if DEPLOY:
    FAKE_REQUEST = False
    NEW_PICKLE = False
    USING_PICKLE = False
    WITH_STATE = True


movie_title_list = get_movie_title_list()
movie_index_list = get_movie_index_list()


@result_blueprint.route('/result-page')
def result_page():
    # Check if a session is currently ongoing, if not redirect to the homepage
    if DEPLOY: 
        session_id = session.get("session-id", None)
        if session_id == None: return redirect('/')


#1065_-1M6332_-1M161_1M1090_1M2262_1M3836_1M69_2M513_2M848_2 69_-1M848_-1M161_1M1090_1M2262_1M513_1M3836_1M1065_2M6332_2M519_2

    like_string_1 = request.args.get('like_string_1', " ")
    like_string_2 = request.args.get('like_string_2', " ")

    user_1_name = request.args.get('user_1')#.strip().split(" ")[0]
    user_2_name = request.args.get('user_2')#.strip().split(" ")[0]

    if WITH_STATE:
        if user_1_name != None:
            # user_1_name = request.args.get('user_1').strip().split(" ")[0]
            # user_2_name = request.args.get('user_2').strip().split(" ")[0]
            session["user_1"] = user_1_name
            session["user_2"] = user_2_name
            session_id = session["session-id"]
            logger.log_page_enter(session_id, "result")
        else:
            print("Like String:", like_string_1, like_string_2)
            user_1_name = session['user_1']
            user_2_name = session['user_2']





    if FAKE_REQUEST:
        movie_ids = movie_index_list
        #['161', '1090', '69', '1065', '2262', '513', '6332', '3836', '848', '519']

        # Normal feedback
        #feedback = [[-1, -1, 1, 1, 1, 1, 2, 2, 2, 0], [-1, -1, 1, 1, 1, 1, 1, 2, 2, 2]]
        feedback = [[-1, -1, 1, 1, 1, 1, 2, 2, 2, 0], [-1, -1, 1, 1, 1, 1, 1, 2, 2, 2]]
        # Only dislikes
        #feedback = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, 1, 1, 1, 1, 1, 2, 2, 2]]
        # Only no feedback
        #feedback = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [-1, -1, 1, 1, 1, 1, 1, 2, 2, 2]]

        recommendation_request = ""
        for j,user_feedback in enumerate(feedback):
            for i,rating in enumerate(user_feedback):
                recommendation_request += movie_ids[i] + "_" + str(rating)
                if i < len(user_feedback) - 1:
                    recommendation_request += "M"
            if j == 0:
                recommendation_request += " "
    
    else:
        recommendation_request = like_string_1 + " " + like_string_2


    if NEW_PICKLE:

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        if config.IN_DOCKER:
            socket.connect("tcp://group_1_moviegen_backend:5555")
        else:
            socket.connect("tcp://localhost:5555")

        socket.send_string(recommendation_request)

        z = socket.recv()
        p = zlib.decompress(z)
        result = pickle.loads(p) # The result object as defined in src/backend/my_dataclasses/result.py
        

        # Test code:
        # - writing pickle
        filehandler = open(os.path.join(os.path.dirname(__file__), "result.pickle"), 'wb') 
        pickle.dump(result, filehandler)
        filehandler.close()

    if WITH_STATE:
        # Check if the result is already in the cookies, if a refresh has happened
        result = session.get("result", None)

        
        # Not in the cookies, compute for first time the result
        if (result == None):
            if USING_PICKLE:
                # - loading pickle
                filehandler = open(os.path.join(os.path.dirname(__file__), "result.pickle"), 'rb') 
                result = pickle.load(filehandler)
                filehandler.close()
            else:
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                if config.IN_DOCKER:
                    socket.connect("tcp://group_1_moviegen_backend:5555")
                else:
                    socket.connect("tcp://localhost:5555")
                socket.send_string(recommendation_request)

                z = socket.recv()
                p = zlib.decompress(z)
                result = pickle.loads(p) # The result object as defined in src/backend/my_dataclasses/result.py
            session["result"] = result

    else:
        if USING_PICKLE:
            # - loading pickle
            filehandler = open(os.path.join(os.path.dirname(__file__), "result.pickle"), 'rb') 
            result = pickle.load(filehandler)
            filehandler.close()
        else:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            if config.IN_DOCKER:
                socket.connect("tcp://group_1_moviegen_backend:5555")
            else:
                socket.connect("tcp://localhost:5555")

            socket.send_string(recommendation_request)

            z = socket.recv()
            p = zlib.decompress(z)
            result = pickle.loads(p) # The result object as defined in src/backend/my_dataclasses/result.py

    

    print(result)

    if WITH_STATE:
        session_id = session["session-id"]
        logger.log_result(session_id, asdict(result))

    # Get the movies from the result (always up-to-date with the latest refresh)
    movie_1 = result.get_movie_1()
    movie_2 = result.get_movie_2()
    movie_3 = result.get_movie_3()
  
    # Get the correct template with different degree of explanation based on the session-id
    session_id = session["session-id"]
    end_page_template = get_end_page_template(session_id)

    trailer_redirect_link_1 =  url_for("result-blueprint.result_page_trailer", movie_column=1)
    trailer_redirect_link_2 =  url_for("result-blueprint.result_page_trailer", movie_column=2)
    trailer_redirect_link_3 =  url_for("result-blueprint.result_page_trailer", movie_column=3)

    movies = [movie_1, movie_2, movie_3]

    bubble1_strings = []
    bubble2_strings = []

    blue_list = ["#1cb2f6", 28, 168, 246]
    green_list = ["#97c95c", 151, 201, 92]

    donut_1 = []
    donut_2 = []
    donut_3 = []
    donut_4 = []
    donut_5 = []
    donut_6 = []

    donuts = [donut_1, donut_2, donut_3, donut_4, donut_5, donut_6]

    bubble_firsts = []
    bubble_seconds = []

    for i_movie,movie in enumerate(movies):
      
        donut_index = i_movie*2 

        donut_n = donuts[donut_index]

        percentage_user_1 = movie.bubble1_genre_user1
        percentage_user_2 = movie.bubble1_genre_user2

        if percentage_user_1 > percentage_user_2:
            bubble_firsts.append(percentage_user_1)
            bubble_seconds.append(percentage_user_2)
            donut_n.extend(blue_list)
            donut_n.extend(green_list)
        else:
            bubble_firsts.append(percentage_user_2)
            bubble_seconds.append(percentage_user_1)
            donut_n.extend(green_list)
            donut_n.extend(blue_list)

        donuts[donut_index] = donut_n

        donut_index = i_movie*2 + 1

        donut_n = donuts[donut_index]

        percentage_user_1 = movie.bubble2_genre_user1
        percentage_user_2 = movie.bubble2_genre_user2

        if ((percentage_user_1 != None) and (percentage_user_2 != None)):

            if percentage_user_1 > percentage_user_2:
                bubble_firsts.append(percentage_user_1)
                bubble_seconds.append(percentage_user_2)
                donut_n.extend(blue_list)
                donut_n.extend(green_list)
            else:
                bubble_firsts.append(percentage_user_2)
                bubble_seconds.append(percentage_user_1)
                donut_n.extend(green_list)
                donut_n.extend(blue_list)

            donuts[donut_index] = donut_n
        else:
            # When None, just take a combo
            bubble_firsts.append(percentage_user_1)
            bubble_seconds.append(percentage_user_2)
            donut_n.extend(blue_list)
            donut_n.extend(green_list)
            donuts[donut_index] = donut_n




    return render_template(end_page_template, movie_1=movie_1, movie_2=movie_2, movie_3=movie_3, user_1_name=user_1_name, user_2_name=user_2_name,
        trailer_redirect_link_1=trailer_redirect_link_1, trailer_redirect_link_2=trailer_redirect_link_2, trailer_redirect_link_3=trailer_redirect_link_3,
        bubble_firsts=bubble_firsts, bubble_seconds=bubble_seconds, donuts=donuts)
    
def get_end_page_template(session_id):
    first_letter = session_id[0]
        
    if first_letter == "a" or first_letter == "A":
        return "end_page_pseudo.html"
    if first_letter == "b" or first_letter == "B":
        return "end_page_percentage.html"
    if first_letter == "e" or first_letter == "E":
        return "end_page_bubbles.html"
    else:
        return "end_page_bubbles.html"

# Endpoint for refreshing movie 1
@result_blueprint.route('/result-page/refresh1')
def result_page_refresh_1():
    result = session["result"]

    from_movie = result.get_movie_1()
    to_movie = result.refresh_1() # Updates the index for movie 1, get_movie_1() will now return the new movie

    if (from_movie != to_movie):
        session_id = session["session-id"]
        logger.log_movie_refresh(session_id, 1, from_movie, to_movie)

    return redirect("/result-page")

# Endpoint for refreshing movie 2
@result_blueprint.route('/result-page/refresh2')
def result_page_refresh_2():
    result = session["result"]
    
    from_movie = result.get_movie_2()
    to_movie = result.refresh_2() # Updates the index for movie 2, get_movie_2() will now return the new movie

    if (from_movie != to_movie):
        session_id = session["session-id"]
        logger.log_movie_refresh(session_id, 2, from_movie, to_movie)

    return redirect("/result-page")

# Endpoint for refreshing movie 3
@result_blueprint.route('/result-page/refresh3')
def result_page_refresh_3():
    result = session["result"]
    
    from_movie = result.get_movie_3()
    to_movie = result.refresh_3() # Updates the index for movie 3, get_movie_3() will now return the new movie

    if (from_movie != to_movie):
        session_id = session["session-id"]
        logger.log_movie_refresh(session_id, 3, from_movie, to_movie)

    return redirect("/result-page")

@result_blueprint.route('/result-page/trailer')
def result_page_trailer():
    movie_column = request.args.get('movie_column')

    result = session["result"]

    movie_column = int(movie_column)

    if movie_column == 1:
        movie = result.get_movie_1()
    elif movie_column == 2:
        movie = result.get_movie_2()
    else:
        movie = result.get_movie_3()

    session_id = session["session-id"]
    logger.log_movie_choice(session_id, movie.name)
    
    return redirect(movie.url_trailer)