from dataclasses import dataclass
from .movie import Movie

@dataclass
class Result:
    movie_list: list[Movie]

    movie_1_index: int = 0
    movie_2_index: int = 1
    movie_3_index: int = 2

    def _get_movie(self, index: int): return self.movie_list[index]

    # Get the movie for each of the columns
    def get_movie_1(self): return self._get_movie(self.movie_1_index)
    def get_movie_2(self): return self._get_movie(self.movie_2_index)
    def get_movie_3(self): return self._get_movie(self.movie_3_index)

    def _get_new_movie_index(self): return max((self.movie_1_index, self.movie_2_index, self.movie_3_index)) + 1

    # Refresh a column and immediately get the new movie (if still available, otherwise returns the old one)
    def refresh_1(self): 
        new_movie_index = self._get_new_movie_index()
        if (new_movie_index < len(self.movie_list)):
            self.movie_1_index = new_movie_index
        return self.get_movie_1()
    def refresh_2(self): 
        new_movie_index = self._get_new_movie_index()
        if (new_movie_index < len(self.movie_list)):
            self.movie_2_index = new_movie_index
        return self.get_movie_2()
    def refresh_3(self): 
        new_movie_index = self._get_new_movie_index()
        if (new_movie_index < len(self.movie_list)):
            self.movie_3_index = new_movie_index
        return self.get_movie_3()

        