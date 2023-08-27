import numpy as np
import pandas as pd


# Given a list of ratings, remove all negative ones and return the rest
def filter_dislikes(lst, array):
    result = []
    for i, xs in enumerate(lst):
        rating = array[i]
        if rating != -1:
            result.append(xs)
    return result

# Visual 1
def vis1(avguser1, avguser2):
    # step 1: concat two dataframes
    frames = [avguser1, avguser2]
    result = pd.concat(frames, axis=1)
    # step 2: calculate average
    result = result.mean(axis=1)

    # Restructure the output
    result = pd.DataFrame(result)
    result = result.rename(columns={0: "percentage"})
    result.index.name = "index"

    return result

# Visual 2
def vis2(array, df):

    df = df.copy()
    toDrop = []
    ratings = []
    # step 1: remove input movies that had dislike
    #print(array)
    for i, rating in enumerate(array):
        if rating < 0:
            rating = -rating
            df.iloc[:,i] = 100 - df.iloc[:,i] 
        ratings.append(rating)
    
    ratings = np.array(ratings)
    
    df = df.drop(df.columns[toDrop],axis = 1)
    df = df.reset_index()
    #df = df.drop("index",axis=1)

    #print(df)
    

    for i in range(df.index[-1]+1):
        a= df.iloc[i,1:]
        df.iloc[i,1:] = np.average(a=a, weights=ratings)
    df = df.set_index("index")

    #print(df)
    
    # step 2: calculate average
    df = df.mean(axis=1)

    #print(df)

    # Restructure the output
    vis2 = pd.DataFrame(df)
    vis2 = vis2.rename(columns={0: "percentage"})
    vis2.index.name = "index"

    #print(vis2)
        
    return vis2

# Visual 3
def vis3(string, index_ouput_movie, index_input_movies, array1, array2, data_processed):
    # 1: find genres of output movie
    list_ouput_movie = data_processed.at[index_ouput_movie, string]

    # 2: remove input movies that had dislike
    #df1 = filter_dislikes(index_input_movies, array1)
    #df2 = filter_dislikes(index_input_movies, array2)
    
    df1 = index_input_movies
    df2 = index_input_movies

    #print(data_processed)

    # 3: find genres of input movies
    genre_dict_1 = {}
    for i, xs in enumerate(df1):
        temp = data_processed.at[xs, string]
        for genre in temp:
            genre_dict_1[genre] = genre_dict_1.get(genre, 0) + array1[i]
        #lst1_input_movie.extend(temp)
    
    #lst2_input_movie = []
    genre_dict_2 = {}
    for i, xs in enumerate(df2):
        temp = data_processed.at[xs, string]
        for genre in temp:
            genre_dict_2[genre] = genre_dict_2.get(genre, 0) + array2[i]
        #lst2_input_movie.extend(temp)
    
    
    # make dataframe
    df = pd.DataFrame(list_ouput_movie, columns=[string])
    df["User1"] = ""
    df["User2"] = ""
    

    for i, xs in enumerate(list_ouput_movie):
        #if xs in lst1_input_movie:
        df.at[i, 'User1'] = max(genre_dict_1.get(xs, 0), 0)
            
    for i, xs in enumerate(list_ouput_movie):
        
        #if xs in lst2_input_movie:
        df.at[i, 'User2'] = max(genre_dict_2.get(xs, 0), 0)
    
    df['Total'] = df['User1'] + df['User2']
    df['Total'] = np.array([max(i,1) for i in df['Total']])
    df['User1_per'] = df['User1'] / df['Total']
    #df.loc[np.isinf(df['User1_per']), 'User1_per'] = 0
    df['User2_per'] = df['User2'] / df['Total']
    #df.loc[np.isinf(df['User2_per']), 'User2_per'] = 0
    df = df.round(2)

    
    return df

# Visual 4
def vis4(index_ouput_movie, index_input_movies, array1, array2, data_processed):
    # 1: find keywords of output movie
    list_ouput_movie = data_processed.at[index_ouput_movie, "keywords"]
    
    # 2: remove input movies that had dislike
    df1 = filter_dislikes(index_input_movies, array1)
    df2 = filter_dislikes(index_input_movies, array2)
    
    # 3: find keywords of input movies
    lst1_input_movie = []
    for i, xs in enumerate(df1):
        temp = data_processed.at[xs, "keywords"]
        lst1_input_movie.extend(temp)
    
    lst2_input_movie = []
    for i, xs in enumerate(df2):
        temp = data_processed.at[xs, "keywords"]
        lst2_input_movie.extend(temp)

    # 4: intersect keywords of input & output movies
    lst1 = [value for value in list_ouput_movie if value in lst1_input_movie]
    lst2 = [value for value in list_ouput_movie if value in lst2_input_movie]
       
    # 5: 0 = both like / 1 = user1 only likes it / 2 = user2 only likes it
    all_keywords = list(set(lst1) | set(lst2))
    result1 = []
    result2 = []
    result0 = []
    for kw in all_keywords:
        if (kw in lst1) & (kw in lst2):
            result0.append(kw)
        elif (kw in lst1):
            result1.append(kw)
        else:
            result2.append(kw)
    
    return [result0, result1, result2]

