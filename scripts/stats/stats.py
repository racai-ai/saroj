import pandas as pd
import nltk
import argparse
import os
import sys

import sklearn

import spacy
from spacy.lang.ro import Romanian
nlp=spacy.load('ro_core_news_sm')

nlp.max_length=10000000 #1644820, default 1000000

totalFiles=0
uniqueFiles={}
totalTokens=0
uniqueTokens={}
uniqueTokensLower={}
entities={}
entitiesTokens={}
uniqueEntities={}
totalSent=0
uniqueSent={}
totalAnnotatedFiles=0
totalUniqueAnnotatedFiles=0

def processFile(ftxt, fann):

    global totalFiles, uniqueFiles, totalTokens, uniqueTokens, uniqueTokensLower, entities, entitiesTokens, uniqueEntities, totalSent, uniqueSent, totalAnnotatedFiles, totalUniqueAnnotatedFiles
    totalFiles+=1

    if os.path.isfile(fann):
        totalAnnotatedFiles+=1

    fname=os.path.basename(fann)
    if fname in uniqueFiles: return []
    uniqueFiles[fname]=True

    #print(ftxt, fann)
    with open(ftxt,"rb") as f: text=f.read()
    with open(ftxt,"r") as f: text1=f.read()
    doc = nlp(text1)
    start=0
    tokens=[]
    #textb=text #bytes(text,encoding="utf-8")
    textb=text.decode("utf-8")

    totalSent+=len(list(doc.sents))
    for sent in doc.sents:
        uniqueSent[" ".join([t.text for t in sent])]=True

    for token in doc:
        #print(token.text, token.i, token.idx)

        t=token.text.strip()
        if len(t)==0: continue

        totalTokens+=1
        uniqueTokens[token.text]=True
        uniqueTokensLower[token.text.lower()]=True

        #t=bytes(t,encoding="utf-8")
        pos=textb.find(t,start)
        if pos!=-1:
            tokens.append({"text":t,"idx":pos})
            #print(t,pos)
            start=pos+len(t)

    #sys.exit(-1)

    ann=[]

    if os.path.isfile(fann):
        totalUniqueAnnotatedFiles+=1
        with open(fann,"r") as f:
            for line in f :
                data=line.split("\t")
                if len(data)!=3: continue
                data[1]=data[1].split(" ")
                if len(data[1])!=3: continue
                data[1][1]=int(data[1][1])
                data[1][2]=int(data[1][2])

                #print(data)

                ann.append(data[1])
                data[2]=data[2].rstrip()

                if data[1][0] not in entities: entities[data[1][0]]=0
                entities[data[1][0]]+=1

                uniqueEntities[data[1][0]+"_"+data[2]]=True

    ret=[]

    for token in tokens:
        found=False
        for a in ann:
            #if a[1]<=token['idx'] and token['idx']+len(token['text'])<=a[2]:
            #if a[1]>=token['idx'] and a[1]<=token['idx']+len(token['text']) or a[2]>=token['idx'] and a[2]<=token['idx']+len(token['text']) or a[1]<=token['idx'] and a[2]>=token['idx']:
            if not (a[2]<=token['idx'] or token['idx']+len(token['text'])<=a[1]):
                found=a
                break
        #print(token['text'], found)
        if found==False:
            ret.append("O")
        else:
            ret.append(found[0])
            if found[0] not in entitiesTokens: entitiesTokens[found[0]]=0
            entitiesTokens[found[0]]+=1

    return ret

parser=argparse.ArgumentParser()
parser.add_argument("-c","--corpus", help="Corpus", required=True, nargs="+")
args=parser.parse_args()

annFolder="gold_standoff"
filesFolder="files"

for corpus in args.corpus:
    if not os.path.exists(corpus) or not os.path.exists(os.path.join(corpus,filesFolder)): # or not os.path.exists(os.path.join(corpus,annFolder)):
        print("{} is not a valid corpus".format(corpus))
        #sys.exit(-1)
        continue

    for filename in os.listdir(os.path.join(corpus,filesFolder)):
        if not filename.endswith(".txt"): continue

        filename=filename[:-4]+".ann"
        fann1 = os.path.join(corpus,annFolder, filename)
        filename=filename[:-4]+".txt"
        ftxt1 = os.path.join(corpus,filesFolder, filename)

        #if os.path.isfile(fann1) and os.path.isfile(ftxt1):
        processFile(ftxt1,fann1)


print("Total TXT files={}".format(totalFiles))
print("Unique TXT files={}".format(len(uniqueFiles)))
print("Total ANN files={}".format(totalAnnotatedFiles))
print("Unique ANN files={}".format(totalUniqueAnnotatedFiles))
print("")
print("In unique files:")
print("Total tokens={}".format(totalTokens))
print("Unique tokens={}".format(len(uniqueTokens)))
print("Unique tokens lowercase={}".format(len(uniqueTokensLower)))
print("Total sentences={}".format(totalSent))
print("Unique sentences={}".format(len(uniqueSent)))
print("Unique entities={}".format(len(uniqueEntities)))
print("Entities:")
totalEntities=0
sdict=dict(sorted(entities.items()))
for k in sdict.keys():
    print("{}\t{}".format(k,sdict[k]))
    totalEntities+=sdict[k]
print("Total Entities: {}".format(totalEntities))

print("")
print("Entities tokens:")
totalEntities=0
sdict=dict(sorted(entitiesTokens.items()))
for k in sdict.keys():
    print("{}\t{}".format(k,sdict[k]))
    totalEntities+=sdict[k]
print("Total Entities tokens: {}".format(totalEntities))

