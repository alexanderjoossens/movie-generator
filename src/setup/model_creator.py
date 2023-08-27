"""
Recomputes the entire model (all similarity data)

**ATTENTION**: Should only be done once on a new installation or 
when something got changed in the recommender's implementation.

The computed simularity data gets exported to "models" for later use.

**WARNING**: These exports can be rather large, depending on the configured number of movies. 
ex. (movie_load_limit=100000, movie_limit=10000) resulted in 1.4GB.
"""

import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.backend.recommender import ContentBasedRecommender

recommender = ContentBasedRecommender(movie_load_limit=700000, movie_limit=600)

recommender.init(recompute=True, export=True)