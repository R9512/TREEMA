 #Need NUM_CHOICES and NUM_EXPERT may be create a class(??).
"""
    - Goal is to introduce the malicious nodes
    - Write a function that does the following:
        - If you give it a parameter k , it will MOST reputable k models and infect them
                - Infect: Basically Change the predictions of the model. 
"""
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
from random import randint as rand
class Predictor:
    def __init__(self,filepath,target,malicous):
        self.MODELS = []
        self.WEIGHT = []
        self.TEST_DATA= pd.read_csv("./test.csv")
        self.TEST_DATA_LABLES = self.TEST_DATA.pop(target)
        for x in listdir(filepath+"/models"):

            if(x[0]=="e"):#Loding the models starting with e
                with open(filepath+"/models/"+x,"rb") as f:
                    self.MODELS.append(load(f))
            elif(x[0]=="w"):#loading the weights
                with open(filepath+"/models/"+x,"rb") as f:
                   self.WEIGHT = (load(f))
    
        weights_copy = self.WEIGHT.copy()
        self.WEIGHT = list(self.WEIGHT.values())
        t = sum(self.WEIGHT)
        self.WEIGHT = [x/t for x in self.WEIGHT]
        
        #Write a code that create malicious
        self.MALICIOUS = [False for x in range(len(self.MODELS))]
        for x in range(malicous):
            v = list(weights_copy.values())
            k = list(weights_copy.keys())
            max_k = k[v.index(max(v))]
            self.MALICIOUS[max_k] = True
            weights_copy[max_k] = -95
        

    def malicious_predict(self,voting,prediction):
        """
            - Takes the prediction and returns the wrong prediction
            - Both for soft and hard voting
            - Hard coded for the case of MNIST data set
        """
        #print(prediction)
        if(voting == "hard"):
            #print("Inside hard")
            for i,x in enumerate(prediction):
                x1 = rand(0,10)
                while x1 == x:#Findind sum number that is not same as x1
                    x1 = rand(0,10)#Careful, not agnostic
                prediction[i] = x1
            return prediction

        if(voting == "soft"):
            for i,y in enumerate(prediction):
                x = max(y)
                x1 = prediction[i].index(x) 
                prediction[i][x1] = 0.000000000000000000001
                
                
            return prediction

    def predict_custom(self,voting = "hard",init = False):
        pred = {}
        final_pred = []
        temp = []
        if(voting == "hard"):
            for i,x in enumerate(self.MODELS):
                pred[i] =  x.predict(self.TEST_DATA)
                if(self.MALICIOUS[i]):

                    pred[i] = self.malicious_predict(voting,pred[i])
            for x in range(len(pred[0])):
                temp = {}
                for y in range(0,5):#5Should be Expert Number
                    if(temp.get(pred[y][x],9512) == 9512):
                        temp[int(pred[y][x])] = 1
                    else:
                        temp[pred[y][x]]+=1
                f_pred = 0
                for z in temp:
                    if(f_pred < temp[z]):
                        f_pred = z
                final_pred.append(f_pred)
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            #print("[VOTING]Hard Voting is Used for TREEMA",t)
            return(t)

        if(voting == "soft"):
            DATA_FRAMES = []
        #print("Shape of Test Data:",test_data.shape)
            for i,x in enumerate(self.MODELS):
                pred[i] = x.predict_proba(self.TEST_DATA).tolist()
                if(self.MALICIOUS[i]):
                    pred[i] = self.malicious_predict(voting,pred[i])

            for x in pred:
                DATA_FRAMES.append(pd.DataFrame(pred[x]))
            FINAL_DATA = pd.concat(DATA_FRAMES)
            by_row_index = FINAL_DATA.groupby(FINAL_DATA.index)
            df_means = by_row_index.mean()
            final_pred = df_means.idxmax(axis=1).to_list()
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            #print("\t\t\t[VOTING]Soft Voting is Used for TREEMA",t)
            return(t)



    def predict_treema(self,voting = "hard",init = False):
        pred = {}
        final_pred = []
        temp = []

        if(voting == "hard"):
            for i,x in enumerate(self.MODELS):
                pred[i] =  x.predict(self.TEST_DATA)
                if(self.MALICIOUS[i]):
                    pred[i] = self.malicious_predict(voting,pred[i])
            for x in range(len(pred[0])):
                temp = {}
                for y in range(0,5):#5Should be Expert Number
                    if(temp.get(pred[y][x],9512) == 9512):
                        temp[int(pred[y][x])] = self.WEIGHT[y]
                    else:
                        temp[pred[y][x]]+=self.WEIGHT[y]
                f_pred = 0
                for z in temp:
                    if(f_pred < temp[z]):
                        f_pred = z
                final_pred.append(f_pred)
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)

            return(t)

        if(voting == "soft"):
            DATA_FRAMES = []
        #print("Shape of Test Data:",test_data.shape)
            for i,x in enumerate(self.MODELS):
                pred[i] = x.predict_proba(self.TEST_DATA)*self.WEIGHT[i]
                pred[i] = pred[i].tolist()
                if(self.MALICIOUS[i]):
                    pred[i] = self.malicious_predict(voting,pred[i])

            for x in pred:
                DATA_FRAMES.append(pd.DataFrame(pred[x]))
            FINAL_DATA = pd.concat(DATA_FRAMES)
            by_row_index = FINAL_DATA.groupby(FINAL_DATA.index)
            df_means = by_row_index.mean()
            #print("PREDICTIONG:",df_means)
            final_pred = df_means.idxmax(axis=1).to_list()
            t = accuracy_score(self.TEST_DATA_LABLES,final_pred)
            #print("\t\t\t[VOTING]Soft Voting is Used for TREEMA",t)
            return(t)

