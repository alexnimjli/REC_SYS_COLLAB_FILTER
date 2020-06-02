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
itemName_column = 'original_title'


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
merged_data = result[['user_id', 'book_id', 'original_title', 'rating']]
# -

testUser = 78
k = 10

# ### looks like user 78 could be me! 

merged_data[merged_data['user_id'] == testUser].sort_values(by=['rating'], ascending =False)[:40]

# Load our data set and compute the user similarity matrix
ml = DataLoader(items_path, ratings_path, userID_column, itemID_column, ratings_column, itemName_column, size_of_data)
data = ml.loadData()

trainSet = data.build_full_trainset()

sim_options = {'name': 'cosine',
               'user_based': True
               }

model = KNNBasic(sim_options=sim_options)
model.fit(trainSet)
simsMatrix = model.compute_similarities()

simsMatrix.shape

# Get top N similar users to our test subject
# (Alternate approach would be to select users up to some similarity threshold - try it!)
testUserInnerID = trainSet.to_inner_uid(testUser)
similarityRow = simsMatrix[testUserInnerID]

# removing the testUser from the similarityRow
similarUsers = []
for innerID, score in enumerate(similarityRow):
    if (innerID != testUserInnerID):
        similarUsers.append( (innerID, score) )

# find the k users largest similarities
kNeighbors = heapq.nlargest(k, similarUsers, key=lambda t: t[1])

# +
# Get the stuff the k users rated, and add up ratings for each item, weighted by user similarity

# candidates will hold all possible items(movies) and combined rating from all k users
candidates = defaultdict(float)
for similarUser in kNeighbors:
    innerID = similarUser[0]
    userSimilarityScore = similarUser[1]
    # this will hold all the items they've rated and the ratings for each of those items
    theirRatings = trainSet.ur[innerID]
    for rating in theirRatings:
        candidates[rating[0]] += (rating[1] / 5.0) * userSimilarityScore
# -

# Build a dictionary of stuff the user has already seen
watched = {}
for itemID, rating in trainSet.ur[testUserInnerID]:
    watched[itemID] = 1

# Get top-rated items from similar users:
pos = 0
for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
    if itemID not in watched:
        movieID = trainSet.to_raw_iid(itemID)
        print(ml.getItemName(int(movieID)), ratingSum)
        pos += 1
        if (pos > 8):
            break


