import pandas as pd
import nltk
import argparse
import os
import sys

import sklearn
import numpy as np
import matplotlib.pyplot as plt

import spacy
from spacy.lang.ro import Romanian
nlp=spacy.load('ro_core_news_sm')

nlp.max_length=10000000 #1644820, default 1000000


y_true=[]
y_pred=[]
totalFiles=0
labels={}

keepBIO=False

def getLabelId(label):
    global labels

    if not keepBIO:
        if label.startswith("B-") or label.startswith("I-"):
            label=label[2:]

    if label in labels: return labels[label]

    labels[label]=len(labels)
    return labels[label]

def processFile(ftxt, fann, fgold):

    global totalFiles, y_true, y_pred
    totalFiles+=1

    print("FILE: ",ftxt)

    annGold=[]

    with open(fgold,"r") as f:
            for line in f :
                data=line.split("\t")
                if len(data)!=3: continue
                data[1]=data[1].split(" ")
                if len(data[1])!=3: continue
                data[1][1]=int(data[1][1])
                data[1][2]=int(data[1][2])

                #print(data)

                annGold.append(data[1])
                #data[2]=data[2].rstrip()

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
                #data[2]=data[2].rstrip()


    with open(ftxt,"r") as f: text1=f.read()
    with open(ftxt,"rb") as f: text=f.read()
    textb=text.decode("utf-8")
    doc = nlp(text1)

    start=0
    tokens=[]
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

    prevPred=""
    prevGold=""
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
            nerPred="O"
        else:
            nerPred=found[0]

        found=False
        for a in annGold:
            #if a[1]<=token['idx'] and token['idx']+len(token['text'])<=a[2]:
            #if a[1]>=token['idx'] and a[1]<=token['idx']+len(token['text']) or a[2]>=token['idx'] and a[2]<=token['idx']+len(token['text']) or a[1]<=token['idx'] and a[2]>=token['idx']:
            if not (a[2]<=token['idx'] or token['idx']+len(token['text'])<=a[1]):
                found=a
                break
        #print(token['text'], found)
        if found==False:
            nerGold="O"
        else:
            nerGold=found[0]

        if nerGold!="O":
            if nerGold==prevGold:
                nerGold="I-"+nerGold
            else:
                prevGold=nerGold
                nerGold="B-"+nerGold
        else:
            prevGold=nerGold

        if nerPred!="O":
            if nerPred==prevPred:
                nerPred="I-"+nerPred
            else:
                prevPred=nerPred
                nerPred="B-"+nerPred
        else:
            prevPred=nerPred

        #print(token['text'],nerGold,nerPred)

        y_true.append(getLabelId(nerGold))
        y_pred.append(getLabelId(nerPred))

parser=argparse.ArgumentParser()
parser.add_argument("-c","--corpus", help="Corpus", required=True, nargs="+")
parser.add_argument("-r","--run", help="Run name", required=True)
args=parser.parse_args()

annFolder="gold_standoff"
filesFolder="files"

for corpus in args.corpus:
    if not os.path.exists(corpus) or not os.path.exists(os.path.join(corpus,args.run)): # or not os.path.exists(os.path.join(corpus,annFolder)):
        print("{} is not a valid corpus".format(corpus))
        #sys.exit(-1)
        continue

    for filename in os.listdir(os.path.join(corpus,args.run)):
        if not filename.endswith(".ann"): continue

        fAnn=os.path.join(corpus,args.run,filename)

        #filename=filename[:-8]+".ann"
        fGold = os.path.join(corpus,annFolder, filename)

        filename=filename[:-4]+".txt"
        fTxt = os.path.join(corpus,"files", filename)

        if os.path.isfile(fAnn) and os.path.isfile(fGold) and os.path.isfile(fTxt):
            processFile(fTxt,fAnn,fGold)


print("Total files:",totalFiles)
print(labels)
cr=sklearn.metrics.classification_report(y_true, y_pred, target_names=labels.keys(), output_dict=False, zero_division=np.nan)
print(cr)
cm = sklearn.metrics.confusion_matrix(y_true, y_pred)

cmd={}
cmlabels=list(labels.keys())
for i in range(len(labels)):
    cmd[cmlabels[i]]=cm[i]
    
cm1=pd.DataFrame.from_dict(cmd, orient='index', columns=cmlabels)

base_out="{}_{}".format(os.path.basename(os.path.normpath(args.corpus[0])),args.run)
with open(base_out+".txt","w") as fout: fout.write("Classification Report\n\n{}\n\nConfusion Matrix\n\n{}\n".format(cr,cm1))
#with open(base_out+".txt","w") as fout: fout.write("Classification Report\n\n{}\n\nConfusion Matrix\n\n{}\n".format(cr,np.array2string(cm1, max_line_width=300)))

disp = sklearn.metrics.ConfusionMatrixDisplay(confusion_matrix=cm) #, display_labels=clf.classes_)
#disp.plot()
px = 1/plt.rcParams['figure.dpi']
fig,ax = plt.subplots(figsize=(1400*px,1400*px))
#plt.matshow(cm)
disp.plot(ax=ax)
#plt.title('Confusion Matrix {}'.format(args.run))
#plt.colorbar()
#plt.ylabel('True Label')
#plt.xlabel('Predicted Label')
plt.savefig(base_out+'.jpg')

