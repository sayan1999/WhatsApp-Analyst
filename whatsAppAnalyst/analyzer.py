import matplotlib, datetime, numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from random import randint
from threading import Thread
from sys import argv
from os.path import isfile, isdir
from time import sleep
from sklearn.feature_extraction.text import TfidfVectorizer
from matplotlib.font_manager import FontProperties
from os.path import join as pathjoin

from lib.utils.promptnessUtils import penaltyForDelay, pointsForMsg, getbonusForRec, getlen
from lib.utils.plotUtils import gradientbars, getTimeNum, gradientbarsHor
from data_loader.attachment_loader import Chat_loader
from lib.utils.wordcloudUtils import preprocess, stopwords
from lib.utils.fileReadUtils import makedirectory
from lib.utils.datetimeUtils import dateTodtime
from lib.mail.mailman import MailSender
from lib.message_class.msg_class import Msg
from lib.mainlogger.log import log


# datetime converter for a matplotlib plotting method
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % randint(60, 100)

class Analyst:
    
    def __init__(self, path):
        
        self.__directryToAttch=pathjoin('../data/attachments', path)
                
        self.__content = Chat_loader(self.__directryToAttch).getData()
        self.__msg = Msg(self.__content["Response"])
        self.__mailid = self.__content["MailID"]
        self.__user = self.__content["User"]
        self.__friends = self.__content["Friends"]

        self.__directry = makedirectory(pathjoin('../data/images', str(datetime.datetime.now()) +'_'+ self.__user ))
        self.__data = []
        for data in self.__content["Data"].values():
            self.__data += data
        self.__datetime = sorted([row['DateTime'] for row in self.__data])

    def getdir(self):
        return self.__directry
    
    def __endAck(self):

        if isdir(self.__directry):
            open(pathjoin(self.__directry, 'ends'), 'w+')

    def __mailToUser(self):
        log.info(self.__msg.get_msg())
        m=MailSender(config='lib/mail/mail.json', logger=log)
        m.sendmail(self.__user, self.__mailid, self.__directry, msg=self.__msg.get_msg())                
        
    def start(self):
        if len(self.__data)==0:
            self.__msg.new_msg("Couldn't retrieve data :(, some error in your file")
            log.info(self.__directryToAttch + ": Data could not be read")
            self.__mailToUser()
            return
        threads=[]
        threads.append(Thread(target=self.__plotChatperDay, name="plotChatperDay"))
        threads.append(Thread(target=self.__plotChatperMonth, name="plotChatperMonth"))
        threads.append(Thread(target=self.__plotChatperSlot, name="plotChatperSlot"))
        threads.append(Thread(target=self.__plotPromptness, name="plotPromptness"))
        threads.append(Thread(target=self.__plotWordCloud, name="plotWordCloud"))
        threads.append(Thread(target=self.__plotChatPerPerson, name="plotChatPerPerson"))
        threads.append(Thread(target=self.__plotLangdiversity, name="plotLangdiversity"))
        threads.append(Thread(target=self.__plot_tf_idf, name="plot_tf_idf"))
        threads.append(Thread(target=self.__plotEmoji, name="plotEmoji"))

        for t in threads:
            t.start() 
            t.join() 

        self.__endAck()
        self.__mailToUser()
        
    
    def __plotChatperDay(self):

         #Scale x-axis according to num of days
        onlyDates = [dateTodtime(dtime.date()) for dtime in self.__datetime]
        if len(onlyDates) == 0:
            log.info(self.__directryToAttch + ": No dates available, unable to plotChatperDay")
            return

        numOfDays = (max(onlyDates).date()-min(onlyDates).date()).days+1
        xlim=(matplotlib.dates.date2num(min(onlyDates)), matplotlib.dates.date2num(max(onlyDates)))
        
        
         #Configurations
        plt.style.use('dark_background')
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        edgecolor='#b8b7a7'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.xlim=xlim 

         #plot 
        plt.hist(onlyDates, bins=numOfDays, color='black', edgecolor=edgecolor)
        
         #Label graph
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus day since you started', color='white', size = 15)
        plt.xlabel("Month Start", color='white', size = 10)
        plt.ylabel("Chats Per Day", color='white', size = 10)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelcolor = 'white')
        plt.grid(b=True, axis= 'y', color='green')
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        log.info("Plotted chat per day")
        # plt.show()      
        
        
    def __plotChatperMonth(self):
        
         #Scale x-axis according to num of months        
        dateMonths = [datetime.datetime(dtime.year, dtime.month, 1) for dtime in self.__datetime]
        if len(dateMonths) == 0:
            log.info(self.__directryToAttch + ": No month data available, unable to plotChatperMonth")
            return
        xlim=(matplotlib.dates.date2num(min(dateMonths)), matplotlib.dates.date2num(max(dateMonths)))
        
         #Configurations
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.xlim=xlim 
                
         #Plot
        barMap = Counter(dateMonths)
        barDict={ month : barMap.get(month, 0) for month in set(dateMonths) }
        bars=ax.bar(barDict.keys(), barDict.values(), width=20)
        gradientbars(bars, ax, max(barDict.values()))

         #Label graph        
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus month since you started', color='white', size = 15)
        plt.xlabel("Month", color='white', size = 14)
        plt.ylabel("Chats Per Month", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        log.info("Plotted chat per month")
        # plt.show()
        
        
    def __plotChatperSlot(self):

        DEFAULTDATE= (1900, 1, 1)
        LASTMINOFDAY= (23, 59)
        
         #Categorize chats into timeslots
        timestamps = sorted([datetime.datetime(*DEFAULTDATE, dtime.hour, dtime.minute) for dtime in self.__datetime])
        if len(timestamps) == 0:
            log.info(self.__directryToAttch + ": No slot data available, unable to plotChatperSlot")
            return
        slots=[0, 3, 5, 7, 9, 12, 15, 17, 19, 21]
        bins=[getTimeNum(e) for e in slots] + [datetime.datetime(*DEFAULTDATE, *LASTMINOFDAY)]
        
        timedict={i : 0 for i in range(10)}
        for time in timestamps:
            for i in range(len(bins)-1):
                if time>=bins[i] and time<bins[i+1]:
                    timedict[i] += 1
                    break
                    
         #Setting ticklabels
        timeticks=[bins[i] + (bins[i+1]-bins[i])/2 for i in range(10)]
        timetickstr=[bins[i].strftime('%-I %p') + ' - ' + bins[i+1].strftime('%-I %p') for i in range(10)]
        timetickstr[9]='9 PM - 11:59 PM'
        
         #Configurations
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)

                
         #Plot
        bars=ax.bar(range(10), timedict.values(), width=0.7)
        gradientbars(bars, ax, max(timedict.values()))

         #Label graph        
        title=ax.set_title('Your WhatsApp chat frequency with ' + ", ".join(self.__friends) + ' versus per daytime slot since you started', color='white', size = 15)
        plt.xlabel("Timeslot", color='white', size = 14)
        plt.ylabel("Chats Per timeslot", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        ax.set_xticks(range(len(timeticks)))
        ax.set_xticklabels(timetickstr)
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        log.info("Plotted chat per slot")
        # plt.show()

    
    def __readNEvalConvWith(self, friend):

        # constant
        THRESHHOLDDELAYFORCONVO = 300

        if self.__content['Data'].get(friend, None) == None:
            log.info(self.__directryToAttch + ": No data available with friend" + friend)
            return []

        chatdata=self.__content['Data'][friend]
        if len(chatdata) == 0:
            log.info(self.__directryToAttch + ": No chatdata available with friend "+friend)
            return

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
        
            # Configurations
            plt.style.use('dark_background')
            fig=plt.figure(figsize=(20, 10))
            ax=plt.axes()
            backgorund_col='#1e272e'
            ax.set_facecolor(backgorund_col)
            fig.set_facecolor(backgorund_col)
            for spine in ax.spines.values():
                spine.set_visible(False)

             #plot 
            
            if len(plotdata[0]):
                plt.plot(list(plotdata[0].keys()), list(plotdata[0].values()), label=persons[0], color='yellow', linewidth=2)
            else:
                log.info(self.__directryToAttch + ": No promptness data available for " + persons[0])

            if len(plotdata[1]):
                plt.plot(list(plotdata[1].keys()), list(plotdata[1].values()), label=persons[1], color='blue', linewidth=1)
            else:
                log.info(self.__directryToAttch + ": No promptness data available for " + persons[1])
            
             #Label graph
            title=ax.set_title('Your WhatsApp chat response promptness with '+friend, color='white', size = 15)
            plt.xlabel("Months", color='white', size = 10)
            plt.ylabel("Promptness coofficient", color='white', size = 10)
            plt.tick_params(axis='x', which='both', labelcolor='white')
            plt.tick_params(axis='y', which='both', left=False, labelcolor = 'white')
            plt.grid(b=True, axis= 'y', color='green')
            ax.legend()
            plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
            log.info("Plotted promptness for " + " ".join(persons))
            # plt.show()

    def __plotWordCloud(self):

        vocab = preprocess(" ".join([d['Message'] for d in self.__data]))
        if len(vocab) == 0:
            log.info(self.__directryToAttch + ": No word available, unable to plotWordcloud")
            return

        background_col='#1e272e'
        wordcloud = WordCloud(width = 1024, height = 1024,
                background_color = background_col, 
                min_font_size = 10, margin=1).generate(vocab)  
        ax=plt.axes()
        ax.legend().remove()
        plt.title('WordCloud with most used words', color='white', size = 15) 
        plt.imshow(wordcloud.recolor(color_func=grey_color_func, random_state=3), interpolation="bilinear")
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.savefig(self.__directry+'/'+'Wordcloud.png', facecolor=background_col)      
        log.info("Plotted wordcloud")
        # plt.show()   
      
    def __plotChatPerPerson(self):

        chatperPerson={}

        for data in self.__data:
            chatperPerson[data['Author']] = chatperPerson.get(data['Author'], 0) + len(data['Message'].split())
        no_of_persons = len(chatperPerson.keys())

        if not no_of_persons:
            log.info(self.__directryToAttch + ": No data for chatPerPerson")
            return
    
         #Configurations
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)
                
         #Plot
        bars=ax.bar(list(range(1, no_of_persons+1)), chatperPerson.values(), width=0.7)
        gradientbars(bars, ax, max(chatperPerson.values()))

         #Label graph        
        title=ax.set_title('Total weight of chats since you started', color='white', size = 15)
        # plt.xlabel("Person", color='white', size = 14)
        plt.ylabel("Chat count", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        ax.set_xticks(range(1, no_of_persons+1))
        ax.set_xticklabels(chatperPerson.keys())
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        log.info("Plotted chat per person")
        # plt.show()      

      
    def __plotLangdiversity(self):

        wordperPerson={}

        self.__perPersonDoc={}

        for data in self.__data:
            wordperPerson[data['Author']] = wordperPerson.get(data['Author'],[]) + data['Message'].split()
            self.__perPersonDoc[data['Author']] = self.__perPersonDoc.get(data['Author'], "") + " " + data['Message']
        
        if not len(wordperPerson):
            log.info(self.__directryToAttch + ": No data for plotLangdiversity")
            return

        for key in wordperPerson:
            wordperPerson[key] = len(set(wordperPerson[key]))
            
        no_of_persons = len(wordperPerson.keys())

        if not no_of_persons:
            log.info(self.__directryToAttch + ": No data for langDiversity")
            return
    
         #Configurations
        fig=plt.figure(figsize=(15, 10))
        ax=plt.axes()
        backgorund_col='#1e272e'
        ax.set_facecolor(backgorund_col)
        fig.set_facecolor(backgorund_col)
        for spine in ax.spines.values():
            spine.set_visible(False)
                
         #Plot
        bars=ax.bar(list(range(no_of_persons)), wordperPerson.values(), width=0.7)
        gradientbars(bars, ax, max(wordperPerson.values()))

         #Label graph        
        title=ax.set_title('Lexical Diversity per person', color='white', size = 15)
        # plt.xlabel("Person", color='white', size = 14)
        plt.ylabel("Count of unique words", color='white', size = 14)
        plt.tick_params(axis='x', which='both', bottom=False, labelcolor='white')
        plt.tick_params(axis='y', which='both', left=False, labelright=True, labelcolor = 'white')
        ax.set_xticks(range(no_of_persons))
        ax.set_xticklabels(wordperPerson.keys())
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        log.info("Plotted lang_diversity")
        # plt.show() 

    def __plot_tf_idf(self):

        if not len(self.__perPersonDoc):
            log.info(self.__directryToAttch + ": No data for tf_idf")
            return

        vectorizer = TfidfVectorizer(stop_words=stopwords)
        vectors = vectorizer.fit_transform(self.__perPersonDoc.values())
        features = vectorizer.get_feature_names()

        denseVectors = vectors.todense()
        persons=list(self.__perPersonDoc.keys())
        perPersontfidf = {}
        for i in range(len(persons)):

            numberofwords=min(len(features), 5)
            indices=denseVectors[i].argsort().tolist()[0][-numberofwords:]            
            perPersontfidf[persons[i]]={features[j]:denseVectors[i, j] for j in indices}

        
        no_of_plots=len(persons)

        if not no_of_plots:
            log.info(self.__directryToAttch + ": No data for tf_idf")
            return
        fig, ax = plt.subplots(no_of_plots)
        if no_of_plots==1:
            ax=np.array([ax])
        backgorund_col='#1e272e'
        fig.set_facecolor(backgorund_col)

        for i in range(no_of_plots):

            ax[i].set_facecolor(backgorund_col)

            bars=ax[i].barh(range(len(perPersontfidf[persons[i]])), perPersontfidf[persons[i]].values(), height=0.7)
            gradientbarsHor(bars, ax[i], max(perPersontfidf[persons[i]].values()), 0.2)

            ax[i].set_yticks(range(len(perPersontfidf[persons[i]])))
            ax[i].set_yticklabels(perPersontfidf[persons[i]].keys())
            
            for spine in ax[i].spines.values():
                spine.set_visible(False)
            
            ax[i].set_title(persons[i], color='white', size=7)
            plt.sca(ax[i])
            plt.tick_params(axis='x', bottom=False, labelcolor='white', labelsize=7)
            plt.tick_params(axis='y', left=False, labelcolor = 'white')

         #Label graph         
        title=plt.suptitle('Words uniquely used by person significantly more than others', color='white', size = 10)
        fig.text(0.5, 0.02, s="Coefficient of usage", color='white', size = 14, ha='center')
                
        log.info("Plotted tf_ifd")
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        # plt.show() 
        

    def __plotEmoji(self):

        prop=FontProperties(fname="../data/fonts/Symbola.ttf")
        plt.rcParams['font.family'] = prop.get_family()

        emojiperperson={}

        for d in self.__data:
            emojiperperson[d['Author']] = emojiperperson.get(d['Author'], []) + d['Emoji']

        for key in emojiperperson:
            emojiperperson[key]=Counter(emojiperperson[key])

        if not len(emojiperperson):
            log.info(self.__directryToAttch + ": No data for plot emoji")
            return

        emojimap={}

        for person, value in emojiperperson.items():

            emojis=list(value.keys())
            count=np.array(list(value.values()))

            no_of_emojis=min(len(emojis), 6)
            indices = count.argsort()[-no_of_emojis:]
            emojimap[person] = { emojis[j] : count[j] for j in indices }

        persons=list(emojimap.keys())
        no_of_plots=len(persons)
        if not no_of_plots:
            log.info(self.__directryToAttch + ": No data for tf_idf")
            return
        fig, ax = plt.subplots(no_of_plots)
        if no_of_plots==1:
            ax=np.array([ax])
        backgorund_col='#1e272e'
        fig.set_facecolor(backgorund_col)

        for i in range(no_of_plots):

            ax[i].set_facecolor(backgorund_col)

            if not len(emojimap[persons[i]]):
                log.info("No emojis from "+person[i])
                continue

            bars=ax[i].barh(range(len(emojimap[persons[i]])), emojimap[persons[i]].values(), height=0.7)
            gradientbarsHor(bars, ax[i], max(emojimap[persons[i]].values()), 20)

            ax[i].set_yticks(range(len(emojimap[persons[i]])))
            ax[i].set_yticklabels(emojimap[persons[i]].keys())
            
            for spine in ax[i].spines.values():
                spine.set_visible(False)
            
            ax[i].set_title(persons[i], color='white', size=7)
            plt.sca(ax[i])
            plt.yticks(fontsize=30, fontproperties=prop)
            plt.tick_params(axis='x', bottom=False, labelcolor='white', labelsize=7)
            plt.tick_params(axis='y', left=False, labelcolor = 'white')

         #Label graph         
        title=plt.suptitle('Most used emojis per person', color='white', size = 10)
        fig.text(0.5, 0.02, s="Frequency", color='white', size = 14, ha='center')
                
        log.info("Plotted emojiMap")
        plt.savefig(self.__directry+'/'+title.get_text()+'.png', facecolor=backgorund_col)
        # plt.show()         


if __name__ == '__main__':
    
    
    if len(argv) != 2:
        print("Correct Usage: script 'path to directory'")
        exit()

    if not(argv[1].startswith('./attachments/ CREATE,ISDIR ')):
        print('not a folder')
        exit()
    
    dirpath=argv[1].split('./attachments/ CREATE,ISDIR ')[1]
    while(not(isfile('../data/attachments/'+dirpath+'/ends'))):
        print("...")
        sleep(5)
    analyzer=Analyst(dirpath)
    analyzer.start()
    log.info("Ended")