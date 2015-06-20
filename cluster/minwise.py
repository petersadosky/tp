"""
Input restaurants.csv from clean folder. Use minwise hashing procedure to 
assign restaurants to clusters based on similarity measures.

I made this clustering algorithm prior to this class with support from
my advisor, Rebecca Steorts in the stats department.
It's a combination of minwise hashing and k-means locality sensitive hashing.

I learned some of it from this book: 
http://infolab.stanford.edu/~ullman/mmds/book.pdf

It doesn't have this approach but similar approaches.

Minwise hashing works by inputting records, shingling them, constructing
a binary characteristic matrix, reducing to a signature matrix, and
binning to clusters. We permute the characteristic matrix p times to 
generate projections for the signature matrix.

I wrote k-means here, all based on pseudocode from the link in the kmeans
function below.
"""

import pandas as pd
import numpy as np
import random
import re
import math
import scipy.stats

def main(inputs, db):
    #records = pd.read_csv('../clean/restaurants.csv')
    records = db
    records = records.drop(['ID', 'Zip', 'Latitude', 'Longitude'], axis=1)
    sack = bagOfWords(records)
    words = sack[0]
    weights = sack[1]
    idf = calcIDF(words)
    numProj = 30
    projections = bagSignatures(weights, numProj, idf)
    preduce = reduced(projections)
    numClusters = 50
    centers = kmeans(preduce, numClusters)
    clusters = label(preduce, centers)
    recommendation = recommend(records, clusters, inputs)
    return recommendation

def makeDict(a):
    results = dict()
    for element in a:
        if element in results:
            results[element] += 1
        else:
            results[element] = 1
    return results

def bagOfWords(records):
    # Convert a record into a bag of words
    results = []
    words = []
    for row, record in records.iterrows():
        record = re.sub('\,|\[|\]|\'|"', '', str(record.tolist()))
        record = record.split(' ')
        words.append(record)
        results.append(makeDict(record))
    return [words, results]

def flatten(a):
    # take a 2d list and make it a 1d list
    return [element for sub in a for element in sub]

def calcIDF(split):
    # idf is inverse document frequency
    idfs = dict()
    for sublist in split:
        for element in sublist:
            if element in idfs:
                idfs[element] += 1
            else:
                idfs[element] = 1 
    for element in idfs:
        # IDF of word w = log((total number of documents)/(1+number of documents
        # containing w))
        idfs[element] = (math.log(len(set(flatten(split)))) / 
                         (1 + math.log(idfs[element])) 
                        )
    return pd.DataFrame.from_dict(idfs, orient='index')

def match(a, b):
    #http://stackoverflow.com/questions/4110059/pythonor-numpy-equivalent-of-
    #match-in-r
    return [b.index(element) if element in b else None for element in a]

def rproject(sack, idf):
    # the stanford book has a good rundown of this part
    nbags = len(sack)
    nwords = len(idf)
    wordNames = list(idf.index)
    # draw from normal distribution
    rgaussian = np.random.normal(0, 1, nwords)
    # normalize to get unit-length vector
    rdirection = rgaussian / math.sqrt(sum(rgaussian ** 2))
    def weightedProjection(bag):
        comparisons = match(bag, wordNames) 
        return sum(rdirection[comparisons] * bag.values() * 
                flatten(idf.iloc[comparisons].values.tolist()))
    allProjections = []
    for bag in sack:
        allProjections.append(weightedProjection(bag))
    return allProjections

def bagSignatures(sack, p, idf):
    signatures = []
    for projection in xrange(p):
        signatures.append(rproject(sack, idf))
    return signatures

def kmeans(data, centers):
    # kmeans function/helpers adapted from pseudocode here: 
    # http://stanford.edu/~cpiech/cs221/handouts/kmeans.html
    # kmeans is a clustering algorithm, which takes features and splits into
    # similarity blocks 
    points = random.sample(data, centers)
    clusters = cluster(data, points, centers)
    iterations = 0
    oldClusters = None
    maxIter = 15
    while not shouldStop(oldClusters, clusters, iterations, maxIter):
        oldClusters = clusters
        iterations += 1
        points = newCenters(clusters)
        clusters = cluster(data, points, centers)
    return clusters