def dir_iter(filepath,PROTOCOL,NUM_EXPERT,NUM_ROUNDS,NUMBER,PERCENT,MALICIOUS):
    fp = ""
    t = 0
    count = 0
    f = open("malicious.csv","a")
    writer = csv.writer(f)
    TREEMA = {"soft":[],"hard":[]}
    CUSTOM = {"soft":[],"hard":[]}
    for x in listdir(filepath):
        fp = filepath+"/"+x
        print("Processing:",fp)
        print("\tDetails",PROTOCOL,NUM_EXPERT,NUM_ROUNDS,NUMBER,PERCENT,MALICIOUS)
        c = Predictor(fp,"lable",MALICIOUS)
        t = c.predict_treema(voting="hard")
        TREEMA["hard"].append(t)
        t = c.predict_treema(voting="soft")
        TREEMA["soft"].append(t)
        t = c.predict_custom(voting="hard")
        CUSTOM["hard"].append(t)
        t = c.predict_custom(voting="soft")
        CUSTOM["soft"].append(t)
        count+=1
    result = []
    for i in TREEMA:
        a = ["TREEMA",PROTOCOL,i,NUM_EXPERT,NUM_ROUNDS,MALICIOUS,PERCENT,sum(TREEMA[i])/(count),statistics.stdev(TREEMA[i])]
        b = ["BASE",PROTOCOL,i,NUM_EXPERT,NUM_ROUNDS,MALICIOUS,PERCENT,sum(CUSTOM[i])/(count),statistics.stdev(CUSTOM[i])]
        result.append(a)
        result.append(b)

    with open("./malicious/"+str(NUMBER)+".csv","w") as f:
        w = csv.writer(f)
        for x in result:
            w.writerow(x)

#platfrom,PROTOCOL,VOTING,NUM_EXPERT,NUM_ROUNDS,MALICIOUS_EXPERT,MEAN_ACC,STD
def parser(name):

    PROTOCOL = name.split(";")[0]
    MAX_ROUND=int(name.split("=")[-1][:-1])
    NUM_ROUND = int(name.split(";")[1].split("=")[-1])
    return PROTOCOL,NUM_ROUND,MAX_ROUND

shutil.rmtree('./malicious', ignore_errors=True)
os.mkdir("./malicious")
count = 0
baser={}
for z in os.listdir("../results"):
    PATH = "../results/"+z
    PROTOCOL,NUM_EXPERT,NUM_ROUNDS = parser(z)
    baser[count]=[PATH,PROTOCOL,NUM_EXPERT,NUM_ROUNDS,count,0,0]

    count+=1

count = 0
PROCESS = []
for z in range(0,72):
    baser[z][-1] = round(0*baser[z][2])
    baser[z][-2] = 0
    baser[z][-3] = count
    count+=1
    process0= Process(target=dir_iter,args=baser[z])
    process0.start()

    baser[z][-1] = round(0.2*baser[z][2])
    baser[z][-2] = 20
    baser[z][-3] = count
    count+=1
    process1= Process(target=dir_iter,args=baser[z])
    process1.start()


    baser[z][-1] = round(0.4*baser[z][2])
    baser[z][-2] = 40
    baser[z][-3] = count
    count+=1
    process2= Process(target=dir_iter,args=baser[z])
    process2.start()

    baser[z][-1] = round(0.6*baser[z][2])
    baser[z][-2] = 60
    baser[z][-3] = count
    count+=1
    process3= Process(target=dir_iter,args=baser[z])
    process3.start()

    baser[z][-1] = round(0.8*baser[z][2])
    baser[z][-2] = 80
    baser[z][-3] = count
    count+=1
    process4= Process(target=dir_iter,args=baser[z])
    process4.start()



    PROCESS.append(process0)
    PROCESS.append(process1)
    PROCESS.append(process2)
    PROCESS.append(process3)
    PROCESS.append(process4)
    break


for x in PROCESS:
    x.join()


print("\n\nAll the Processing DONE")




