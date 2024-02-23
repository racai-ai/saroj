import pandas as pd
import nltk
import argparse
import os
import sys

import sklearn

from spacy.lang.ro import Romanian
nlp = Romanian()
tokenizer = nlp.tokenizer


def processFile(ftxt, fann):
    #print(ftxt, fann)
    with open(ftxt,"rb") as f: text=f.read()
    with open(ftxt,"r") as f: text1=f.read()
    doc = nlp(text1)
    start=0
    tokens=[]
    #textb=text #bytes(text,encoding="utf-8")
    textb=text.decode("utf-8")
    for token in doc:
        #print(token.text, token.i, token.idx)

        t=token.text.strip()
        if len(t)==0: continue
        #t=bytes(t,encoding="utf-8")
        pos=textb.find(t,start)
        if pos!=-1:
            tokens.append({"text":t,"idx":pos})
            #print(t,pos)
            start=pos+len(t)

    #sys.exit(-1)

    ann=[]

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

    ret=[]

    for token in tokens:
        found=False
        for a in ann:
            if a[1]<=token['idx'] and token['idx']+len(token['text'])<=a[2]:
                found=a
                break
        #print(token['text'], found)
        if found==False:
            ret.append("O")
        else:
            ret.append(found[0])

    return ret

parser=argparse.ArgumentParser()
parser.add_argument("--corpus1", help="Corpus 1", required=True)
parser.add_argument("--corpus2", help="Corpus 2", required=True)
args=parser.parse_args()

annFolder="gold_standoff"
filesFolder="files"

if not os.path.exists(args.corpus1) or not os.path.exists(os.path.join(args.corpus1,filesFolder)) or not os.path.exists(os.path.join(args.corpus1,annFolder)):
    #print("{} is not a valid corpus".format(args.corpus1))
    sys.exit(-1)

if not os.path.exists(args.corpus2) or not os.path.exists(os.path.join(args.corpus2,filesFolder)) or not os.path.exists(os.path.join(args.corpus2,annFolder)):
    #print("{} is not a valid corpus".format(args.corpus2))
    sys.exit(-1)

commonFiles=0
y1=[]
y2=[]
for filename in os.listdir(os.path.join(args.corpus1,annFolder)):
    if not filename.endswith(".ann"): continue

    fann1 = os.path.join(args.corpus1,annFolder, filename)
    fann2 = os.path.join(args.corpus2,annFolder, filename)
    
    filename=filename[:-4]+".txt"
    ftxt1 = os.path.join(args.corpus1,filesFolder, filename)
    ftxt2 = os.path.join(args.corpus2,filesFolder, filename)

    if os.path.isfile(fann1) and os.path.isfile(fann2) and os.path.isfile(ftxt1) and os.path.isfile(ftxt2):
        commonFiles+=1
        f1=processFile(ftxt1,fann1)
        f2=processFile(ftxt1,fann2)

        y1+=f1
        y2+=f2

#print("Common files: {}".format(commonFiles))
#print("Annotations: {} - {}".format(len(y1),len(y2)))

if len(y1)>0:
    k=sklearn.metrics.cohen_kappa_score(y1,y2)

    print("{}\t{}\t{}\t{}\t{}".format(
	os.path.basename(os.path.normpath(args.corpus1)),
        os.path.basename(os.path.normpath(args.corpus2)),
	commonFiles,
        len(y1),
        round(k,2)))

