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
#prompt nhits 300~1700
#delayed nhits 500~720

import multiprocessing
import ROOT
import csv
#multicores general value
filesa2 = multiprocessing.Manager().list()
pnum = multiprocessing.Manager().list()
dnum = multiprocessing.Manager().list()
filesa = multiprocessing.Manager().list()

#progress finction, _2 means version 2
def find_1(num):
    # list your file number need to be analysis here
    for fi in range(258300,258974):
        try:
            #this fine only analysis s004 part, in my project I use 11 files like this with S000 to S010 and submit in a job array
            #If you want to analysis in one single file, you can write a loop here
            open("Analysis40_r0000"+str(fi)+"_s004_p000.ntuple.root")
            filename = "Analysis40_r0000"+str(fi)+"_s004_p000.ntuple.root"
        except:
            try:
                open("Analysis40_r0000"+str(fi)+"_s004_p001.ntuple.root")
                filename = "Analysis40_r0000"+str(fi)+"_s004_p001.ntuple.root"
            except:
                if num==1:
                    print("Analysis40_r0000"+str(fi)+"_s004_p000.ntuple.root do not exist")
                continue
        infile = ROOT.TFile(filename)
        tree = infile.Get("output")
        if num == 1:
            print("file number: "+str(fi)+" is analysising")
        N = tree.GetEntries()
        for i in range(N):
            #number equals qures
            if i%32 != num: continue
            tree.GetEntry(i)
            #basic check
            dcApplied = tree.dcApplied
            dcFlagged = tree.dcFlagged
            if (((dcApplied & 0x210000003FF6) & dcFlagged) != (dcApplied & 0x210000003FF6)): continue
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
                #get delayed energy
                hitsCleaned = int(tree.nhitsCleaned)
                if deltaT < 0.52: continue
                if deltaT > 1000: break
                #calculate distance
                vz = posz
                vy = posy
                vx = posx
                distance = ((vx-osx)*(vx-osx)+(vy-osy)*(vy-osy)+(vz-osz)*(vz-osz))**0.5
                if distance > 1000: continue
                r_1 = (osx*osx+osy*osy+osz*osz)**0.5
                if osz < 750: continue
                prh = (vx*vx+vy*vy)**0.5
                drh = (osx*osx+osy*osy)**0.5
                if prh > 6000: continue
                if drh > 6000: continue
                #energy cut
                if nhitsCleaned > 1700: continue
                if nhitsCleaned < 300: continue
                if hitsCleaned > 720: continue
                if hitsCleaned < 500: continue
                if r > 6000: continue
                if r_1 > 6000: continue
                #record value
                pnum.append(i) 
                dnum.append(ii)
                filesa.append(fi)
                filesa2.append(r)

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
print(" ")
print("find total "+str(len(pnum))+"events")
print(" ")
print("find total "+str(len(pnum))+"events")
print(" ")
print("find total "+str(len(pnum))+"events")

with open("csv_events4.csv","w") as csvfile:
    for csvn in range(len(pnum)):
        writer = csv.writer(csvfile)
        writer.writerow([str(filesa[csvn])+"_soo4","   ",pnum[csvn],dnum[csvn]])



