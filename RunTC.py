#!/usr/bin/enc python
"""

RunTC.py

Python script that demonstrates usage of TwitterClassification.py

screen_name and handle are synonymous

@author Christine Chen
@date 12/17/16
 
"""

import TwitterClassification
import sys
from twython import Twython
import threading
import time
import datetime

#how many Twitter entities to pull info from
PULL_AND_CLASSIFY_THRESH = 250
#only pull and classify friend info from entities with this many friends or less
FRIEND_THRESH = 5000

"""
progress_bar_loading

c/o http://thelivingpearl.com/2012/12/31/creating-progress-bars-with-python/
creates a thread that runs a spinny wait gadget on the commandline while 
potentially another task executes
"""
class progress_bar_loading(threading.Thread):
    
    def run(self):
            global stop
            global kill
            sys.stdout.flush()
            i = 0
            while stop != True:
                    if (i%4) == 0: 
                    	sys.stdout.write('\b/')
                    elif (i%4) == 1: 
                    	sys.stdout.write('\b-')
                    elif (i%4) == 2: 
                    	sys.stdout.write('\b\\')
                    elif (i%4) == 3: 
                    	sys.stdout.write('\b|')

                    sys.stdout.flush()
                    time.sleep(0.2)
                    i+=1
                    
            if kill == True: 
            	print ('\b\b\b\b ABORT!'),
            



#instantiate Twython object
#INSERT YOUR TWITTER TOKENS HERE!
twitter=Twython(app_key='APP KEY HERE',
      app_secret='APP SECRET HERE',
      oauth_token='OAUTH TOKEN HERE',
      oauth_token_secret='OAUTH TOKEN SECRET HERE')


#ask user to provide "start" Twitter handle#############################
start_handle = input("Twitter handle: ")
#check user input
if(TwitterClassification.get_twitter_info([start_handle],TwitterClassification.SCREEN_NAME, twitter) == TwitterClassification.ERROR):
    print("Issue with handle provided. Exiting program\n")
    sys.exit(1)
print("\n")
    
#handles_new contains a list of all handles to gather data from
handles_new = [start_handle]
#dictionary that contains key:value in the form of handle:time_info_pulled_from_handle
#this dictionary will ensure that there is no redundant scraping
handles_done = {}

train_file = "training_set.csv"
test_file = "testing_set.csv"

#create the classifier and test it############################################################
print("-----CREATING CLASSIFIER-----\n")
kill = False      
stop = False
p = progress_bar_loading()
p.start()

classifier = None

try:
    classifier = TwitterClassification.create_classifier(train_file)
    stop = True
except KeyboardInterrupt or EOFError:
    kill = True
    stop = True
    print("Error in creating classifier. Exiting program.")
    sys.exit(1)

if(classifier == TwitterClassification.ERROR):
    print("Error in creating classifier. Exiting program.")
    sys.exit(1)
    
print("-----TESTING CLASSIFIER-----\n")
if(TwitterClassification.test_classifier(test_file, classifier) == TwitterClassification.ERROR):
    print("Error in testing classifier. Exiting program.")
    sys.exit(1)

print("-----BEGINNING DATA COLLECTION AND CLASSIFICATION PHASE-----\n")

#while there are still handles to pull information from...
while(handles_new != []):
    
    #accumulator that holds all orgs returned by pull_and_classify in the following
    #for loop to repopulate handles_new
    orgs_found = []
    
    print("#####Scraping FRIEND info for the following Twitter entities#####")
    print(handles_new)
    print("\n")
    
     
    num_handles_new = len(handles_new)
    counter = 0
    
    for handle in handles_new: 
        
        ##CHECK TO SEE IF LIMIT HAS BEEN HIT###############
        if(len(handles_done)>=PULL_AND_CLASSIFY_THRESH):
            break
        
        #display the handle being processed
        counter = counter + 1
        print("Entity %s/%s: %s" % (str(counter), num_handles_new, handle))
        
        ##CHECK TO SEE IF ENTITY HAS TOO MANY FRIENDS######
        handle_info = TwitterClassification.get_twitter_info([handle], TwitterClassification.SCREEN_NAME, twitter)
        if(handle_info != []):
            num_friends = handle_info[0]['friends_count']
            if(num_friends>FRIEND_THRESH):
                print("%s has too many friends (%s). Skipping.\n" % (handle, str(num_friends)))
                continue
        else:
            print("Issue with pulling data from Twitter API. Skipping.\n")
            continue
        
        #GO AHEAD AND PULL AND CLASSIFY FRIEND INFO NOW######
        new_orgs_found = TwitterClassification.pull_and_classify(handle, TwitterClassification.FRIEND, classifier, twitter)
        if(new_orgs_found == TwitterClassification.ERROR):
            print("Error in pulling Twitter information for %s. Skipping.\n" % handle)
            continue
        orgs_found = orgs_found + new_orgs_found
        
        #add handle to handles_done 
        handles_done[handle] = "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())
        
    #clean out handles_new
    for handle in handles_new:
        handles_new.remove(handle)
   
    #fill handles_new with new orgs that are not already in handles_done dictionary
    handles_new = [x for x in orgs_found if x not in handles_done]

