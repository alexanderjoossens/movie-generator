"""
A collection of functions for combining the recommendation results of two people.
"""

import pandas as pd


# input: (1) array list with rating user gave to the input movies 
#        (2) dataframe met similarities
# output: 1 list for all movies a score including the ratings of the user
def get_one_list(array, df):
    # test toevoegen lengtes!!!
    df = df.copy()
    for index, column in enumerate(df):
        rating = array[index]
        df[column] = df[column]*rating
    print("get_one_list")
    print(df)
        
    return df.sum(1)

# input: rating list of both users
# output: combined group recommendation list using technique = Multiplicative 
def groep_rec_mult(user1, user2):
    df = pd.DataFrame({  'User1': user1,
                       'User2' : user2})

    df['total_score'] = df['User1'] * df['User2']
    return df['total_score']  

# input: rating list of both users
# output: combined group recommendation list using technique = Least Misery
def groep_rec_least(user1, user2):
    df = pd.DataFrame({  'User1': user1,
                       'User2' : user2})

    df['total_score'] = df[['User1','User2']].min(axis=1)
    return df['total_score'] 

# input: combined group recommendation list
# output: top 15 movies
def filter_top_15(group_lst):
    return group_lst.nlargest(15, "total_score")

# input: combined group recommendation list
# output: top 15 movies
def filter_top_15_index_list(group_lst):
    result = group_lst.nlargest(15)
    result = result.reset_index()
    return result["index"].tolist()
