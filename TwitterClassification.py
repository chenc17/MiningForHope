#!/usr/bin/enc python
"""

TwitterClassification.py

An API of sorts that allows for binary classification 
of Twitter entities based on their description field
 
Uses Twython module to access Twitter API
http://social-metrics.org/twitter-user-data/

Uses TextBlob module to create classifier
https://textblob.readthedocs.io/en/dev/

@author Christine Chen
@date 12/17/16
 
"""

################IMPORT STMTS###########################
import os
import string
import datetime
from textblob.classifiers import NaiveBayesClassifier
from tqdm import tqdm, trange #for progress bar
#from time import time, sleep
import time

#################"CONSTANTS"############################
MAX_RETURN = 100 #max amount of users Twitter lookup_user call returns
ID = "id"
SCREEN_NAME = "sn"
FRIEND = "FRIENDS"
FOLLOWER = "FOLLOWERS"
ERROR = -1
#used to distinguish between ORG and NORG 
ORG_THRESH = 0.85
KEYWORD_1_IN = "traffick"
KEYWORD_2_IN = "slave"

"""

clean

removes new lines, carriage return characters, and unprintable characters
lambda function c/o http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python

returns cleaned string
"""
#http://stackoverflow.com/questions/24358361/removing-u2018-and-u2019-character
def clean(str_to_clean):
    str_1 = str_to_clean.replace('\n', ' ').replace('\r', ' ')
    str_2 = "".join(filter(lambda x: x in string.printable, str_1))
    return str_2

    
"""

get_twitter_ids

screen_name_entity: Twitter handle
id_type: specifies whether to get FRIEND or FOLLOWER ids for screen_name_entity
twitter_token: Twython object for accessing Twitter API

returns list containing twitter ids found
if there is an error, returns empty list

"""
def get_twitter_ids(screen_name_entity, id_type, twitter_token):
    
    #start with first page
    cursor = -1
    response = []
    #a cursor value of 0 indicates that there are no more values to gather 
    while cursor != 0:
        try:
            #time.sleep(100)
            if(id_type == FRIEND):
                check_rate_limit({'application':'/application/rate_limit_status','friends':'/friends/ids'}, twitter_token)
                friend_dict = twitter_token.get_friends_ids(screen_name=screen_name_entity, cursor=cursor, count=5000)
                response = response + friend_dict['ids']
                cursor=friend_dict['next_cursor']
                
            elif(id_type == FOLLOWER):
                check_rate_limit({'application':'/application/rate_limit_status','followers':'/followers/ids'}, twitter_token)
                follower_dict = twitter_token.get_followers_ids(screen_name=screen_name_entity, cursor=cursor, count=5000)
                response = response + follower_dict['ids']
                cursor=follower_dict['next_cursor']
                
                    
        except Exception as e:
            print("EXCEPTION!")
            print (e)
            break
    
    return response

"""

get_twitter_info

list_of_vals: list of Twitter identifiers
list_type: specifies type of identifier (ID OR SCREEN_NAME)
twitter_token: Twython object for accessing Twitter API

returns list of dictionaries (where each dictionary contains the information for
each Twitter entity in list_of_vals)
if there is an error, returns empty list

"""       
def get_twitter_info(list_of_vals, list_type, twitter_token):
    num_names = len(list_of_vals)

    twitter_info = []
     
    try:              
        #gather info in groups dictated by Twitter API limit (MAX_RETURN)
        for i in range (0, num_names, MAX_RETURN):
        
            idx_stop=0
            if(i+MAX_RETURN>num_names):
                idx_stop=num_names
            else:
                idx_stop=i+MAX_RETURN
                
            check_rate_limit({'application':'/application/rate_limit_status','users':'/users/lookup'}, twitter_token)
            if(list_type == ID):
               twitter_info = twitter_info + twitter_token.lookup_user(user_id=list_of_vals[i:idx_stop])
            elif (list_type == SCREEN_NAME):
               twitter_info = twitter_info + twitter_token.lookup_user(screen_name=list_of_vals[i:idx_stop])
    
    except Exception as e:
        print("EXCEPTION!")
        print (e)
        
          
    return twitter_info

