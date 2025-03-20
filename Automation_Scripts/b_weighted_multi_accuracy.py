 #Need NUM_CHOICES and NUM_EXPERT may be create a class(??).

from os import listdir
import pandas as pd
from sklearn.ensemble import VotingClassifier
from pickle import load
from sklearn.metrics import accuracy_score
import statistics
import shutil
import os
import csv
from multiprocessing import Process
from time import sleep
import numpy as np
class Predictor:
    def __init__(self,filepath,target,NUM_EXPERT):
        self.MODELS = []
        self.WEIGHT = []
        self.TEST_DATA= pd.read_csv("./test.csv")
        self.TEST_DATA_LABLES = self.TEST_DATA.pop(target)
        self.NUM_EXPERT = NUM_EXPERT
        for x in listdir(filepath+"/models"):

            if(x[0]=="e"):#Loding the models starting with e
                with open(filepath+"/models/"+x,"rb") as f:
                    self.MODELS.append(load(f))
            elif(x[0]=="w"):#loading the weights
                with open(filepath+"/models/"+x,"rb") as f:
                   self.WEIGHT = (load(f))
        self.ACCURACY_WEIGHT = []
        #Just Taking the Accuracy Weights
        temp = self.WEIGHT["ACCURACY"]
       
        for x in range(0,len(temp)):
            self.ACCURACY_WEIGHT.append(temp[x])
        t = sum(self.ACCURACY_WEIGHT)
        self.ACCURACY_WEIGHT = [x/t for x in self.ACCURACY_WEIGHT]
        self.ACCURACY_WEIGHT = np.array(self.ACCURACY_WEIGHT)
        
        #Just Taking the TREEMA Weights
        self.TREEMA_WEIGHT = []
        temp = self.WEIGHT["TREEMA"]
        
        for x in range(0,len(temp)):
            self.TREEMA_WEIGHT.append(temp[x])
        t = sum(self.TREEMA_WEIGHT)
        self.TREEMA_WEIGHT = [x/t for x in self.TREEMA_WEIGHT]
        self.TREEMA_WEIGHT = np.array(self.TREEMA_WEIGHT)
        

    def predict_custom(self,voting = "hard",init = False):
        #This is classical Ensemble Learning where you should use the 
        #ACCURACY BASED STUFF
        
        if(voting == "hard"):
            pred = []
            final_pred = []
            temp = []
            for i,x in enumerate(self.MODELS):#Poulating the Predictions
                pred.append(x.predict(self.TEST_DATA))
            pred = np.array(pred)
            pred = np.transpose(pred)
            unique = [0,1,2,3,4,5,6,7,8,9]
            final_pred = []
            for i in range(pred.shape[0]):
                weighted_votes = np.zeros(10)#Just Initialzing it to zero
                for j,p in enumerate(unique):
                    weighted_votes[j] = np.sum(self.ACCURACY_WEIGHT[ pred[i] == p])
                final_pred.append(unique[np.argmax(weighted_votes)])
                
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            return(t)

        if(voting == "soft"):
            pred= {}
            DATA_FRAMES = []
            for i,x in enumerate(self.MODELS):
                pred[i] = x.predict_proba(self.TEST_DATA)
            final_result = 0
            for i,x in enumerate(pred):
                d = pd.DataFrame(pred[x])
                d = d*self.ACCURACY_WEIGHT[i]
                if(i == 0):
                    final_result = pd.DataFrame(0,index = d.index,columns=d.columns)
                final_result = final_result+d         
            
            final_pred = final_result.idxmax(axis=1).to_list()
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            return(t)

    def predict_treema(self,voting = "hard",init = False):
        
        unique = [0,1,2,3,4,5,6,7,8,9]
        final_pred = []
        pred = []

        if(voting == "hard"):
            temp = []
            for i,x in enumerate(self.MODELS):#Poulating the Predictions
                pred.append(x.predict(self.TEST_DATA))
            pred = np.array(pred)
            pred = np.transpose(pred)
            for i in range(pred.shape[0]):
                weighted_votes = np.zeros(10)#Just Initialzing it to zero
                for j,p in enumerate(unique):
                    weighted_votes[j] = np.sum(self.TREEMA_WEIGHT[ pred[i] == p])
                final_pred.append(unique[np.argmax(weighted_votes)])
                
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            return(t)

        if(voting == "soft"):
            pred= {}
            DATA_FRAMES = []
            for i,x in enumerate(self.MODELS):
                pred[i] = x.predict_proba(self.TEST_DATA)
            final_result = 0
            for i,x in enumerate(pred):
                d = pd.DataFrame(pred[x])
                d = d*self.TREEMA_WEIGHT[i]
                if(i == 0):
                    final_result = pd.DataFrame(0,index = d.index,columns=d.columns)
                final_result = final_result+d         
            
            final_pred = final_result.idxmax(axis=1).to_list()
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            return(t)
            

