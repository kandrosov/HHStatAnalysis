# Provides scale factors for event reweighting based on an analytical model.
# This file is part of https://github.com/cms-hh/HHStatAnalysis.
# compiling

import ROOT
import numpy as np
from array import array
import matplotlib
import matplotlib.pyplot as plt

class NonResonantModel:
    def __init__(self):
        # read coefficients from the input file here
        # to store coefficients use self.
        self.effSM = np.zeros((3,13))
        self.effSum = np.zeros((3,13))
        self.MHH = np.zeros((3,13))
        self.COSTS = np.zeros((3,13))
        self.A1 = np.zeros((3,13))
        self.A3 = np.zeros((3,13))
        self.A7 = np.zeros((3,13))
        print "initialize"

    # Declare the function
    def functionGF(self, kl,kt,c2,cg,c2g,A): return A[0]*kt**4 + (A[1]*kt**2 )*kl**2 + A[2]*kt*kl*kt**2 

    def ReadCoefficients(self,inputFileName) : #,effSM,MHH,COSTS,A1,A3,A7):
        # here you should return TH2D histogram with BSM/SM coefficientes to calculate the scale factors for m_hh vs. cos_theta_star
        # loop over events and efficency calculation will be channel-dependent, so corresponding code
        # should go to the other file
        #filne = "coefficientsByBin_klkt.txt"
        f = open(inputFileName, 'r+')
        lines = f.readlines() # get all lines as a list (array)
        # Read coefficients by bin
        countercost=0
        countermhh=0
        for line in  lines:
          l = []
          tokens = line.split()
          for token in tokens:
              num = ""
              num_char = "."
              num2 = "e"
              num3 = "-"
              for char in token: 
                  if (char.isdigit() or (char in num_char) or (char in num2) or (char in num3)): num = num + char
              try: l.append(float(num))
              except ValueError: pass
          self.MHH[countercost][countermhh] = l[1] 
          self.COSTS[countercost][countermhh] = l[2] 
          self.effSM[countercost][countermhh] = l[3]/10000. # in units of 10k events
          self.effSum[countercost][countermhh] = l[4]/10000. # in units of 10k events # 12 JHEP benchmarks 
          # Just for testing purposes the above contains the number of events by bin from an ensenble of events 
          # calculated from the 12 benchmarks defined in 1507.02245v4 (JHEP version) each one with 100k events
          self.A1[countercost][countermhh] = l[5]
          self.A3[countercost][countermhh] = l[6]
          self.A7[countercost][countermhh] = l[7]
          countercost+=1
          if countercost == 3 :
             countercost=0
             countermhh+=1
        f.close()
        # and at the end of the function return it
        print "Stored coefficients by bin"

    def getNormalization(self,kl, kt,HistoAllEvents):   
      sumOfWeights = 0 
      A13tev = [2.09078, 0.282307, -1.37309]
      sumW=0
      sumW2=0
      sumSM=0
      HistW= float((1000.-250.)*2)
      # print HistoAllEvents.GetNbinsX(),HistoAllEvents.GetNbinsY() 
      for binmhh in range (0,HistoAllEvents.GetNbinsX()) :
         WX = HistoAllEvents.GetXaxis().GetBinWidth(binmhh+1)
         for bincost in range (0,HistoAllEvents.GetNbinsY()) :
            WY = HistoAllEvents.GetYaxis().GetBinWidth(bincost+1)
            A = [self.A1[bincost][binmhh],self.A3[bincost][binmhh],self.A7[bincost][binmhh]]
            #if HistoAllEvents.GetBinContent(binmhh,bincost) > 0 : 
            sumOfWeights+=float(self.effSM[bincost][binmhh]*self.functionGF(kl,kt,0,0,0,A)/self.functionGF(kl,kt,0,0,0,A13tev))
            sumW+=self.functionGF(kl,kt,0,0,0,A13tev)
            sumW2+=self.functionGF(kl,kt,0,0,0,A)
            sumSM+=self.effSM[bincost][binmhh]
            #/ HistoAllEvents.GetBinContent(binmhh,bincost) # / (WX*WY)
            # sumW+=(WX*WY)
            # HistoAllEvents.GetBinWidth(binmhh,bincost) #.GetBinContent(binmhh,bincost)
      #print sumW, sumW2,sumSM, HistW
      #A = [self.A1[1][5],self.A3[1][5],self.A7[1][5]]
      #print "in bin 5,1", float(self.effSM[1][5]*self.functionGF(kl,kt,0,0,0,A)/self.functionGF(kl,kt,0,0,0,A13tev))
      return float(sumOfWeights)

    # distribute the calculated GenMHH and CostS in the bins numbering  (matching the coefficientsByBin_klkt.txt)
    def getScaleFactor(self,mhhcost,kl, kt, effSumV0) : # ,effSM,MHH,COSTS,A1,A3,A7):   
       binGenMHH = [250.,270.,300.,330.,360.,390., 420.,450.,500.,550.,600.,700.,800.,1000.]
       binGenCostS  = [ -1., -0.55,0.55,1.  ]
       # determine from which bin the event belong
       binmhh = 0
       bincost = 0
       for ii in range (0,13) : 
         if mhhcost[0] > binGenMHH[12-ii] : 
            binmhh = 12-ii 
            break
       for ii in range (0,3) : 
         if mhhcost[1] > binGenCostS[2-ii] : 
            bincost = 2-ii
            break
       # calculate the weight
       A13tev = [2.09078, 0.282307, -1.37309]
       #if effSum > 0 and A1 > 0: 
       if effSumV0 > 0 :
          A = [self.A1[bincost][binmhh],self.A3[bincost][binmhh],self.A7[bincost][binmhh]]
          effBSM = float(self.effSM[bincost][binmhh]*self.functionGF(kl,kt,0,0,0,A)/self.functionGF(kl,kt,0,0,0,A13tev))
          #if v1 ==0 : CalcWeight = effBSM/float(effSum[bincost][binmhh]) # ==> JHEP sum in denominator
          CalcWeight = effBSM/float(effSumV0) # ==> V0 sum in denominator (Moriond 2016)
          return CalcWeight
       else : return 0


    ### only to read the text files to test

    def ReadLine(self,line, countline,Px,Py,Pz,En) :
            l = []
            tokens = line.split()
            for token in tokens:
                num = ""
                num_char = "."
                num2 = "e"
                num3 = "-"
                for char in token:     
                    if (char.isdigit() or (char in num_char) or (char in num2) or (char in num3)): num = num + char
                try: l.append(float(num))
                except ValueError: pass
            if countline < 2 :
               Px[countline] = l[1] 
               Py[countline] = l[2]
               Pz[countline] = l[3]
               En[countline] = l[4]
            #return countline

    def CalculateMhhCost(self,mhhcost,countline,Px,Py,Pz,En) :
               # calculate reweigthing 
               if abs(Px[0])!= abs(Px[1]) : print "error parsing ascii file"
               P1 = ROOT.TLorentzVector()
               P1.SetPxPyPzE(Px[0],Py[0],Pz[0],En[0])    
               P2 = ROOT.TLorentzVector()
               P1.SetPxPyPzE(Px[1],Py[1],Pz[1],En[1])
               SUM = ROOT.TLorentzVector()
               SUM.SetPxPyPzE(Px[0]+Px[1],Py[0]+Py[1],Pz[0]+Pz[1],En[0]+En[1])
               mhhcost[0]=SUM.M()
               P1boost = P1
               P1boost.Boost(-SUM.BoostVector())
               mhhcost[1] = float(P1boost.CosTheta())

    def LoadTestEvents(self,CalcMhhTest,CalcCostTest,filne) :
       counteventSM = 0
       Px = np.zeros((2)) 
       Py = np.zeros((2)) 
       Pz = np.zeros((2)) 
       En = np.zeros((2)) 
       f = open(filne, 'r+')
       lines = f.readlines() # get all lines as a list (array)
       countline = 0 # particuliarity of the text file with events = each 2 lines are one event there
       for line in  lines:
             self.ReadLine(line, countline,Px,Py,Pz,En)
             #print countline
             countline+=1
             mhhcost= [0,0] # to store [mhh , cost] of that event
             if countline==2 : # if read 2 lines 
                self.CalculateMhhCost(mhhcost,countline,Px,Py,Pz,En) # ==> adapt to your input 
                countline=0
                CalcMhhTest[counteventSM] = float(mhhcost[0])
                CalcCostTest[counteventSM] = float(mhhcost[1])
                counteventSM+=1

    ###################################################
    # Draw the histograms
    #####################################################
    def plotting(self,kl,kt, CalcMhh,CalcCost,CalcWeight,CalcMhhTest,CalcCostTest,drawtest):
      c2 = 0
      cg = 0
      c2g = 0
      print "Plotting test histograms"
      bin_size = 40; min_edge = 260; max_edge = 1000
      N = (max_edge-min_edge)/bin_size; Nplus1 = N + 1
      bin_list = np.linspace(min_edge, max_edge, Nplus1)
      plt.xlim(min_edge, max_edge)
      if drawtest==1 : plt.hist(CalcMhhTest, bin_list , normed=1,  histtype='bar', label='simulated', color= 'r', edgecolor='r', lw=3)
      plt.hist(CalcMhh, bin_list, weights=CalcWeight , normed=1, histtype='bar', label='reweigted', fill=False, color= 'k', edgecolor='k')
      plt.legend(loc='upper right')
      plt.title(" In  kl =="+str(kl)+", kt =="+str(kt)+", c2 =="+str(c2)+", cg =="+str(cg)+", c2g ==" +str(c2g) )
      plt.xlabel("Mhh (GeV)")
      plt.ylabel("events")
      plt.savefig("Mhh_kl_"+str(kl)+"_kt_"+str(kt)+"_c2_"+str(c2)+"_cg_"+str(cg)+"_c2g_" +str(c2g)+".pdf")
      plt.cla()   # Clear axis
      plt.clf()   # Clear figure
      plt.close() 
      bin_size = 0.2; min_edge = -1; max_edge = 1
      N = (max_edge-min_edge)/bin_size; Nplus1 = N + 1
      bin_list = np.linspace(min_edge, max_edge, Nplus1)
      plt.xlim(min_edge, max_edge)
      if drawtest==1 : plt.hist(CalcCostTest, bin_list , normed=1,  histtype='bar', label='simulated', color= 'r', edgecolor='r', lw=3)
      plt.hist(CalcCost, bin_list, weights=CalcWeight , normed=1, histtype='bar', label='reweigted', fill=False, color= 'k', edgecolor='k', lw=3)
      plt.title(" In  kl =="+str(kl)+", kt =="+str(kt)+", c2 =="+str(c2)+", cg =="+str(cg)+", c2g ==" +str(c2g) )
      plt.legend(loc='upper right')
      plt.xlabel("Cost*")
      plt.ylabel("events")
      plt.savefig("CostS_kl_"+str(kl)+"_kt_"+str(kt)+"_c2_"+str(c2)+"_cg_"+str(cg)+"_c2g_" +str(c2g)+".pdf")
      plt.cla()   # Clear axis
      plt.clf()   # Clear figure
      plt.close() 

