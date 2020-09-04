#Author Yuxuan Wu
#prompting message

#this is a specified multi cores program, it use 32 cores currently. Make sure you have enough cores or it will have some errors
#the number of cores used has marked in program, if you want to change the usage of cores, there are three place need to be changed
#if i%32 != num: continue
#pool = multiprocessing.Pool(processes=32)
#for xx in xrange(32):

#If data is large, limited the record value
#Sometimes deltaT < 0 in MC data
#Modify cores before each time
#cuts: z > 550mm
#rho < 6000mm
#delr < 1000mm
#delt between 0.52 and 1000

#This program will generate two files with number of prompt and delayed events

import multiprocessing
import ROOT
import csv
#multicores general value
pnum = multiprocessing.Manager().list()
dnum = multiprocessing.Manager().list()

def find_1(num):
    infile = ROOT.TFile("combine.root")
    tree = infile.Get("output")
    #N = tree.GetEntries()
    N = 100
    for i in range(N):
        #number equals qures
        if i%32 != num: continue
        if i%10000 == 0:
            print("dealing with"+str(i)+"events")
        tree.GetEntry(i)
        #basic check
        dcApplied = tree.dcApplied
        dcFlagged = tree.dcFlagged
        if (((dcApplied & 0x210000003FF6) & dcFlagged ) != (dcApplied & 0x210000003FF6)): continue
        fitvalid = tree.fitValid
        if fitvalid==0: continue
        #get prompt time
        uTSecs = tree.uTSecs
        uTNSecs = tree.uTNSecs
        TimePri = uTSecs*1e9 + uTNSecs
        #get prompt place
        posx = tree.posx
        posy = tree.posy
        posz = tree.posz - 108
        r = (posx*posx+posy*posy+posz*posz)**0.5
        if posz < 750: continue
        #get prompt energy
        nhitsCleaned = tree.nhitsCleaned
        for ii in range(i+1,N):
            tree.GetEntry(ii)
            dcApplied = tree.dcApplied
            dcFlagged = tree.dcFlagged
            if (((dcApplied & 0x210000003FF6) & dcFlagged ) != (dcApplied & 0x210000003FF6)): continue
            itvalid = bool(tree.fitValid)
            if itvalid == 0: continue
            #get delayed time
            TSecs = tree.uTSecs
            TNSecs = tree.uTNSecs
            TimePri_1 = TSecs*1e9 + TNSecs
            deltaT = abs((TimePri_1 - TimePri)/1000)
            #get delayed place
            osx = float(tree.posx)
            osy = float(tree.posy)
            osz = float(tree.posz) - 108
            #get delayed nhits
            hitsCleaned = int(tree.nhitsCleaned)

            #cuts for deltat
            if deltaT > 1000: break
            if deltaT < 0.52: continue
            
            #calculate distance
            vz = posz
            vy = posy
            vx = posx
            distance = ((vx-osx)*(vx-osx)+(vy-osy)*(vy-osy)+(vz-osz)*(vz-osz))**0.5
            
            #cut for delta r
            if distance > 1000: continue
            r_1 = (osx*osx+osy*osy+osz*osz)**0.5
            #cut for position z for delayed events
            if osz < 750: continue
            #cut for radius
            if r > 6000:continue
            elif r_1 > 6000:continue
            #cut for nhits
            if nhitsCleaned > 1700: continue
            if nhitsCleaned < 300: continue

            if hitsCleaned > 720: continue
            if hitsCleaned < 500: continue
            #record event number
            pnum.append(i)
            dnum.append(ii)
     #only for check whether all done or not
    return(i)

#multicores, list cores after processes=
pool = multiprocessing.Pool(processes=32)
pool_list = []
#number equals cores
for xx in xrange(32):
    pool_list.append(pool.apply_async(find_1, (xx, )))

pool.close()
pool.join()

with open("csv_pevents.csv","w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(pnum)
with open("csv_devents.csv","w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(dnum)