"""

create_classifier

training_set_file: file containing training data in csv format

EXAMPLE of training_set_file expected format:
"I love cheese",ORG
"I hate juice",NORG
"I enjoy ping pong",ORG
"I don't like football",NORG

returns ERROR if there is an issue
otherwise returns classifier object

"""                    
def create_classifier(training_set_file):
    #setup classifier
   
    try:
        with open(training_set_file, 'r') as fp:
            cl = NaiveBayesClassifier(fp, format="csv")
            return cl
    except FileNotFoundError:
        print("Could not find file: %s" % (training_set_file))
        return ERROR

"""

test_classifier()

testing_set_file: file containing testing data in csv format 
(see example for create_classifier for info on creating testing_set_file)
classifier: a classifier created by calling create_classifier function

returns ERROR if there is an issue

"""
def test_classifier(testing_set_file, classifier):
    try:
        with open(testing_set_file, 'r') as fp:
            print("Classifier Accuracy: %.2f" % classifier.accuracy(fp, format="csv"))
            classifier.show_informative_features(10)
            print("\n")
    except FileNotFoundError:
        print("Could not find file: %s" % (testing_set_file))
        return ERROR
        
"""    
check_rate_limit()

this function should be called prior to any use of the Twitter API
to ensure that a call to the Twitter API will not result in 
exceeding the rate limit 

dict_resources: a dictionary containing the Twitter resources that are about to be used 
the resource is the key and the specific call within that resource family that should
be checked is the corresponding value
for example, dict_resources = {'application':'/application/rate_limit_status', 'users':'/users/lookup', 
                  'friends':'/friends/ids', 'followers':'/followers/ids'}

twitter_token: Twython object for accessing Twitter API                

inspiration from: https://unsupervisedlearning.wordpress.com/category/uncategorized/  

"""               
def check_rate_limit(dict_resources, twitter_token):
    
    #get resources from dict_resources
    resources_to_check = list(dict_resources)
    
    #to be safe, use try
    try:
        
        status = twitter_token.get_application_rate_limit_status(resources = resources_to_check)
        #variable to keep track of total sleep time
        total_time_wait = 0
        
        #check each resource
        for resource in resources_to_check:
            
            #pull out the specific API call within resource family
            status_resource = status['resources'][resource][dict_resources[resource]]
            
            #if there are no more remaining calls, may need to sleep
            if(status_resource['remaining'] <= 0):
                time_to_wait = max(status_resource['reset'] - time.time(), 0) + 10 # addding 10 second pad
                
                #check to see if the total sleep time has already fulfilled the 
                #time to wait for specific API call...if so, no need to sleep
                if(total_time_wait > time_to_wait):
                    continue
                
                print("===============Sleeping %s seconds for %s==============\n" % (str(time_to_wait), dict_resources[resource]))
                for i in trange(int(time_to_wait)):
                    time.sleep(1)
                #add time_to_wait to total
                total_time_wait = total_time_wait + time_to_wait
        
    
    except Exception as e:
        print (e)
        print("In check_rate_limit: sleeping for 15 minutes!")
        for i in trange(15*60):
            time.sleep(1)
        
    return