def findMin(value, data):
    results = []
    for element in data:
        results += [abs(value - element)]
    return data[results.index(min(results))]

def cluster(data, points, centers):
    clusters = dict()
    for point in points:
        clusters[point] = []
    for element in data:
        clusters[findMin(element, points)] += [element]
    # if not enough clusters reinit them
    if len(clusters) < centers:
        for reinit in xrange(centers - len(clusters)):
            clusters[random.choice(data)] = []
    return clusters

def newCenters(clusters):
    points = []
    for key in clusters:
        points.append(scipy.stats.mstats.gmean(clusters[key]))
    return points

def shouldStop(oldClusters, clusters, iterations, maxIter):
    if iterations > maxIter: return True
    return oldClusters == clusters

def reduced(projections):
    # take the p projections and reduce to single value using
    # geometric mean
    # this uses scipy for geometric mean
    aproj = np.array(projections)
    reductions = []
    for index in xrange(len(projections[0])):
        geomean = scipy.stats.mstats.gmean(aproj[:,index])
        reductions.append(geomean)
    assert(len(reductions) == len(projections[0]))
    return reductions

def label(projections, centers):
    # convert the minhash values to record indices
    labels = dict()
    k = 0
    for key, value in centers.iteritems():
        labels[k] = []
        for element in value:
            labels[k] += [projections.index(element)]
        k += 1
    return labels

def recommend(records, clusters, inputs):
    # Input: restaurant databases, generated clusters, and input restaurants
    # Output: a single restaurant name
    # Use a heuristic to determine which cluster to dive into
    restaurants, ratings = inputs[0], inputs[1]
    table = records['Name']
    restaurantIndices = []
    for restaurant in restaurants:
        restaurantIndices.append(table[table == restaurant].index[0])
    candidateClusters = []
    for key, cluster in clusters.iteritems():
        for index in restaurantIndices:
            if index in cluster:
                candidateClusters.append(key)
    maxRatings = []
    # find the indices of the best rated restaurants among the inputs
    for index, rating in enumerate(ratings):
        if rating == max(ratings):
            maxRatings.append(index)
    selection = maxRatings[random.sample(range(len(maxRatings)), 1)[0]]
    targetRestaurant = restaurants[selection]
    # connect taht index with a restaurant
    targetIndex = table[table == targetRestaurant].index[0]
    targetCluster = None
    for key, cluster in clusters.iteritems():
        if targetIndex in cluster:
            targetCluster = key
    return intraCluster(records, clusters[targetCluster], targetRestaurant) 

def euclideanDist(target, points):
    minimum = None
    minIndex = None
    for index, element in enumerate(points):
        # http://stackoverflow.com/questions/1401712/how-can-the-euclidean-
        # distance-be-calculated-with-numpy
        dist = np.linalg.norm(np.array(target)-np.array(element[1:]))
        if dist != 0 and (minimum == None or dist < minimum):
            minimum = dist
            minIndex = index
    return minIndex

def intraCluster(records, cluster, targetRestaurant):
    # once we've selected a cluster use a euclidean distance formula
    # to find the restaurant most similar
    data = records[['Name', 'ReviewCount', 'Stars', 'Price']]
    subset = data.loc[cluster]
    matrix = map(list, subset.values)
    target = None
    for record in matrix:
        if record[0] == targetRestaurant:
            target = record[1:]
    bestMatch = euclideanDist(target, matrix)
    learnedMatch = learn(bestMatch, subset.iloc[bestMatch]['Name'], 
                         targetRestaurant)
    return learnedMatch


def learn(matchIndex, bestMatch, targetRestaurant):
    # use this to improve recommendations in the future
    # restaurants that have already been chosen won't be selected again
    with open('learning.csv') as f:
        learned = f.readlines()
    cleaned = []
    for ilearn in xrange(len(learned)):
        lea = learned[ilearn].replace('[', '')
        lea = lea.replace('\n', '')
        lea = lea.replace('"', '')
        lea = lea.replace("'", '')
        lea = lea.replace(']', '')
        cleaned.append(lea.split(','))
    for row in xrange(len(cleaned)):
        if cleaned[row][-1] == bestMatch and targetRestaurant in cleaned[row]:
            return intraCluster(records, cluster.remove(matchIndex), 
                                targetRestaurant)
    return bestMatch 



