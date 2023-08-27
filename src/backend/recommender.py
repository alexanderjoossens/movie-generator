import os, sys
import time
import math
import pickle

import multiprocessing
from multiprocessing import Pool
from itertools import repeat

import pandas as pd
import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.frontend.utils.input_movies import get_movie_title_list

class ContentBasedRecommender:
    
    def __init__(self, movie_load_limit=None, movie_limit=500, max_number_credits=3):
        self.movie_limit = movie_limit
        self.movie_load_limit = movie_load_limit
        self.max_number_credits = max_number_credits
        self.dataset_path = os.path.join(os.getcwd(),"..","..","dataset", "millions-of-movies", "movies.csv")
        self.export_path = os.path.join(os.getcwd(), "..","..", "models")
        
        self.num_cores = multiprocessing.cpu_count()
        self.num_partitions = self.num_cores-2 # leave some cores for other processes
        
        self.modes = ("DESCRIPTION", "METADATA", "HYBRID")
        
    def init(self, recompute=False, export=False):
        
        self.load_dataset()
        self.limit_dataset()
        
        if recompute:
            self.preprocess_data()
            self.build_bow_cosine_sim()
            self.build_soup_cosine_sim()
            if export:
                self.export_similarity_matrices()
        else:
            self.preprocess_data()
            self.import_similarity_matrices()
            
        self.build_title_index()
        self.build_poster_paths()
        self.build_movie_genres()

        if recompute:
            self.export_title_index()
            self.export_poster_paths()
            self.export_movie_genres()
        
    def load_dataset(self):
        print("Loading dataset ...", end =" ")
        start = time.time()
        self.data = pd.read_csv(self.dataset_path, nrows=self.movie_load_limit)
        print("Done! (took {} seconds)".format(time.time()-start))
        
    def limit_dataset(self):
        
        # limit to English movies
        language_filter = self.data["original_language"]=="en"
        self.data = self.data[language_filter]
        
        # Remove duplicates
        self.data = self.data[self.data["title"].duplicated() == False]
        self.data = self.data.drop_duplicates(subset=['title'])
        self.data = self.data.reset_index(drop=True)

        # filter movies with no genre
        # --- Genres ---
        # change "-" seperated string to a list
        self.data["genres"] = self.data["genres"].apply(lambda x: x.strip().split("-") if isinstance(x, str) else [])
        genre_filter = self.data["genres"].map(len) >= 1
        self.data = self.data[genre_filter]

        # Filter horror movies
        #horror_filter = ~self.data["genres"].isin(["Horror"])
        #self.data = self.data[horror_filter]

        # Filter christmas movies
        titles_words = self.data["title"]
        #print(titles_words)
        #titles_words.apply(lambda x: x.strip().split(" "))
        #christmas_filter = titles_words.apply(lambda x: x in(['Christmas', 'christmas']))

        #christmas_filter = ~titles_words.str.contains("Christmas|christmas", case=False, regex=True)
        #print(christmas_filter)
        #self.data = self.data[christmas_filter]

        #print(self.data)


        # limit number of movies
        # - Get the input movies that at least should be included
        input_movies = self.data[self.data["title"].isin(get_movie_title_list())]
        self.data = self.data[~self.data["title"].isin(get_movie_title_list())]
        # - Sort movies by popularity
        self.data = self.data.sort_values("popularity", ascending=False)
        #self.sort_movies()
        # - Add the input movies to the top
        self.data = pd.concat([input_movies, self.data])
        print(self.data.head(20))
        # - Limit the number of movies
        load_limit = self.movie_load_limit if (self.movie_load_limit!=None) else math.inf
        self.data = self.data.head(min(load_limit, self.movie_limit))      
        # - Reset the index column
        self.data = self.data.reset_index(drop=True)

        print(self.data.tail(10))

        print(self.data.iloc[260:270,:])

       

        
    def preprocess_data(self):
        
        print("Pre-processing dataset ...", end =" ")
        start = time.time()     
        
        
        # --- Keywords ---
        # change "-" seperated string to a list
        self.data["keywords"] = self.data["keywords"].apply(lambda x: x.strip().split("-") if isinstance(x, str) else [])
        # remove spaces and convert to lower case
        self.data["keywords"] =  self.data["keywords"].apply(lambda x: [str.lower(i.replace(" ", "_")) for i in x]) 
        
        # --- Tagline ---
        # change "N/A" to an empty string
        self.data["tagline"] = self.data["tagline"].fillna("")
        
        # --- Overview ---
        # change "N/A" to an empty string
        self.data["overview"] = self.data["overview"].fillna("")
        
        # --- Overview & Tagline
        # combine two column to get a single one that contains all writen out text (to build BOW)
        self.data["overview & tagline"] = self.data["overview"] + self.data["tagline"]
        
        # --- Credits ---
        # change "-" seperated string to a list
        self.data["credits"] = self.data["credits"].apply(
            lambda x: x.strip().split("-") if isinstance(x, str) else []) 
        # only keep top self.max_number_credits most important credits
        self.data["credits"] = self.data["credits"].apply(
            lambda x: x[:self.max_number_credits] if len(x) >=self.max_number_credits else x) 
        # remove spaces and convert to lower case
        self.data["credits"] = self.data["credits"].apply(
            lambda x: [str.lower(i.replace(" ", "_")) for i in x]) 
        
        # --- Soup --
        self.create_word_soup()
        
        print("Done! (took {} seconds)".format(time.time()-start))
        
    def create_word_soup(self):
                
        # rebuild indexing based on keywords
        genre_TM = self.data.apply(lambda x: pd.Series(x['keywords']),axis=1).stack().reset_index(level=1, drop=True) 
        genre_TM.name = 'keyword'
        genre_TM = genre_TM.value_counts()
        
        # create filter based on keyword count
        genre_TM = genre_TM[genre_TM > 1] 
        
        # function to filter keywords based on the "genre_TM" filter
        def filter_keywords(x):
            words = []
            for i in x:
                if i in genre_TM:
                    words.append(i)
            return words   
        # remove keywords that only appear once
        self.data['keywords'] = self.data['keywords'].apply(filter_keywords)
        
        # create word soup
        self.data['soup'] =  self.data['keywords'] +  self.data['credits'] + self.data['genres']
        self.data['soup'] =  self.data['soup'].apply(lambda x: ' '.join(x))
        
        
    def build_bow_cosine_sim(self):
    
        print("Building BOW similarity matrix ...", end =" ")
        start = time.time()
        
        # create BOW & calculate tf-idf matrix
        # - scrapes all words / 2 word ngrams
        # - calculates tf-idf for each word / ngram
        # - constructs a matrix with for each movie the tf-idf values of all the words / ngrams it contains
        tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(self.data['overview & tagline'])
        #tfidf_matrix = parallelize_tfidf(self.data, self.num_partitions, self.num_cores) # doesn't seem to work
        
      
        
        # results in a (#movies x #movies)-matrix with pairwise similarity values
        # similarity based on equal word usage, weighted with tf-idf values
        self.cosine_sim_bow = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        print("Done! (took {} seconds)".format(time.time()-start))
        
    def build_soup_cosine_sim(self):
        
        print("Building soup similarity matrix ...", end =" ")
        start = time.time()
        
        count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
        count_matrix = count.fit_transform(self.data['soup'])
        
        # compute similarity matrix
        self.cosine_sim_soup = cosine_similarity(count_matrix, count_matrix)
        
        print("Done! (took {} seconds)".format(time.time()-start))
        
    def build_title_index(self):
        
        print("Building title index ...", end =" ")
        start = time.time()
        
        #self.data = self.data.reset_index()
        print(self.data.shape)
        self.titles = self.data['title']
        print(len(self.titles))
        self.title_indices = pd.Series(self.data.index, index=self.titles) 
        
        print("Done! (took {} seconds)".format(time.time()-start))
    
    def export_title_index(self):
        self.title_indices.to_csv(os.path.join(os.getcwd(), "..", "..", "title_export.csv"))

    def build_poster_paths(self):
        self.poster_paths = pd.Series(self.data['poster_path']) 

    def export_poster_paths(self):
        self.poster_paths.to_csv(os.path.join(os.getcwd(), "..", "..", "poster_path_export.csv"))

    def build_movie_genres(self):
        self.movie_genres = pd.Series(self.data['genres']) 

    def export_movie_genres(self):
        self.movie_genres.to_csv(os.path.join(os.getcwd(), "..", "..", "movie_genres_export.csv"))
        
    def export_similarity_matrices(self):
        
        print("Exporting pre-computed model ...", end =" ")
        start = time.time()

        file = open(os.path.join(
            self.export_path, 
            'cosine_sim_bow_ll{}_ml{}.pickle'.format(self.movie_load_limit, self.movie_limit)
        ), 'wb')
        pickle.dump(self.cosine_sim_bow, file)
        file.close()
        
        file = open(os.path.join(
            self.export_path, 
            'cosine_sim_soup_ll{}_ml{}.pickle'.format(self.movie_load_limit, self.movie_limit)
        ), 'wb')
        pickle.dump(self.cosine_sim_soup, file)
        file.close()
        
        print("Done! (took {} seconds)".format(time.time()-start))

    
    def import_similarity_matrices(self):
        
        print("Importing pre-computed model ...", end =" ")
        start = time.time()
        
        self.cosine_sim_bow = pickle.load( open(os.path.join(
            self.export_path, 
            'cosine_sim_bow_ll{}_ml{}.pickle'.format(self.movie_load_limit, self.movie_limit)
        ), 'rb') )
        self.cosine_sim_soup = pickle.load( open(os.path.join(
            self.export_path, 
            'cosine_sim_soup_ll{}_ml{}.pickle'.format(self.movie_load_limit, self.movie_limit)
        ), 'rb') )
        
        print("Done! (took {} seconds)".format(time.time()-start))

    def sort_movies(self):

        movies = self.data

        vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int') # get the number of votes of these movies
        vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int') # get the average of the votes
        C = vote_averages.mean() # average of the averages
        m = vote_counts.quantile(0.60) # get 60th percentile of the vote counts
        qualified = movies[(movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())] # get 60th percentile movies
        qualified['vote_count'] = qualified['vote_count'].astype('int')
        qualified['vote_average'] = qualified['vote_average'].astype('int')
        qualified['wr'] = qualified.apply(lambda x : self.weighted_rating(x,m,C), axis=1)
        qualified = qualified.sort_values('wr', ascending=False)

        self.data = qualified

    
    # IMDB's weighted rating formula
    def weighted_rating(self, x,m,C):
        v = x['vote_count']
        R = x['vote_average']
        return (v/(v+m) * R) + (m/(m+v) * C)
        
    def get_description_similarity_scores(self, idx):
        sim_scores = np.array(list(enumerate(self.cosine_sim_bow[idx]))) # get the similarities with the rest of the dataset
        return sim_scores
    
    def get_metadata_similarity_scores(self, idx):
        sim_scores = np.array(list(enumerate(self.cosine_sim_soup[idx]))) # get the similarities with the rest of the dataset
        return sim_scores
    
    def get_similarity_scores(self, movie_idx, mode="HYBRID", sorted_scored=False):
        if mode == "DESCRIPTION": sim_scores = self.get_description_similarity_scores(movie_idx)
        if mode == "METADATA": sim_scores = self.get_metadata_similarity_scores(movie_idx)
        if mode == "HYBRID": sim_scores = (self.get_metadata_similarity_scores(movie_idx) + self.get_description_similarity_scores(movie_idx))/2
        
        if sorted_scored:
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        else:
            sim_scores = sim_scores[:,1]   
        
        return sim_scores
        
    def get_recommended_titles(self, title, mode="HYBRID"):
        sim_scores = self.get_similarity_scores(title, mode, sorted_scored=True)
        sim_scores = sim_scores[1:]
        movie_indices = [i[0] for i in sim_scores]     
        
        return self.titles.iloc[movie_indices]

    
    
    
def tfidf_func(data, tfidf_vectorizer):
    #print("Process working on: ",data)    
    tfidf_matrix = tfidf_vectorizer.transform(data['overview & tagline'])
    #return pd.DataFrame(tfidf_matrix.toarray())
    return tfidf_matrix

def parallelize_tfidf(df, num_partitions, num_cores):
    a = np.array_split(df, num_partitions)
    pool = Pool(num_cores)
    tfidf_vectorizer = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
    tfidf_vectorizer.fit(df)
    args = (a, tfidf_vectorizer)
    #df = pd.concat(pool.starmap(func=tfidf_func, iterable=zip(a, repeat(tfidf_vectorizer))))
    df = sp.vstack(pool.starmap(func=tfidf_func, iterable=zip(a, repeat(tfidf_vectorizer))), format='csr')
    pool.close()
    pool.join()
    return df