from dataclasses import dataclass

@dataclass
class Movie:
    name: str
    combined_pref: str
    balance_user1: str
    balance_user2: str
    bubble1_genre: str
    bubble1_genre_user1: str
    bubble1_genre_user2: str
    bubble2_genre: str
    bubble2_genre_user1: str
    bubble2_genre_user2: str
    imdb_tekst: str
    url_trailer: str
    poster_path: str
