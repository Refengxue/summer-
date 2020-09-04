#Author Yuxuan Wu
#prompting message
#this is a 3 cores program
#If data is large, limited the record value
#Sometimes deltaT < 0 in MC data
#Modify cores before each time
#this is used to analysis events found in file multi_MC_anal.py
#this is an example of display result
#if you need to check more values, please do following steps
#create a new multiprocessing.Manager().list() variable after what I made
#append values in list just created

import multiprocessing
import ROOT
import numpy as np
import array
#multicores general value
#you can delet them and corresponding .append part at the same time
delt = multiprocessing.Manager().list()
pev= multiprocessing.Manager().list()
dev= multiprocessing.Manager().list()
delr = multiprocessing.Manager().list()
prad = multiprocessing.Manager().list()
drad = multiprocessing.Manager().list()
pnh = multiprocessing.Manager().list()
dnh = multiprocessing.Manager().list()
#read part, do not delet it
pev = np.loadtxt('csv_pevents.csv',delimiter = ',',skiprows = 0)
dev = np.loadtxt('csv_devents.csv',delimiter = ',',skiprows = 0)

#progress finction, _2 means analysis part
def find_2(num):
    infile = ROOT.TFile("combine.root")
    tree = infile.Get("output")
    N = len(pev)
    for i in range(N):
        #number equals qures
        if i%3 != num: continue
        tree.GetEntry(int(pev[i]))
        uTSecs = tree.uTSecs
        uTNSecs = tree.uTNSecs
        TimePri = uTSecs*1e9 + uTNSecs
        #get prompt place
        posx = tree.posx
        posy = tree.posy
        posz = tree.posz - 108
        radius = np.sqrt(posx*posx + posy*posy + posz*posz)
        pnh.append(tree.nhitsCleaned)
        tree.GetEntry(int(dev[i]))
        TSecs = tree.uTSecs
        TNSecs = tree.uTNSecs
        TimePri_1 = TSecs*1e9 + TNSecs
        #get prompt place
        osx = tree.posx
        osy = tree.posy
        osz = tree.posz - 108
        distance = ((posx-osx)*(posx-osx)+(posy-osy)*(posy-osy)+(posz-osz)*(posz-osz))**0.5 
        deltaT = abs((TimePri_1 - TimePri)/1000)
        drad.append(np.sqrt(osx*osx + osy*osy + osz*osz))
        #record value
        delt.append(deltaT)
        delr.append(distance)
        prad.append(radius)
        dnh.append(tree.nhitsCleaned)

    #only for check whether all done or not
    return(i)

#multicores, list cores after processes=
pool = multiprocessing.Pool(processes=3)
pool_list = []
#number equals cores
for xx in xrange(3):
    pool_list.append(pool.apply_async(find_2, (xx, )))

pool.close()
pool.join()
#record value in TH1D & TH2D
h1 = ROOT.TH1D("time","delta_t",200,0,1000)
h2 = ROOT.TH1D("delta_r","distance",50,0,1000)
h3 = ROOT.TH1D("radius","rad",100,0,6500)
h4 = ROOT.TH1D("radius","rad",100,0,6500)
h5 = ROOT.TH1D("pnhits","prompt",80,0,2000)
h6 = ROOT.TH1D("dnhits","delayed",80,0,2000)
for i in range(len(delt)):
    h1.Fill(delt[i])
    h2.Fill(delr[i])
    h3.Fill(prad[i])
    h4.Fill(drad[i])
    h5.Fill(pnh[i])
    h6.Fill(dnh[i])
#plot and save need to improve
c1 = ROOT.TCanvas("c1")
h1.Draw()
