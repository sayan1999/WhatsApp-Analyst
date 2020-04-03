#!/usr/bin/env python
# coding: utf-8

from data_loader.attachment_loader import Chat_loader
from matplotlib import pyplot as plt
from collections import Counter
import matplotlib
import datetime
import numpy as np
from utils.promptnessUtils import penaltyForDelay, pointsForMsg, getbonusForRec, getlen
from utils.plotUtils import gradientbars, getTimeNum
from utils.wordcloudUtils import preprocess
from wordcloud import WordCloud
import datetime
from os import mkdir

# datetime converter for a matplotlib plotting method
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class Analyst:
    
    def __init__(self):
        self.__content = Chat_loader().getData()
        self.__user = self.__content["User"]
        self.__directry = './images/'+self.__user+'_'+str(datetime.datetime.now())
        mkdir(self.__directry)
        self.__friends = self.__content["Friends"]
        self.__data = []
        for data in self.__content["Data"].values():
            self.__data += data
        self.__datetime= [row['DateTime'] for row in self.__data]
        self.__timestamps = [row['Time'] for row in self.__data]
        self.__onlyDates = [row['Date'] for row in self.__data]
        self.__dateMonths = [datetime.datetime.strptime(row['Date'].strftime("%m %y"), "%m %y").date() for row in self.__data]

        
    
    def plotChatperDay(self):

#         Scale x-axis according to num of days
        numOfDays = (max(self.__onlyDates).date()-min(self.__onlyDates).date()).days
        xl = int(max((numOfDays)/20, 10))
        xlim=(matplotlib.dates.date2num(min(self.__onlyDates)), matplotlib.dates.date2num(max(self.__onlyDates)))
                
        
