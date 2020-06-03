# -*- coding: utf-8 -*-
from DataLoader import DataLoader
from surprise import KNNBasic
import heapq
from collections import defaultdict
from operator import itemgetter
import pandas as pd

# +
items_path = '../data/goodbooks-10k-master/books.csv'
ratings_path = '../data/goodbooks-10k-master/ratings.csv'
itemID_column = 'book_id'
userID_column = 'user_id'
ratings_column = 'rating'
itemName_column = 'title'

# please check how large your ratings.csv is, the larger it is the longer it'll take to run!
# 5 million entries is far too much!
size_of_data = 100000

# +
ratings = pd.read_csv(ratings_path)
print('shape of original ratings was: ', ratings.shape)
ratings = ratings[:size_of_data]
print('shape of ratings is now: ', ratings.shape)
items = pd.read_csv(items_path)

result = pd.merge(ratings, items, how='left', on=['book_id'])
merged_data = result[['user_id', 'book_id', 'title', 'rating']]
# -

testUser = 78
k = 10

merged_data[merged_data['user_id'] == testUser].sort_values(by=['rating'], ascending =False)[:40]

ml = DataLoader(items_path, ratings_path, userID_column, itemID_column, ratings_column, itemName_column, size_of_data)
data = ml.loadData()

trainSet = data.build_full_trainset()

sim_options = {'name': 'cosine',
               'user_based': False
               }

model = KNNBasic(sim_options=sim_options)
model.fit(trainSet)
simsMatrix = model.compute_similarities()

simsMatrix.shape

testUserInnerID = trainSet.to_inner_uid(testUser)

# Get the top K items we rated
testUserRatings = trainSet.ur[testUserInnerID]
kNeighbors = heapq.nlargest(k, testUserRatings, key=lambda t: t[1])

# Get similar items to stuff we liked (weighted by rating)
candidates = defaultdict(float)
for itemID, rating in kNeighbors:
    similarityRow = simsMatrix[itemID]
    for innerID, score in enumerate(similarityRow):
        candidates[innerID] += score * (rating / 5.0)

len(trainSet.ur[testUserInnerID]), len(candidates)

# Build a dictionary of stuff the user has already seen
watched = {}
for itemID, rating in trainSet.ur[testUserInnerID]:
    watched[itemID] = 1

# Get top-rated items from similar users:
pos = 0
for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
    if not itemID in watched:
        movieID = trainSet.to_raw_iid(itemID)
        print(ml.getItemName(int(movieID)), ratingSum)
        pos += 1
        if (pos > 10):
            break

# # select a single item and find items similar to that
#
# here I'm loading a new user with ratings for selected books

# +
k=10
testItemID = 485
mockUserID = 0
max_rating = ratings['rating'].max()

selected_items = [485, 592, 1041, 479, 95, 4106]
selected_ratings = []
#can manually input the ratings per item 
#selected_ratings = [5, 5, 5, 5, 5, 4]

# +
# this code will build new dataframe with the new items and ratings
# the default user will be 0

new_rows = {userID_column:[], itemID_column:[], ratings_column:[]}
if selected_ratings or len(selected_ratings) != 0:
    for num, values in enumerate(zip(selected_items, selected_ratings)):
        new_rows[userID_column].append(mockUserID)
        new_rows[itemID_column].append(values[0])
        new_rows[ratings_column].append(values[1])
else:
    for values in enumerate(selected_items):
        new_rows[userID_column].append(mockUserID)
        new_rows[itemID_column].append(values[1])
        new_rows[ratings_column].append(max_rating)

new_rows = pd.DataFrame(new_rows)
# -

ml = DataLoader(items_path, ratings_path, userID_column, itemID_column, ratings_column, itemName_column, size_of_data)
data = ml.addUserLoadData(new_rows)

trainSet = data.build_full_trainset()

sim_options = {'name': 'cosine',
               'user_based': False
               }

model = KNNBasic(sim_options=sim_options)
model.fit(trainSet)
simsMatrix = model.compute_similarities()

simsMatrix.shape

testUserInnerID = trainSet.to_inner_uid(mockUserID)

# Get the top K items we rated
testUserRatings = trainSet.ur[testUserInnerID]
kNeighbors = heapq.nlargest(k, testUserRatings, key=lambda t: t[1])

# Get similar items to stuff we liked (weighted by rating)
candidates = defaultdict(float)
for itemID, rating in kNeighbors:
    similarityRow = simsMatrix[itemID]
    for innerID, score in enumerate(similarityRow):
        candidates[innerID] += score * (rating / 5.0)

len(trainSet.ur[testUserInnerID]), len(candidates)

# Build a dictionary of stuff the user has already seen
watched = {}
for itemID, rating in trainSet.ur[testUserInnerID]:
    watched[itemID] = 1

# Get top-rated items from similar users:
pos = 0
for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
    if not itemID in watched:
        movieID = trainSet.to_raw_iid(itemID)
        print(ml.getItemName(int(movieID)), ratingSum)
        pos += 1
        if (pos > 10):
            break




