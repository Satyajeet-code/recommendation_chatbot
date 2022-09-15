#!/usr/bin/env python
# coding: utf-8

# In[18]:


import nltk           #used for nautral language processing
import numpy as np    #used for arrays and matrices manipulation
import random         #used to select a random string/number or anything within a given constraint(preferably)
import string         # to process standard python strings
from sklearn.feature_extraction.text import TfidfVectorizer    #used to convert texts into vectors
from sklearn.metrics.pairwise import cosine_similarity         #used to calculate distance between 2 values
from sklearn.neighbors import NearestNeighbors       #a distance based machine learning algorithm (uses cosine similarity internally)
import requests        #used to search the web
from bs4 import BeautifulSoup #used to simlify/beautify the extracted web code
import warnings              
import psycopg2
warnings.filterwarnings("ignore")   #used to ignore the warnings


# In[24]:


host= "localhost"
username= "postgres"
database="postgres"
password= "Satya1234"
port= 5432
# con=psycopg2.connect(host=host,dbname=database,user=username,password=password,port=port)
# cur=con.cursor()
def chat(a):
    global wiki_text
    global url
    global r
    global soup
    global resp
    global remove_punct_dict
########################### checking if file exists or else getting data from wikipedia ##################################    
    try:
        f=open(a+'.txt','r',errors = 'ignore')
    except FileNotFoundError:
        print('No data found for your search')
        print('Now searching the web:\n')
        url='https://www.google.com/search?q='+a
        r=requests.get(url)
        soup=BeautifulSoup(r.text)


        links = []
        for link in soup.findAll('a'):
            links.append(link.get('href'))


        link_index_list=[]   
        for i in links:
            if 'wikipedia' in i:
                link_index_list.append(links.index(i))

        if len(link_index_list)!=0:
            ind=link_index_list[0]        
            end_index=links[ind].index('&')
            
#             https://en.wikipedia.org/wiki/Vikrant_Rona&amp



            print(links[ind][7:end_index])



            url=links[ind][7:end_index]

            if 'img' or 'jpg' or'jpeg' in url:
                ind=link_index_list[1]        
                end_index=links[ind].index('&')
                print(links[ind][7:end_index])
                url=links[ind][7:end_index]
                r=requests.get(url)
                soup=BeautifulSoup(r.text)
                wiki_text=soup.find_all('p')[1].text
            else:
                r=requests.get(url)
                soup=BeautifulSoup(r.text)
                wiki_text=soup.find_all('p')[1].text
            if len(wiki_text)==1:
                wiki_text=soup.find_all('p')[2].text
        else:
            print('Enter correct movie name')
            
#             try:
#                 wiki_text=soup.find_all('p')[1].text
#             except:
#                 print('check the format of your input')
        if len(wiki_text)==0:
            print('Sorry no data found')
        else:
            wiki_text = wiki_text.encode("ascii", "ignore")
            wiki_text = wiki_text.decode()
            with open(a+".txt", "w") as text_file:
                text_file.write(wiki_text)
                f=open(a+'.txt','r',errors = 'ignore')
##################################### Basic NLP ###################################################            
        
    raw=f.read() #reads the content of your file as a string
    raw=raw.lower()# converts to lowercase
    nltk.download('punkt') # first-time use only
    nltk.download('wordnet') # first-time use only
    sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
    word_tokens = nltk.word_tokenize(raw)# converts to list of words
    lemmer = nltk.stem.WordNetLemmatizer()
#WordNet is a semantically-oriented dictionary of English included in NLTK.
#lematization is a process to convert words into its root form (going > go)
    def LemTokens(tokens):                                                  
        return [lemmer.lemmatize(token) for token in tokens]
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    def LemNormalize(text):
        return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
#################################### Greeting ##############################################################
    GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey")
    GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
    def greeting(sentence):

        for word in sentence.split():
            
            
            if word.lower() in GREETING_INPUTS:
                
                resp=random.choice(GREETING_RESPONSES)
                insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
                value=(sentence,resp)
