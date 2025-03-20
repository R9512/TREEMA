import os
import toml
from os import listdir
from os import rmdir,mkdir
from shutil import copytree,rmtree
from time import sleep
from random import randint as rand
def copy_all_files(filename):#WORK HERE
    #Ensure that PARTIONS WERE DELETE
    for x in os.listdir("./runs"):
        rmtree("./runs/"+x+"/part_data",ignore_errors=True)
    copytree("./runs/", "./results/"+filename, symlinks=False, ignore=None,)
    rmtree("runs",ignore_errors=True)
    mkdir("./runs")

def count_instance():#Used For Generating POPULAR ONE
    count = 0
    for z in os.listdir("./runs"):
            if(os.path.isfile("./runs/"+z+"/models/gasUsed.pickle")):
                count+=1
            else:
                rmtree("./runs/"+z,ignore_errors=True)
    return(count)

def harvester(PROTOCOL):
    MAX_ITER = 10#Carefull
    for y in range(5,16,2):#EXPERTS CAREFUL 5 
        s = os.system("python3 setup.py "+str(y))#CAREFULL
        for z in range(5,15,3):#Round Numbers CAREFUL 5 
            current_iter = 0
            while current_iter < MAX_ITER:
                with open('config.toml', 'r') as f:
                    config = toml.load(f)
                    config["PROTOCOL"]["NAME"] = PROTOCOL
                    config["PROTOCOL"]["N"] = y
                    config["METADATA"]["NUM_PARTIONS"] = y
                    config["METADATA"]["MAX_ROUNDS"] = z
                    config["MALICIOUS"]["PROP"] = 0
                    config["MALICIOUS"]["LIST"] = [0 for x in range(0,y)]
                with open('config.toml', 'w') as f:
                    toml.dump(config, f)
                s = os.system("./setup.sh "+str(y-1)) #CAREFULL
                sleep(5)
                current_iter = count_instance()
                    
            copy_all_files(PROTOCOL+";NUM_EXPERT="+str(y)+";MAX_ROUNDS="+str(z))

rmtree("./results",ignore_errors=True)
os.mkdir("./results")
harvester("SNOWBALL")
harvester("SLUSH")
harvester("SNOWFLAKE")