def dir_iter(filepath,PROTOCOL,NUM_EXPERT,NUM_ROUNDS,NUMBER):

    fp = ""
    t = 0
    count = 0
    TREEMA = {"soft":[],"hard":[]}
    CUSTOM = {"soft":[],"hard":[]}
    for x in listdir(filepath):
        fp = filepath+"/"+x
        print("\tProcessing:",fp,"CURRENT:",count,"To Do:",10-count)
        c = Predictor(fp,"lable",NUM_EXPERT)
        t = c.predict_custom(voting="soft")
        
        t = c.predict_treema(voting="hard")
        TREEMA["hard"].append(t)
        t = c.predict_treema(voting="soft")
        TREEMA["soft"].append(t)
        t = c.predict_custom(voting="soft")
        CUSTOM["soft"].append(t)
        t = c.predict_custom(voting="hard")
        CUSTOM["hard"].append(t)
        count+=1


    result = []
    for i in TREEMA:
        a = ["TREEMA",PROTOCOL,i,NUM_EXPERT,NUM_ROUNDS,sum(TREEMA[i])/(count),statistics.stdev(TREEMA[i])]
        b = ["BASE",PROTOCOL,i,NUM_EXPERT,NUM_ROUNDS,sum(CUSTOM[i])/(count),statistics.stdev(CUSTOM[i])]
        result.append(a)
        result.append(b)

    with open("./accuracy/"+str(NUMBER)+".csv","w") as f:
        w = csv.writer(f)
        for x in result:
            w.writerow(x)
    #CSV WRITING HERER

def parser(name):
    a,b,c = name.split(";")
    PROTOCOL = a
    MAX_ROUND=int(b.split("=")[-1])
    NUM_ROUND = int(c.split("=")[-1])
    return PROTOCOL,NUM_ROUND,MAX_ROUND
#platform,protocol,num_expert,num_rounds,mean_test_acc,std_test_acc

shutil.rmtree('./accuracy', ignore_errors=True)
os.mkdir("./accuracy")
count = 0
baser={}
PROCESS = []
for z in os.listdir("../results"):#Carefull  used .  instead of ..
    PATH = "../results/"+z ##Carefull  used .  instead of ..
    PROTOCOL,NUM_EXPERT,NUM_ROUNDS = parser(z)
    baser[count]=(PATH,PROTOCOL,NUM_EXPERT,NUM_ROUNDS,count)
    process0= Process(target=dir_iter,args=baser[count])
    process0.start()
    PROCESS.append(process0)
    count+=1
for x in PROCESS:
    x.join()

import glob
import pandas as pd
df_files = []
for z in glob.glob("./accuracy/*.csv"):
    print(z)
    temp = pd.read_csv(z,names=["platform","protocol","voting","num_expert","num_rounds","mean_test_acc","std_test_acc"])
    df_files.append(temp)
final_df = pd.concat(df_files)
final_df.to_csv("ACCURACY.csv")


print("\n\nAll the Processing DONE")





