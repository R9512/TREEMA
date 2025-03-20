from os import listdir
from sklearn.ensemble import VotingClassifier
from pickle import load
from sklearn.metrics import accuracy_score
import statistics
import shutil
import os
import pandas as pd
from multiprocessing import Process
from time import sleep

BASE = "./To_SERVER"
class Gas_Giver:
    def calc(self,filepath):
        self.manger_gas = 0
        self.expert_gas = 0
        count = 0
        for x in listdir(filepath):
            with open(filepath+"/"+x+"/models/gasUsed.pickle","rb") as f:
                a = load(f)
            m,e = a["MANAGER"],sum(list(a["EXPERT"].keys()))
            self.manger_gas+=m
            self.expert_gas+=e
            count+=1
        return self.manger_gas/10,self.expert_gas/10,count


#main
G = Gas_Giver()
b = {"PROTOCOL":[],"NUM_EXPERT":[],"MAX_ROUNDS":[],"EXPERT":[],"MANAGER":[],"COUNT":[]}
for x in listdir(BASE):#Change to results
    a,a1,a2= G.calc(BASE+"/"+x)
    a3 = x.split(";")
    print(a3)
    b["PROTOCOL"].append(a3[0])
    b["NUM_EXPERT"].append(a3[1].split("=")[-1])
    b["MAX_ROUNDS"].append(a3[2].split("=")[-1])
    b["MANAGER"].append(a)
    b["EXPERT"].append(a1)
    b["COUNT"].append(a2)
data = pd.DataFrame(b)
data.to_csv("gas_used.csv",index=False)