#         Configurations
        plt.style.use('dark_background')
        fig=plt.figure(figsize=(xl, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        edgecolor='#b8b7a7'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.xlim=xlim 

#         plot 
        plt.hist(self.__onlyDates, bins=numOfDays, color='black', edgecolor=edgecolor)
        
#         Label graph
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus day since you started', color='white', size = 15)
        plt.xlabel("Month Start", color='white', size = 10)
        plt.ylabel("Chats Per Day", color='white', size = 10)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelcolor = 'white')
        plt.grid(b=True, axis= 'y', color='green')
        plt.savefig(self.__directry+'/'+'_'+str(datetime.datetime.now())+'_'+str(title)+'.png')
        plt.show()
        
        
        
    def plotChatperMonth(self):
        
#         Scale x-axis according to num of months        
        xlim=(matplotlib.dates.date2num(min(self.__dateMonths)), matplotlib.dates.date2num(max(self.__dateMonths)))
        
#         Configurations
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.xlim=xlim 
                
#         Plot
        barMap = Counter(self.__dateMonths)
        barDict={ month : barMap.get(month, 0) for month in set(self.__dateMonths)}
        bars=ax.bar(barDict.keys(), barDict.values(), width=20)
        gradientbars(bars, ax, max(barDict.values()))

#         Label graph        
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus month since you started', color='white', size = 15)
        plt.xlabel("Month", color='white', size = 14)
        plt.ylabel("Chats Per Month", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        plt.savefig(self.__directry+'/'+str(datetime.datetime.now())+'_'+str(title)+'.png')
        plt.show()
        
        
    def plotChatperSlot(self):
        
#         Categorize chats into timeslots
        self.__timestamps=sorted(self.__timestamps)
        slots=[0, 3, 5, 7, 9, 12, 15, 17, 19, 21]
        bins=[getTimeNum(e) for e in slots] + [datetime.datetime(1900, 1, 1, 23, 59)]
        
        timedict={}
        for time in self.__timestamps:
            for i in range(len(bins)-1):
                if time>=bins[i] and time<bins[i+1]:
                    timedict[i] = timedict.get(i, 0) + 1
                    break
                    
#         Setting ticklabels
        timeticks=[bins[i] + (bins[i+1]-bins[i])/2 for i in range(10)]
        timetickstr=[bins[i].strftime('%-I %p') + ' - ' + bins[i+1].strftime('%-I %p') for i in range(10)]
        timetickstr[9]='9 PM - 11:59 PM'
        
#         Configurations
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)

                
#         Plot
        bars=ax.bar(range(10), timedict.values(), width=0.7)
        gradientbars(bars, ax, max(timedict.values()))

#         Label graph        
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus per daytime slot since you started', color='white', size = 15)
        plt.xlabel("Timeslot", color='white', size = 14)
        plt.ylabel("Chats Per timeslot", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        ax.set_xticks(range(len(timeticks)))
        ax.set_xticklabels(timetickstr)
        plt.savefig(self.__directry+'/'+str(datetime.datetime.now())+'_'+str(title)+'.png')
        plt.show()

    def promptPlot(self, friendname, plotlist):                
        
#         Configurations
        plt.style.use('dark_background')
        fig=plt.figure(figsize=(20, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)

#         plot 
        
        plt.plot(list(plotlist[1][0].keys()), list(plotlist[1][0].values()), label=plotlist[0][0], color='yellow', linewidth=2)
        plt.plot(list(plotlist[1][1].keys()), list(plotlist[1][1].values()), label=plotlist[0][1], color='blue', linewidth=1)
    
        
#         Label graph
        title=ax.set_title('Your WhatsApp chat response promptness with '+plotlist[0][1], color='white', size = 15)
        plt.xlabel("Months", color='white', size = 10)
        plt.ylabel("Promptness coofficient", color='white', size = 10)
        plt.tick_params(axis='x', which='both', labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelcolor = 'white')
        plt.grid(b=True, axis= 'y', color='green')
        ax.legend()
        plt.savefig(self.__directry+'/'+str(datetime.datetime.now())+'_'+str(title)+'.png')
        plt.show()


    def __getPromptness(self, friend):

        THRESHHOLDDELAYFORCONVO = 300
        chatdata=self.__content['Data'][friend]
        person=self.__user
        sdate=chatdata[0]['Date']
        edate=chatdata[-1]['Date']
        oneday=datetime.timedelta(days=1)
        rangeofdays=(edate-sdate).days
        userInteraction={}
        userInteraction[person]={}
        userInteraction[friend]={}
        
        conversation=False
        lastgotreply=actuallastdatetime=lastdatetime=chatdata[0]['DateTime']
        pastuser=chatdata[0]['Author']
        recurrency=rotation=0
        messageOverhead=0
        # reward for the very first message in chat
        userInteraction[pastuser][sdate]=100
        self.__vocab=chatdata[0]['Message']
        for chat in chatdata[1:]:
            self.__vocab += " " + (chat['Message'])
            curuser=chat['Author']
            curdate=chat['Date']
            curdatetime=chat['DateTime']
            diffromreply=(curdatetime-lastgotreply).seconds

            if curuser==pastuser:
                
                if conversation:
                    lastdatetime=curdatetime

                if diffromreply > THRESHHOLDDELAYFORCONVO :
                    conversation=False

                messageOverhead += getlen(chat['Message'])
                recurrency += 1
                if not(conversation):
                    rotation = 0
            
            else:
                if recurrency:
                    userInteraction[pastuser][curdate]=(userInteraction[pastuser].get(curdate, 0) + 
                                        pointsForMsg(messageOverhead) * getbonusForRec(recurrency))
                if conversation:
                    penaltydelay=0
                else:
                    penaltydelay=min(15, (curdatetime-lastdatetime).seconds/60)

                actualdelay=(curdatetime-actuallastdatetime).seconds
                userInteraction[curuser][curdate]=(userInteraction[curuser].get(curdate, 0) + 
                                        pointsForMsg(getlen(chat['Message'])) * getbonusForRec(rotation) - 
                                        penaltyForDelay(conversation, penaltydelay, recurrency))

                if actualdelay < THRESHHOLDDELAYFORCONVO:
                    conversation = True
                else:
                    conversation = False

                messageOverhead=0
                recurrency = 0
                rotation += 1
                lastdatetime=curdatetime
                pastuser=curuser
                lastgotreply=actuallastdatetime

            actuallastdatetime=curdatetime         

        tempcurdate=sdate
        for _ in range(rangeofdays+1):
            userInteraction[person][tempcurdate]=userInteraction[person].get(tempcurdate, 0)
            userInteraction[friend][tempcurdate]=userInteraction[friend].get(tempcurdate, 0)
            tempcurdate+=oneday            
        for person in userInteraction:
            userInteraction[person][sdate]=sum(list(userInteraction[person].values()))/len(userInteraction[person])
            
        return userInteraction

    def __calcPromptness(self):
        self.__promptdata={}
        for friend in self.__friends:
            self.__promptdata[friend]=self.__getPromptness(friend)

    def plotPromptness(self):
        self.__calcPromptness()

        for friendname, promptWithFriend in self.__promptdata.items():
            persons=[]
            plotdata=[]
            for p, data in promptWithFriend.items():
                avgdata={}
                persons.append(p)
                temp={key:data[key] for key in sorted(data.keys())}
                sortedkeys, sorteddata=list(temp.keys()), list(temp.values())
                avgdata[sortedkeys[0]]=sorteddata[0]
                for i in range(1, len(data)):
                    avgdata[sortedkeys[i]]=avgdata[sortedkeys[i-1]]*0.5+sorteddata[i]*0.5
                plotdata.append(avgdata)

            self.promptPlot(friendname, [persons, plotdata])

    def plotWordCloud(self):

        self.__vocab = preprocess(self.__vocab)

        wordcloud = WordCloud(width = 800, height = 800,
                background_color ='black', 
                min_font_size = 10).generate(self.__vocab)
  
                
        plt.figure(figsize = (8, 8), facecolor = None) 
        plt.imshow(wordcloud) 
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.savefig(self.__directry+'/'+str(datetime.datetime.now())+'_Wordcloud.png')        
        plt.show() 

if __name__ == '__main__':
    
    a=Analyst()
    a.plotChatperDay()
    a.plotChatperMonth()
    a.plotChatperSlot()
    a.plotPromptness()
    a.plotWordCloud()