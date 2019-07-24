import urllib.request
import urllib.parse
import time
import csv 
import argparse

parser = argparse.ArgumentParser(description="Uses HTML requests to obtain new images of each APSU parking lot")
parser.add_argument('InputLocation', metavar='inputfile', nargs='?', type=str, help='name/location of input csv file',default='in.csv')
parser.add_argument('OutputLocation',metavar='outfile',nargs='?',type=str,help='name/location of output csv file',default='out.csv')
args = parser.parse_args()

#Load HTTP request and storage location from CSV into array then step through 

InImages= []
OutImages=[]
counter=0  
Bool_continue=True 


with open(args.InputLocation) as imageIn:
   #Load all the content at once
        fileReader=csv.reader(imageIn)
        ##for load in imageInput: 
            ## Input.append(load)
        for load in fileReader: 
            InImages.append(load[0])  
   
         
with open(args.OutputLocation) as imageOut:
   #Load all the content at once
        fileReader=csv.reader(imageOut)
        ##for load in imageInput: 
            ## Input.append(load)
        for load in fileReader: 
            OutImages.append(load[0]) 
            
print('\n\nThis program will continue to update the parking lot image every 3 minutes.')
while Bool_continue== True:             
    for counter in range(len(InImages)): 
        InImage   = str(InImages[counter])
        InStorage = str(OutImages[counter])
      
        image=urllib.request.URLopener()
        image.retrieve(InImage,InStorage) 
        time.sleep(180) 
        print("An image refresh occured.")
    