#                 cur.execute(insert_script,value)
#                 con.commit()
                
                return random.choice(GREETING_RESPONSES)
############################################# Getting similar movies ################################################################
    def get_similar_movies(sentence):
        
        
        if 'similar' or 'like' in sentence:
            url = "https://google.com/search?q="+'movies like '+a
            r = requests.get(url)
            soup = BeautifulSoup (r.text)
            return 'ROBOT: Since you liked '+a +' you will also like '+ (soup.find("div", class_= 'BNeawe s3v9rd AP7Wnd').text)
    def get_rotten_rating(sentence):
        
        
        if 'rating' in sentence:
            url='https://www.google.com/search?q='+ 'rotten tomatoes rating of '+a
            r=requests.get(url)
            soup=BeautifulSoup(r.text)
            s=soup.find("span", class_='oqSTJd').text

            return 'ROBOT: The rotten tomatoes rating of  '+a +' is '+ s
    def show_text_file(sentence):
        
        if 'txt' or 'text' in sentence:
            try:
                f=open(a+'.txt','r',errors = 'ignore')
            except FileNotFoundError:
                print('No file found')
            return str(f.read())

        
    def response(user_response):
        
        robo_response=''
        TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
        tfidf = TfidfVec.fit_transform(sent_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx=vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if req_tfidf==0:
            robo_response=robo_response+"I am sorry! I don't understand you"
            resp=robo_response
            insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
            value=(user_response,resp)
#             cur.execute(insert_script,value)
#             con.commit()
            return robo_response
        else:
            robo_response = robo_response+sent_tokens[idx]
            resp=robo_response
            insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
            value=(user_response,resp)
#             cur.execute(insert_script,value)
#             con.commit()
            return robo_response
    flag=True
    print("ROBO: My name is Robot. I will answer your queries. If you want to exit, type Bye!")
    while(flag==True):
        user_response = input()
        user_response=user_response.lower()
        if user_response!='bye':
            if user_response=='thanks' or user_response=='thank you':
                flag=False
                resp="You are welcome.."
                insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
                value=(user_response,resp)
#                 cur.execute(insert_script,value)
#                 con.commit()
                print("ROBOT: You are welcome..")
                
            elif 'txt'  in user_response or 'text' in user_response:
                print("ROBOT: " + show_text_file(user_response))
                resp=show_text_file(user_response)
                insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
                value=(user_response,resp)
#                 cur.execute(insert_script,value)
#                 con.commit()
                
                
            elif 'similar' in user_response or 'like' in user_response:
                resp=get_similar_movies(user_response)
                insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
                value=(user_response,resp)
#                 cur.execute(insert_script,value)
#                 con.commit()
                print("ROBOT: "+ get_similar_movies(user_response))
            
            elif 'rating' in user_response:
                resp=get_rotten_rating(user_response)
                insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
                value=(user_response,resp)
#                 cur.execute(insert_script,value)
#                 con.commit()
                print("ROBOT: "+ get_rotten_rating(user_response))
            

            else:
                if greeting(user_response)!=None:
                    resp=greeting(user_response)
                    insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
                    value=(user_response,resp)
                    cur.execute(insert_script,value)
#                     con.commit()
                    print("ROBOT: "+greeting(user_response))
#                 elif(get_similar_movies(user_response)!=None and 'similar' or 'like' in  user_response):
#                 elif 'similar' or 'like' in  user_response:
#                     print("ROBO: "+get_similar_movies(user_response))
                else:
                    sent_tokens.append(user_response)
                    word_tokens=word_tokens+nltk.word_tokenize(user_response)
                    final_words=list(set(word_tokens))
                    print("ROBOT: ",end="")
                    print(response(user_response))
#                     con.commit()
                    sent_tokens.remove(user_response)
                

        else:
            flag=False
            resp="Bye! take care.."
            insert_script="INSERT INTO chatbot (question,answer) values (%s,%s)"
            value=(user_response,resp)
#             cur.execute(insert_script,value)
#             con.commit()
            print("ROBOT: Bye! take care..")
   


# In[ ]:


chat('Vikrant Rona')

