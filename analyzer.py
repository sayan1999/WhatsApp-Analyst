from utils.promptnessUtils import penaltyForDelay, pointsForMsg, getbonusForRec, getlen
from utils.plotUtils import gradientbars, getTimeNum
from data_loader.attachment_loader import Chat_loader
from utils.wordcloudUtils import preprocess
from utils.fileReadUtils import makedirectory
from utils.datetimeUtils import dateTodtime
import matplotlib, datetime, numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from random import randint
from threading import Thread

# datetime converter for a matplotlib plotting method
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % randint(60, 100)

class Analyst:
    
    def __init__(self):
        self.__content = Chat_loader().getData()
        self.__user = self.__content["User"]
        self.__directry = makedirectory('./images/'+self.__user+'_'+str(datetime.datetime.now()))
        self.__friends = self.__content["Friends"]
        self.__data = []
        for data in self.__content["Data"].values():
            self.__data += data
        self.__datetime= sorted([row['DateTime'] for row in self.__data])

    def start(self):
        threads=[]
        threads.append(Thread(target=self.__plotChatperDay)) 
        threads.append(Thread(target=self.__plotChatperMonth)) 
        threads.append(Thread(target=self.__plotChatperSlot)) 
        threads.append(Thread(target=self.__plotPromptness)) 
        threads.append(Thread(target=self.__plotWordCloud)) 
        for t in threads:
            t.start() 
            t.join()                 
    
    def __plotChatperDay(self):

#         Scale x-axis according to num of days
        onlyDates = [dateTodtime(dtime.date()) for dtime in self.__datetime]
        numOfDays = (max(onlyDates).date()-min(onlyDates).date()).days
        xl = int(max((numOfDays)/20, 10))
        xlim=(matplotlib.dates.date2num(min(onlyDates)), matplotlib.dates.date2num(max(onlyDates)))
                
        
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
        plt.hist(onlyDates, bins=numOfDays, color='black', edgecolor=edgecolor)
        
#         Label graph
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus day since you started', color='white', size = 15)
        plt.xlabel("Month Start", color='white', size = 10)
        plt.ylabel("Chats Per Day", color='white', size = 10)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelcolor = 'white')
        plt.grid(b=True, axis= 'y', color='green')
        plt.savefig(self.__directry+'/'+title.get_text()+'.png')
        plt.show()      
        
        
    def __plotChatperMonth(self):
        
#         Scale x-axis according to num of months        
        dateMonths = [datetime.datetime(dtime.year, dtime.month, 1) for dtime in self.__datetime]
        xlim=(matplotlib.dates.date2num(min(dateMonths)), matplotlib.dates.date2num(max(dateMonths)))
        
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
        barMap = Counter(dateMonths)
        barDict={ month : barMap.get(month, 0) for month in set(dateMonths)}
        bars=ax.bar(barDict.keys(), barDict.values(), width=20)
        gradientbars(bars, ax, max(barDict.values()))

