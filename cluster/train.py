"""
Create a training set from which to test the results of minhashing for
recommending restaurants
"""

import pandas as pd
import csv

def main():
    data = pd.read_csv('../clean/restaurants.csv')
    #df = pd.DataFrame(index=data['Name'], columns=data['Name']).fillna(0)
    matrix = make2dList(len(data['Name']), len(data['Name']))
    for record1 in xrange(len(data)):
        for record2 in xrange(len(data)):
            if (data['Price'][record1] == data['Price'][record2] and 
                data['Stars'][record1] == data['Stars'][record2]):
                matrix[record1][record2] = 1
            elif data['Stars'][record1] == data['Stars'][record2]:
                matrix[record1][record2] = 0.66
            elif data['Price'][record1] == data['Price'][record2]:
                matrix[record1][record2] = 0.33
    writeToFile(matrix)


def make2dList(rows, cols):
    # from lecture
    a=[]
    for row in xrange(rows): a += [[0]*cols]
    return a

def writeToFile(l):
    with open('train.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(l)


if __name__ == '__main__':
    main()
