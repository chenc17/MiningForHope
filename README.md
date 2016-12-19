## Synopsis:  <br />
This project "scrapes" friend or follower information from a Twitter account and classifies the friends or followers into two broad classes:  organizations that are fighting human trafficking and everyone else

##Requirements:
* Python 3.5
* Need Twitter application app_key, app_secret, oauth_token, oauth_token_secret:  <br />
http://social-metrics.org/slideshare-tutorial-1/ 
* Must have the following modules installed:  <br />
-twython: https://twython.readthedocs.io/en/latest/  <br />
-textblob: https://textblob.readthedocs.io/en/dev/  <br />
-tqdm: https://pypi.python.org/pypi/tqdm  <br />

##Description of Files
-TwitterClassification.py: An API of sorts that allows for binary classification of Twitter entities based on their description field  <br />
-RunTC.py: Python script that demonstrates usage of TwitterClassification.py in identifying organizations that are fighting human trafficking  <br />
-testing_set.csv: A csv file containing data used to test classifier  <br />
-training_set.csv: A csv file containing data used to create classifier  <br />
-dataset_labeled.csv: A csv file containing all data used in testing_set.csv and training_set.csv   <br />

##The two default classes are "ORG" and "NORG"
For the particular dataset included, "ORG" stands for allies or organizations that are fighting human trafficking and providing services to victims (shelter, legal, healthcare, etc.) and "NORG" stands for everyone else.  <br />
For exact details on how to create training and testing files, please refer to the textblob guide: https://textblob.readthedocs.io/en/dev/classifiers.html  <br />
The training and testing files included are based on manual classification of the friend info pulled from @GblEmancipation.  <br />

##TO GET STARTED, CREATE TWITTER TOKENS AND ADD TO RUNTC.PY (line 63)		
twitter=Twython(app_key='APP KEY HERE',
      app_secret='APP SECRET HERE',
      oauth_token='OAUTH TOKEN HERE',
      oauth_token_secret='OAUTH TOKEN SECRET HERE')  
      
##Running via terminal (assuming all requirements are in place):
Via the terminal navigate to the folder containing the source code. Run RunTC.py: 
```
python ./RunTC.py
```
Enter a Twitter handle at the prompt (suggest that you enter the handle for an organization that is known to be following other organizations fighting human trafficking...i.e. Thorn and not Polaris)
```
Twitter handle: Thorn
```
By default, RunTC.py will scrape all friend information for Thorn and create a folder with the 
following files:

Thorn_NORG_[DATE].txt <br />
Thorn_ORG_[DATE].txt <br />
Thorn_twitter_friends_data_[DATE].txt <br />

Each of these files are tab separated .txt files. Open in Excel to view contents. <br />
Thorn_NORG_[DATE].txt: data organized under the following columns--probability entity is ORG, name of entity, Twitter handle, extended URL associated with Twitter account if available <br />
Thorn_ORG_[DATE].txt: data organized under the following columns--probability entity is ORG, name of entity, Twitter handle, extended URL associated with Twitter account if available <br />
Thorn_twitter_friends_data_[DATE].txt: This is all data (ORG AND NORG) organized under the following columns--classification, probability entity is ORG, probability entity is NORG,  id, screen_name, name, created_at, url associated with entity, followers_count, friends_count, description associated with entity, location, language, and  extended_url <br />

Assuming that enough ORGs are found, RunTC.py will pivot and keep scraping new ORGs found until hitting the PULL_AND_CLASSIFY_THRESH limit defined at the top of RunTC.py

##Running via cmd window (assuming no requirements in place)
* Make sure python 3.5.2 is installed. If not, download appropriate version from https://www.python.org/downloads/windows/ <br />
If possible download with the web installer. Use the "Install Now" option that includes the pip installer. Be sure to also check the "Add Python 3.5 to PATH."
* In RunTC.py and TwitterClassification.py, change the first line "#!/usr/bin/enc python" to "#!python3"
```
py -3.5 -m pip install textblob
```
```
py -3.5 -m pip install tqdm
```
```
py -3.5 -m pip install twython
```
* Navigate to folder containing RunTC.py, TwitterClassification.py and any of the required training/testing files
```
py RunTC.py
```
If you get an error along the lines of "tokenizers/punkt/english.pickle not found": <br />
In a Python shell, <br />

```
>>>import nltk
>>>nltk.download('punkt')
```

##Two important constants to modify in RunTC.py
PULL_AND_CLASSIFY_THRESH - how many Twitter entities to pull info from <br />
FRIEND_THRESH - only pull and classify friend info from entities with this many friends or less <br />

##TwitterClassification.py "API":

##clean(str_to_clean)
removes new lines, carriage return characters, and unprintable characters. Returns cleaned string.  <br />

##get_twitter_ids(screen_name_entity, id_type, twitter_token)
parameters: screen_name_entity (Twitter handle),  id_type (specifies whether to get FRIEND or FOLLOWER ids for screen_name_entity), twitter_token (Twython object for accessing Twitter API) <br />
returns:  list containing twitter ids found (no error) or empty list (error) <br />

##get_twitter_info(list_of_vals, list_type, twitter_token)
parameters: list_of_vals (list of Twitter identifiers), list_type (specifies type of identifier?ID OR SCREEN_NAME), twitter_token (Twython object for accessing Twitter API). <br />
returns: list of dictionaries, where each dictionary contains the information for each Twitter entity in list_of_vals (no error) or empty list (error) <br />

##create_classifier(training_set_file)

##test_classifier(testing_set_file, classifier)

##check_rate_limit(dict_resources, twitter_token)
This function should be called prior to any use of the Twitter API
to ensure that a call to the Twitter API will not result in 
exceeding the rate limit. <br />
parameters: <br />
1. dict_resources, a dictionary containing the Twitter resources that should be checked.
The resource is the key and the specific call within that resource family that should
be checked is the corresponding value. For example, <br />
dict_resources = {'application':'/application/rate_limit_status', 'users':'/users/lookup', 
'friends':'/friends/ids', 'followers':'/followers/ids'} <br />
2. twitter_token: Twython object for accessing Twitter API   <br />              

##pull_and_classify(screen_name_entity, entity_to_pull, classifier, twitter_token)-
Pulls Twitter information for all friends or followers of the entity specified, uses classifier to separate out the friends or followers into two categories based on their Twitter description fields, and writes results to tab separated files. <br />
parameters: screen_name_entity (Twitter handle for entity that information is being pulled from),  entity_to_pull (pulling FRIEND or FOLLOWER information?), classifier (classifier object created through create_classifier()), twitter_token (Twython object for accessing Twitter API) <br />
returns: list of screen names of all ORGs found (no error) or ERROR (error) <br />

##Next Steps:
-Find a way to save and reload classifier (to eliminate wait time in re-creating classifier) <br />
-Work on way to automatically update classifier based on new information being gathered/increase accuracy of classifier (currently, keywords at top of TwitterClassification.py are helpful but rather limiting, resulting in a large amount of false negatives) <br />
-Find a way to only write entities to ORG files that have not been recorded yet <br />
-Read in Twitter tokens from a config file and perform verification <br />
-Get script to continue running even when computer sleeps <br />
-Cleaner way to exit program (besides Control-C!) <br />