#         Label graph        
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus month since you started', color='white', size = 15)
        plt.xlabel("Month", color='white', size = 14)
        plt.ylabel("Chats Per Month", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        plt.savefig(self.__directry+'/'+title.get_text()+'.png')
        plt.show()
        
        
    def __plotChatperSlot(self):

        DEFAULTDATE= (1900, 1, 1)
        LASTMINOFDAY= (23, 59)
        
#         Categorize chats into timeslots
        timestamps = [datetime.datetime(*DEFAULTDATE, dtime.hour, dtime.minute) for dtime in self.__datetime]
        slots=[0, 3, 5, 7, 9, 12, 15, 17, 19, 21]
        bins=[getTimeNum(e) for e in slots] + [datetime.datetime(*DEFAULTDATE, *LASTMINOFDAY)]
        
        timedict={}
        for time in timestamps:
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
        plt.savefig(self.__directry+'/'+title.get_text()+'.png')
        plt.show()

    
    def __readNEvalConvWith(self, friend):

        # constant
        THRESHHOLDDELAYFORCONVO = 300

        chatdata=self.__content['Data'][friend]
        person=self.__user
        
        # setting variables before iteration
        sdate=dateTodtime(chatdata[0]['DateTime'].date())
        edate=dateTodtime(chatdata[-1]['DateTime'].date())
        
        userInteraction={}
        userInteraction[person]={}
        userInteraction[friend]={}
        
        #  initial conditions
        conversation=False
        lastgotreply=actuallastDtime=lastDtimeToCalcDelayFrom=chatdata[0]['DateTime']
        pastuser=chatdata[0]['Author']
        recurrency=rotation=0
        messageOverhead=0
    
        for chat in chatdata[1:]:
            
            # setting var for current iteration
            curuser=chat['Author']
            curdate=dateTodtime(chat['DateTime'].date())
            curdatetime=chat['DateTime']
            diffromlastgotreply=(curdatetime-lastgotreply).seconds

            if curuser==pastuser:
                
                if conversation:
                    lastDtimeToCalcDelayFrom = curdatetime

                if diffromlastgotreply > THRESHHOLDDELAYFORCONVO :
                    conversation = False

                messageOverhead += getlen(chat['Message'])
                recurrency += 1

                if not(conversation):
                    rotation = 0
            
            else:
                if recurrency:
                    userInteraction[pastuser][curdate]=(userInteraction[pastuser].get(curdate, 0) + 
                                        pointsForMsg(messageOverhead) * getbonusForRec(recurrency))
                
                if conversation:
                    delay=0
                else:
                    delay=(curdatetime-lastDtimeToCalcDelayFrom).seconds/60

                actualdelay=(curdatetime-actuallastDtime).seconds
                userInteraction[curuser][curdate]=(userInteraction[curuser].get(curdate, 0) + 
                                        pointsForMsg(getlen(chat['Message'])) * getbonusForRec(rotation) - 
                                        penaltyForDelay(conversation, delay, recurrency))

                if actualdelay < THRESHHOLDDELAYFORCONVO:
                    conversation = True
                else:
                    conversation = False

                messageOverhead=0
                recurrency = 0
                rotation += 1
                lastDtimeToCalcDelayFrom=curdatetime
                pastuser=curuser
                lastgotreply=actuallastDtime

            actuallastDtime=curdatetime         

        
        # those days without chat don't have keys, so insert them with value = 0
        oneday=datetime.timedelta(days=1)
        rangeofdays=(edate-sdate).days
        tempdate=sdate
        for _ in range(rangeofdays+1):
            userInteraction[person][tempdate]=userInteraction[person].get(tempdate, 0)
            userInteraction[friend][tempdate]=userInteraction[friend].get(tempdate, 0)
            tempdate+=oneday            
        
        # Normalize first day interaction to the mean of all days
        for person in userInteraction:
            userInteraction[person][sdate]=sum(list(userInteraction[person].values()))/len(userInteraction[person])
            
        return userInteraction        

    def __calcPromptness(self, friend):
        
        promptnessDataInConvWithaFriend=self.__readNEvalConvWith(friend)

        BETA=0.9
        persons=[]
        plotdata=[]
        # turn day-to-day promptness to exponentially weighted promptness
        for person, evaledConv in promptnessDataInConvWithaFriend.items():
            
            persons.append(person)
            avgdata={}
            evaledConv={key:evaledConv[key] for key in sorted(evaledConv.keys())}
            sortedkeys, sorteddata=list(evaledConv.keys()), list(evaledConv.values())
            avgdata[sortedkeys[0]]=sorteddata[0]
            for i in range(1, len(evaledConv)):
                avgdata[sortedkeys[i]]=avgdata[sortedkeys[i-1]]*BETA+sorteddata[i]*BETA 
            plotdata.append(avgdata)               

        return [persons, plotdata]


    def __plotPromptness(self): 

        for friend in self.__friends:
            persons, plotdata =  self.__calcPromptness(friend)             
        
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
            
            plt.plot(list(plotdata[0].keys()), list(plotdata[0].values()), label=persons[0], color='yellow', linewidth=2)
            plt.plot(list(plotdata[1].keys()), list(plotdata[1].values()), label=persons[1], color='blue', linewidth=1)
        
            
    #         Label graph
            title=ax.set_title('Your WhatsApp chat response promptness with '+friend, color='white', size = 15)
            plt.xlabel("Months", color='white', size = 10)
            plt.ylabel("Promptness coofficient", color='white', size = 10)
            plt.tick_params(axis='x', which='both', labelcolor='white')
            plt.tick_params(axis='y', which='both', left=False, labelcolor = 'white')
            plt.grid(b=True, axis= 'y', color='green')
            ax.legend()
            plt.savefig(self.__directry+'/'+title.get_text()+'.png')
            plt.show()

    def __plotWordCloud(self):

        self.__vocab = preprocess(" ".join([d['Message'] for d in self.__data]))

        background_col='#1e272e'
        wordcloud = WordCloud(width = 1024, height = 1024,
                background_color = background_col, 
                min_font_size = 10, margin=1).generate(self.__vocab)  
                
        plt.title('WordCloud with most used words', color='white', size = 15) 
        plt.imshow(wordcloud.recolor(color_func=grey_color_func, random_state=3), interpolation="bilinear")
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.savefig(self.__directry+'/'+'Wordcloud.png')        
        plt.show()     

if __name__ == '__main__':
    
    analyzer=Analyst()
    analyzer.start()
    