"""

pull_and_classify()

-pulls Twitter information for all friends or followers of the entity specified
-uses classifier to separate out the friends or followers into two categories
based on their Twitter description fields (ORG and NORG)
-results are written out to tab separated files

screen_name_entity: screen name (or Twitter handle) for entity that information is being pulled from 
entity_to_pull: pulling FRIEND or FOLLOWER information?
classifier: classifier object created through create_classifier()
twitter_token: Twython object for accessing Twitter API

returns list of screen names of all ORGs found
returns ERROR if there is an issue

"""
def pull_and_classify(screen_name_entity, entity_to_pull, classifier, twitter_token):
    
    #list of orgs (with high confidence) found by pulling data from screen_name_entity
    org_handles = []

    #print("=====PULLING TWITTER IDS FOR %s %s=====\n" % (screen_name_entity, entity_to_pull))
    #get ids of twitter entities 
    ids = get_twitter_ids(screen_name_entity, entity_to_pull, twitter_token)
    if(ids == []):
        return ERROR
        
    num_entities_found = len(ids)
    #print("=====FOUND %s %s=====\n" % (str(num_entities_found),entity_to_pull))
    
    #print("=====PULLING TWITTER INFO FOR %s %s=====\n" % (screen_name_entity, entity_to_pull))
    #get info about those twitter entities
    info = get_twitter_info(ids, ID, twitter_token)
    if(info == []):
        return ERROR
        
    #SET UP DIRECTORY AND FILES#############################################################################
    now=datetime.datetime.now()
    day = "%i.%i.%i.txt" % ( now.month, now.day, now.year)
    
    #NAME OUTPUT FILES
    all_data = "%s/%s_twitter_friends_data_%s" % (screen_name_entity, screen_name_entity, day)
    org = "%s/%s_ORG_%s" % (screen_name_entity, screen_name_entity, day)
    norg = "%s/%s_NORG_%s" % (screen_name_entity, screen_name_entity, day)
    
    #MAKE THE DIRECTORY
    os.makedirs(os.path.dirname(all_data), exist_ok=True)
    
    #OPEN FILES
    all_fp = open(all_data, "w")
    org_fp = open(org, "w")
    norg_fp = open(norg, "w")

    #HEADER FIELDS FOR ALL_FP
    all_fields = "classification prob_ORG prob_NORG id screen_name name created_at url followers_count friends_count description location lang extended_url".split()
    twitter_fields = "id screen_name name created_at url followers_count friends_count description location lang".split() 
    all_fp.write(str.join('\t', (all_fields)) + "\n")  
    
    #HEADER FIELDS FOR ORG_FP AND NORG_FP
    org_norg_fields = "prob_ORG screen_name description extended_url".split()
    org_fp.write(str.join('\t', (org_norg_fields)) + "\n")  
    norg_fp.write(str.join('\t', (org_norg_fields)) + "\n")  
    
    print("=====BEGINNING CLASSIFICATION FOR %s's %s (%s)=====\n" % (screen_name_entity, entity_to_pull, str(num_entities_found)))
    #THIS BLOCK WILL LOOP OVER EACH OF THE Twitter entities FOUND AND OUTPUT DATA TO respective FILES#######
    for entry in tqdm(info):
       
        #CREATE EMPTY LIST
        lst = []

        #ADD CLASSIFICATION
        prob_dist = classifier.prob_classify(clean(entry['description']))
        lst.append(str(prob_dist.max()))
        lst.append(str(round(prob_dist.prob("ORG"), 2)))
        lst.append(str(round(prob_dist.prob("NORG"), 2)))
        
        #ADD DATA FOR REST OF THE FIELDS
        for f in twitter_fields:
            str_value = clean(str(entry[f]))
            if(str_value==' '):
                str_value = "None"
            lst.append(str_value)
        
        #NOT EVERY ID WILL HAVE A 'URL' KEY, SO CHECK FOR ITS EXISTENCE WITH IF CLAUSE
        if 'url' in entry['entities']:
            lst.append(clean(str(entry['entities']['url']['urls'][0]['expanded_url'])))
        else:
            lst.append("None")    
        
        row = (str.join('\t', lst))
        all_fp.write(row)
        all_fp.write("\n")
        
        #######SHOULD TWITTER ENTITY BE ADDED TO ORG OR NORG?##################################
        desc = lst[all_fields.index("description")].lower()
        org_norg_lst = [lst[all_fields.index("prob_ORG")], lst[all_fields.index("screen_name")], desc, lst[all_fields.index("extended_url")]]
        row_org_norg = (str.join('\t', org_norg_lst))
        
        #BASED ON PROBABILITY THAT ENTITY IS AN ORG AND WHETHER OR NOT THE DESCRIPTION
        #CONTAINS THE KEYWORDS, PUT ENTITY INTO APPROPRIATE FILE (ORG OR NORG)
        if (round(prob_dist.prob("ORG"), 2) >= ORG_THRESH and 
            (KEYWORD_1_IN in desc or 
             KEYWORD_2_IN in desc)):
            #print("ADDED: ")
            #print(org_norg_lst)
            #print("\n")
            org_fp.write(row_org_norg)
            org_fp.write("\n")
            
            org_handles = org_handles + [lst[all_fields.index("screen_name")]]
            

        else:
            norg_fp.write(row_org_norg)
            norg_fp.write("\n")
    
    all_fp.close()
    org_fp.close()
    norg_fp.close()

    print("\n=====DONE! See generated files in %s folder=====\n" % screen_name_entity)
    return org_handles
    

