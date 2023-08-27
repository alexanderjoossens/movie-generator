import math
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.backend.my_dataclasses.movie import Movie
from src.backend.my_dataclasses.result import Result


def pack_result(
        movie_titles,
        movie_indices,
        vis1, 
        vis2User1, 
        vis2User2, 
        vis3_genres, 
        vis3_credits,
        movie_descriptions,
        movie_poster_paths
    ):

    movie_list = []

    nr_movies = len(movie_titles)

    for i_movie in range(nr_movies):
        movie = make_movie(
            movie_title=movie_titles[i_movie],
            movie_index=movie_indices[i_movie],
            vis1=vis1,
            vis2User1=vis2User1,
            vis2User2=vis2User2,
            vis3_genre=vis3_genres[i_movie],
            vis3_credit=vis3_credits[i_movie],
            movie_description=movie_descriptions[i_movie],
            movie_poster_path=movie_poster_paths[i_movie],
        )

        movie_list.append(movie)

    return Result(
        movie_list=movie_list
    )


def make_movie(
        movie_title,
        movie_index,
        vis1,
        vis2User1,
        vis2User2,
        vis3_genre,
        vis3_credit,
        movie_description,
        movie_poster_path
    ):

    # Visual 1: combined preferences
    combined_pref = math.trunc(vis1._get_value(movie_index, "percentage"))

    # Visual 2: balance
    balance_user1 = math.trunc(vis2User1._get_value(movie_index, "percentage"))
    balance_user2 = math.trunc(vis2User2._get_value(movie_index, "percentage"))

    # Visual 3: Bubbles   
    # - bubble 1
    #if (vis3_genre.shape[0] != 0):
    bubble1_genre = vis3_genre._get_value(0, 'genres')
    bubble1_genre_user1 = round(vis3_genre._get_value(0, 'User1_per'), 2)
    bubble1_genre_user2 = round(vis3_genre._get_value(0, 'User2_per'), 2)

    if bubble1_genre_user1 == 0.5:
        bubble1_genre_user1 = 0.51
        bubble1_genre_user2 = 0.49

    if (bubble1_genre_user1 == 0) & (bubble1_genre_user2 == 0):
        bubble1_genre_user1 = 0.51
        bubble1_genre_user2 = 0.49

    # else:
    #     bubble1_genre = None
    #     bubble1_genre_user1 = None
    #     bubble1_genre_user2 = None
    # - bubble 2   
    if ((vis3_genre.shape[0] != 1) and (vis3_genre.shape[0] != 0)):
        bubble2_genre = vis3_genre._get_value(1, 'genres')
        bubble2_genre_user1 = vis3_genre._get_value(1, 'User1_per')
        bubble2_genre_user2 = vis3_genre._get_value(1, 'User2_per')

        if bubble2_genre_user1 == 0.5:
            bubble2_genre_user1 = 0.51
            bubble2_genre_user2 = 0.49
        
        if (bubble2_genre_user1 == 0) & (bubble2_genre_user2 == 0):
            bubble2_genre_user1 = 0.51
            bubble2_genre_user2 = 0.49

    else:
        bubble2_genre = None
        bubble2_genre_user1 = None
        bubble2_genre_user2 = None

    # Visual 4: IMDB
    imdb_tekst = movie_description

    # Movie trailer
    url_trailer = "https://www.youtube.com/results?search_query=trailer {}".format(movie_title)

    # Movie poster
    poster_path = movie_poster_path

    return Movie(
            name=movie_title, 
            combined_pref=combined_pref, 
            balance_user1=balance_user1, 
            balance_user2=balance_user2, 
            bubble1_genre=bubble1_genre, 
            bubble1_genre_user1=bubble1_genre_user1, 
            bubble1_genre_user2=bubble1_genre_user2, 
            bubble2_genre=bubble2_genre, 
            bubble2_genre_user1=bubble2_genre_user1, 
            bubble2_genre_user2=bubble2_genre_user2, 
            imdb_tekst=imdb_tekst, 
            url_trailer=url_trailer,
            poster_path=poster_path,
        )