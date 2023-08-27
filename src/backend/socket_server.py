import zmq
import numpy as np
import pandas as pd
import zlib
import pickle
from scipy import stats
from threading import Thread
import urllib.request
import socket
import sys, os
import time
from urllib import request, parse
import socket


from recommender import ContentBasedRecommender
import combiner
import visualiser
import packer

SOCKET_ADDRESS = "tcp://*:5555"
MOVIE_LOAD_LIMIT = 700000
MOVIE_LIMIT = 600

# Add project root folder to PATH
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.frontend import config
from src.frontend.utils.input_movies import get_movie_title_list, get_movie_index_list


def healthcheck():
    while True:
        try:
            urllib.request.urlopen("https://hc-ping.com/" + config.HEALTHCHECK_UUID_BACKEND, timeout=10)
        except socket.error as e:
            print("Healthcheck ping failed: %s" % e)
        time.sleep(10)


class Server:

    def __init__(self, socket_address, movie_load_limit, movie_limit):
        self.socket_address = socket_address
        self.movie_load_limit = movie_load_limit
        self.movie_limit = movie_limit

    def setup(self):

        print("  Setting up socket connection...")
        print("    Address:", self.socket_address)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.socket_address)
        print("  Done!")

        print()

        print("  Setting up recommender")
        print("    Movie load limit:", self.movie_load_limit)
        print("    Movie limit:", self.movie_limit)
        self.recommender = ContentBasedRecommender(self.movie_load_limit, self.movie_limit)
        self.recommender.init()
        print("  Done!")


    


    def run(self):

        print("Server started running")

        print()

        print("Starting setup sequence ...")
        self.setup()
        print("Done!")

        print()

        print("Starting healthcheck pinger ...")
        t = Thread(target=healthcheck)
        t.start()

        print("Listening for requests ...")

        while True:
            #try:
                # Get latest request for recommendations
                recommendation_request = self.socket.recv_string()
                print("Received request", recommendation_request)

                # Process the received string
                # - Split per user
                (like_string_1, like_string_2) = recommendation_request.strip().split(" ")
                # - Extract movie index and rating information
                feedback_1 = like_string_to_array(like_string_1)
                feedback_2 = like_string_to_array(like_string_2)
                # - Combine movies
                movies_1 = feedback_1[0,:]
                rating_1 = feedback_1[1,:]
                movies_2 = feedback_2[0,:]
                rating_2 = feedback_2[1,:]

                # rating_1 = np.array([1.5 if r == 2 else r for r in rating_1])
                # rating_2 = np.array([1.5 if r == 2 else r for r in rating_2])

                rating_1 = np.array([max(r, -0.1) for r in rating_1])
                rating_2 = np.array([max(r, -0.1) for r in rating_2])

                movies_combined = np.union1d(movies_1, movies_2)
                # - Pad the ratings (for when one uses does not have a rating for a certain movie)
                padded_rating_1 = pad_rating(movies_1, rating_1, movies_combined)
                padded_rating_2 = pad_rating(movies_2, rating_2, movies_combined)
                
                # Compute the similarities
                movie_similarities = np.array([self.recommender.get_similarity_scores(movie) for movie in movies_combined])
                movie_similarities = pd.DataFrame.transpose(pd.DataFrame(movie_similarities))

                # Convert similarities to per-input-movie percentiles
                movie_similarities_percentiles = movie_similarities.copy()
                for i in range(movie_similarities_percentiles.shape[1]):
                    # Calculate the percentile distribution per input movie / per column
                    movie_similarities_percentiles.loc[:,i] = stats.percentileofscore(movie_similarities_percentiles.loc[:,i], movie_similarities_percentiles.loc[:,i])


                # Aggragated similarities for each user based on their rating
                user1_lst = combiner.get_one_list(padded_rating_1, movie_similarities_percentiles)
                user2_lst = combiner.get_one_list(padded_rating_2, movie_similarities_percentiles)

                # Aggragating for the whole group
                group_lst = combiner.groep_rec_least(user1_lst, user2_lst)

                # Remove the input movies
                print(group_lst)
                group_lst = group_lst.reset_index()
                print(group_lst)
                input_filter = ~group_lst["index"].isin([int(x) for x in get_movie_index_list()])
                print(input_filter)
                group_lst = group_lst[input_filter]
                group_lst = group_lst.set_index("index")
                print(group_lst)

                # Getting the top 15
                result = combiner.filter_top_15(group_lst)
                result = result.reset_index()
                print("Result", result)

                # Only get part of dataset that is included in top 15
                result_indices = result["index"].to_numpy()
                result_movie_similarities_percentiles_2 = movie_similarities_percentiles[movie_similarities_percentiles.index.isin(result_indices)]

                # Check for user input with only dislikes / no feedback
                padded_rating_1, padded_rating_2, result_movie_similarities_percentiles_2 = self.save_bad_feedback_situation(padded_rating_1, padded_rating_2, result_movie_similarities_percentiles_2)

                # Visual 2
                vis2User1 = visualiser.vis2(padded_rating_1, result_movie_similarities_percentiles_2)
                vis2User2 = visualiser.vis2(padded_rating_2, result_movie_similarities_percentiles_2) 

                # Visual 1
                vis1 = visualiser.vis1(vis2User1, vis2User2)   

                # Visual 3
                vis3_genres = []
                for result_index in result_indices:
                    vis3_genres.append(
                        visualiser.vis3(
                            "genres", 
                            result_index, 
                            movies_combined, 
                            pd.array(padded_rating_1), 
                            pd.array(padded_rating_2), 
                            self.recommender.data
                            )
                        )

                vis3_credits = []
                for result_index in result_indices:
                    vis3_credits.append(
                        visualiser.vis3(
                            "credits", 
                            result_index, 
                            movies_combined, 
                            pd.array(padded_rating_1), 
                            pd.array(padded_rating_2), 
                            self.recommender.data
                            )
                        )
                
                # Visual 4
                vis4 = visualiser.vis4(result_index, movies_combined, padded_rating_1, padded_rating_2, self.recommender.data)

                # Movie titles
                movie_titles = [self.recommender.titles[index] for index in result_indices]

                print(movie_titles)

                # Movie descriptions
                movie_descriptions = [self.recommender.data["overview"][index] for index in result_indices]

                # Poster path
                movie_poster_paths = [self.recommender.data["poster_path"][index] for index in result_indices]

                # Create resulting datastructure
                result = packer.pack_result(
                    movie_titles=movie_titles,
                    movie_indices=result_indices,
                    vis1=vis1,
                    vis2User1=vis2User1,
                    vis2User2=vis2User2,
                    vis3_genres=vis3_genres,
                    vis3_credits=vis3_credits,
                    movie_descriptions=movie_descriptions,
                    movie_poster_paths=movie_poster_paths
                )


                p = pickle.dumps(result)
                z = zlib.compress(p)

                self.socket.send(z)


            # except Exception as e:
            #     print(e)
            #     notify_exception(e)

    

    # Function to save a situation where one (or both) user(s) gave bad feedback (only dislikes or only no feedbacks)
    def save_bad_feedback_situation(self, padded_rating_1, padded_rating_2, result_movie_similarities_percentiles_2):

        # Create index column (to get the ID's of the recommended movies)
        result_movie_similarities_percentiles_2 = result_movie_similarities_percentiles_2.reset_index()
        recommended_movies = result_movie_similarities_percentiles_2["index"]

        print(result_movie_similarities_percentiles_2)

        # Check if we got bad feedback
        user_1_bad_ratings = ((not (1 in padded_rating_1)) and (not (2 in padded_rating_1)))
        user_2_bad_ratings = ((not (1 in padded_rating_2)) and (not (2 in padded_rating_2)))


        # Add the recommended movies as if they were input movies
        counter = 10
        if (user_1_bad_ratings or user_2_bad_ratings):
            print("FIXING FEEDBACK")
            for recommended_movie in recommended_movies:
                sim = self.recommender.get_similarity_scores(recommended_movie)
                sim = sim[recommended_movies]
                result_movie_similarities_percentiles_2[counter] = stats.percentileofscore(sim, sim)
                counter += 1

            # Handel the ratings
            #if (user_1_bad_ratings):
                # If user gave bad feedback, let them like all the recommended movies as if they were input movies
            padded_rating_1.extend([1 for i in range(len(recommended_movies))])
            #else:
                # If user gave good feedback, ignore the added recommended movies
                #padded_rating_1.extend([0 for i in range(len(recommended_movies))])

            #if (user_2_bad_ratings):
            padded_rating_2.extend([1 for i in range(len(recommended_movies))])
            #else:
                #padded_rating_2.extend([0 for i in range(len(recommended_movies))])

            print(result_movie_similarities_percentiles_2)
            print(padded_rating_1)
            print(padded_rating_2)


        # Set index column back in place
        result_movie_similarities_percentiles_2 = result_movie_similarities_percentiles_2.set_index("index")

        

        return padded_rating_1, padded_rating_2, result_movie_similarities_percentiles_2

    
# Some helper functions

def like_string_to_array(like_string):
    return np.swapaxes(np.array([ np.array(list(map(lambda x: int(x), movie_feedback.strip().split("_")))) for movie_feedback in like_string.strip().split("M")]), 0, 1)

def pad_rating(movies, rating, larger_movies):
    return [
        rating[movies.tolist().index(movie_id)] if movie_id in movies.tolist() else 0 for movie_id in larger_movies
        ]

# Getting the names of the movies
def from_indices_to_titles(recommender, result):
    return [recommender.titles[i] for i in result['index']]

def notify_exception(exception):
        exception = str(exception)
        try:
            request.urlopen("https://hc-ping.com/" + config.HEALTHCHECK_UUID_BACKEND + "/fail", timeout=10, data=exception.encode('utf-8'))
        except socket.error as e:
            print("Healthcheck log failed: %s" % e)


if __name__ == "__main__":
    server = Server(
        socket_address=SOCKET_ADDRESS,
        movie_load_limit=MOVIE_LOAD_LIMIT,
        movie_limit=MOVIE_LIMIT
    )
    server.run()





#while True:




#socket.send(b"OK")

# 0_-1M357_1 0_-1M357_1M265_2

