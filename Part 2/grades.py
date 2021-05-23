import csv
import sys
from sys import argv

def cal(row,sub,ind,max,list):
    if(int(row[sub])>max):
        max=int(row[sub])
        list[ind]=[row['Name']]
    elif(int(row[sub])==max):
        list[ind].append(row['Name'])
    return list,max
def hi():
    with open(sys.argv[1], mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        total,math,bio,eng,phy,che,hin=dict(),0,0,0,0,0,0
        sub=['Maths','Biology','English','Physics','Chemistry','Hindi']
        list=[[],[],[],[],[],[]]
        for row in csv_reader:
            total[row['Name']]=int(row['Maths'])+int(row['Biology'])+int(row['English'])+int(row['Physics'])+int(row['Chemistry'])+int(row['Hindi'])
            list,math=cal(row,'Maths',0,math,list)
            list,bio=cal(row,'Biology',1,bio,list)
            list,eng=cal(row,'English',2,eng,list)        
            list,phy=cal(row,'Physics',3,phy,list)
            list,che=cal(row,'Chemistry',4,che,list)
            list,hin=cal(row,'Hindi',5,hin,list)
    ind=0
    for i in list:
        print("Topper in ",sub[ind],"is ",end="")
        print(*list[ind], sep=", ") 
        ind+=1
    print("\n-------------------------------------------\n")
    count=0
    for i in sorted(total, key=total.get, reverse=True):
        count+=1
        print(count,'.',i)        
        if(count==3):
            break
