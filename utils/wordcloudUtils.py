from nltk.corpus import stopwords as stopwordlib 
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import re

stopwords = stopwordlib.words('english')
stopwords.extend(['hai','nhi','mai','toh','ho','kya','na','ka','hi','ki','tum','nahi','bhi',
                  'haan','se','ke','tha','k','aur','rhe','ko','rhi','main','mujhe','abhi','voh','b',
                  'hun','thi','hain','ek','kar','rha','e','hoga','kal','lekin','tumne',
                  'hua','arey','pr','koi','liye','hum','maine','gaya','accha','aa','tumhe','mera',
                  'kuch','yeh','hota','u','ye','time','bohot','er','tumhara','lab',
                  'kyun','kr','class','fir','sir','hu','gayi','karna','chahiye','acha','n','jo','nt'])

le = WordNetLemmatizer()

def preprocess(text):   
    
    tokens=word_tokenize(text.lower())
    
    punctuation=re.compile('[^a-zA-Z]*')    
    post_punctutation=([punctuation.sub("", word) for word in tokens])
      
    stem_token=[le.lemmatize(word) for word in post_punctutation]    
    stem_token=[token for token in stem_token if token not in stopwords]
    return " ".join(stem_token)