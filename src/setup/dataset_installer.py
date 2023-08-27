import os
import opendatasets as od

# You need to create an account on Kaggle and get a key for this
od.download("https://www.kaggle.com/datasets/akshaypawar7/millions-of-movies", data_dir=os.path.join("..", "..", "dataset"))