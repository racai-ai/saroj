import pandas as pd
import nltk
import argparse
import os
import sys

import sklearn

import spacy
from spacy.lang.ro import Romanian
nlp=spacy.load('ro_core_news_sm')

entities=[]

def processFile(ftxt, fann):

    global entities

    fname=os.path.basename(fann)

    if os.path.isfile(fann):
        with open(fann,"r") as f:
            for line in f :
                data=line.split("\t")
                if len(data)!=3: continue
                data[1]=data[1].split(" ")
                if len(data[1])!=3: continue
                data[1][1]=int(data[1][1])
                data[1][2]=int(data[1][2])

                entities.append("{}\t{}\t{}".format(data[2].rstrip(),data[1][0],fname))

    return []

parser=argparse.ArgumentParser()
parser.add_argument("-c","--corpus", help="Corpus", required=True, nargs="+")
args=parser.parse_args()

annFolder="gold_standoff"
filesFolder="files"

for corpus in args.corpus:
    if not os.path.exists(corpus) or not os.path.exists(os.path.join(corpus,filesFolder)) or not os.path.exists(os.path.join(corpus,annFolder)):
        print("{} is not a valid corpus".format(corpus))
        #sys.exit(-1)
        continue

    for filename in os.listdir(os.path.join(corpus,filesFolder)):
        if not filename.endswith(".txt"): continue

        filename=filename[:-4]+".ann"
        fann1 = os.path.join(corpus,annFolder, filename)
        filename=filename[:-4]+".txt"
        ftxt1 = os.path.join(corpus,filesFolder, filename)

        if os.path.isfile(fann1) and os.path.isfile(ftxt1):
            processFile(ftxt1,fann1)


for ent in sorted(entities):
    print("{}".format(ent))

