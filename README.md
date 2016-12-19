## Synopsis: This project "scrapes" friend or follower information from a Twitter account and classifiers the friends or followers into two broad classes:
organizations that are fighting human trafficking and everyone else

##Requirements:
* Python 3.5
* Need Twitter application app_key, app_secret, oauth_token, oauth_token_secret: http://social-metrics.org/slideshare-tutorial-1/ 
* Must have the following modules installed: 
-twython: https://twython.readthedocs.io/en/latest/
-textblob: https://textblob.readthedocs.io/en/dev/
-tqdm: https://pypi.python.org/pypi/tqdm

##This folder contains the following:
-TwitterClassification.py: An API of sorts that allows for binary classification of Twitter entities based on their description field
-RunTC.py: Python script that demonstrates usage of TwitterClassification.py in identifying organizations that are fighting human trafficking
-testing_set.csv: A csv file containing data used to test classifier
-training_set.csv: A csv file containing data used to create classifier
-dataset_labeled.csv: A csv file containing all data used in testing_set.csv and training_set.csv 

##The two default classes are "ORG" and "NORG"
For the particular dataset included, "ORG" stands for allies or organizations that are fighting human trafficking and providing services to victims (shelter, legal, healthcare, etc.) and "NORG" stands for everyone else.
For exact details on how to create training and testing files, please refer to the textblob guide: https://textblob.readthedocs.io/en/dev/classifiers.html
The training and testing files included are based on manual classification of the friend info pulled from @GblEmancipation.

##Two important constants to modify in RunTC.py
PULL_AND_CLASSIFY_THRESH - how many Twitter entities to pull info from
FRIEND_THRESH - only pull and classify friend info from entities with this many friends or less

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

Thorn_NORG_[DATE].txt
Thorn_ORG_[DATE].txt
Thorn_twitter_friends_data_[DATE].txt

Each of these files are tab separated .txt files. Open in Excel to view contents.
Thorn_NORG_[DATE].txt: data organized under the following columns--probability entity is ORG, name of entity, Twitter handle, extended URL associated with Twitter account if available
Thorn_ORG_[DATE].txt: data organized under the following columns--probability entity is ORG, name of entity, Twitter handle, extended URL associated with Twitter account if available
Thorn_twitter_friends_data_[DATE].txt: This is all data (ORG AND NORG) organized under the following columns--classification, probability entity is ORG, probability entity is NORG,  id, screen_name, name, created_at, url associated with entity, followers_count, friends_count, description associated with entity, location, language, and  extended_url

Assuming that enough ORGs are found, RunTC.py will pivot and keep scraping new ORGs found until hitting the PULL_AND_CLASSIFY_THRESH limit defined at the top of RunTC.py

##Running via cmd window (assuming no requirements in place)
1. Make sure python 3.5.2 is installed. If not, download appropriate version from https://www.python.org/downloads/windows/
If possible download with the web installer. Use the "Install Now" option that includes the pip installer. Be sure to also check the "Add Python 3.5 to PATH."
2. In RunTC.py and TwitterClassification.py, change the first line "#!/usr/bin/enc python" to "#!python3"
3. 
```
py -3.5 -m pip install textblob
```
4. 
```
py -3.5 -m pip install tqdm
```
5. 
```
py -3.5 -m pip install twython
```
6. Navigate to folder containing RunTC.py, TwitterClassification.py and any of the required training/testing files
```
py RunTC.py
```
If you get an error along the lines of "tokenizers/punkt/english.pickle not found":
Go into a python shell, 
```
>>>import nltk
>>>nltk.download('punkt')
```

##TwitterClassification.py API:

##def clean(str_to_clean)-removes new lines, carriage return characters, and unprintable characters. Returns cleaned string. 

##def get_twitter_ids(screen_name_entity, id_type, twitter_token)- 
parameters: screen_name_entity (Twitter handle),  id_type (specifies whether to get FRIEND or FOLLOWER ids for screen_name_entity), twitter_token (Twython object for accessing Twitter API)
returns:  list containing twitter ids found (no error) or empty list (error)

##def get_twitter_info(list_of_vals, list_type, twitter_token)- 
parameters: list_of_vals (list of Twitter identifiers), list_type (specifies type of identifier?ID OR SCREEN_NAME), twitter_token (Twython object for accessing Twitter API). 
returns: list of dictionaries, where each dictionary contains the information for each Twitter entity in list_of_vals (no error) or
empty list (error)

##def create_classifier(training_set_file)

##def test_classifier(testing_set_file, classifier)

##check_rate_limit(dict_resources, twitter_token)
This function should be called prior to any use of the Twitter API
to ensure that a call to the Twitter API will not result in 
exceeding the rate limit.
parameters: 
1. dict_resources, a dictionary containing the Twitter resources that should be checked.
The resource is the key and the specific call within that resource family that should
be checked is the corresponding value. For example,
dict_resources = {'application':'/application/rate_limit_status', 'users':'/users/lookup', 
'friends':'/friends/ids', 'followers':'/followers/ids'}
2. twitter_token: Twython object for accessing Twitter API                

##def pull_and_classify(screen_name_entity, entity_to_pull, classifier, twitter_token)-
Pulls Twitter information for all friends or followers of the entity specified, uses classifier to separate out the friends or followers into two categories based on their Twitter description fields, and writes results to tab separated files.
parameters: screen_name_entity (Twitter handle for entity that information is being pulled from),  entity_to_pull (pulling FRIEND or FOLLOWER information?), classifier (classifier object created through create_classifier()), twitter_token (Twython object for accessing Twitter API)
returns: list of screen names of all ORGs found (no error) or ERROR (error)

##Next Steps:
-Find a way to save and reload classifier (to eliminate wait time in re-creating classifier)
-Work on way to automatically update classifier based on new information being gathered/increase accuracy of classifier (currently, keywords at top of TwitterClassification.py are helpful but rather limiting, resulting in a large amount of false negatives)
-Have a limit on amount of friends/followers that will be classified for a given Twitter Entity (probably do not want to pull all the 94,000 friends of IJM...!)
-Find a way to only write entities to ORG files that have not been recorded yet
-Read in Twitter tokens from a config file and perform verification
-Get script to continue running even when computer sleeps
-Cleaner way to exit program (besides Control-C!)


