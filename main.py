#lets write a simple script to get 20 words and their frequency percentage with highst frequency in an english wikipedia article.
#applications are in recommender systems, chatbots, sentiment analysis, market research etc.

#beautiful soup is a python library for pulling data out of HTML and XML files.
from bs4 import BeautifulSoup

#Requests is HTTP library for pulling pushing and authenticating
import requests

#re lets you do regular expression operations (special text string for describing a search pattern, find and replacce)
import re

#operator module exports a set of efficient functions corresponding to intrinsic operators of python(comparison, addition, greater than, less than)
import operator

#parses json, formats it
import json

#tabulate module provides just one function tabulate which takes a list of lists or another tabular data type as first argument
#and outputs a nicely formatted plaun-text table
from tabulate import tabulate

#system calls deals with user arguments
import sys

#list of common stop words
from stop_words import get_stop_words

#get the words
def getWordList(url):
  word_list = []
  
  #raw data
  source_code = requests.get(url)
  
  #convert to text
  plain_text = source_code.text
  
  #lxml format
  soup = BeautifulSoup(plain_text, 'lxml')
  
  #finds the words in paragrapgh tag
  for text in soup.findAll('p'):
    if text.text is None:
      continue
    
    #content
    content = text.text
    
    #lowercase and split to an array
    words = content.lower().split()
    
    #for each word
    for word in words:
      
      #remove non-chars
      cleaned_word = clean_word(word)
      
      #if there is still something there, add it to our word list
      if len(cleaned_word) > 0:
        word_list.append(cleaned_word)
  return word_list

#clean word with regex
def clean_word(word):
  cleaned_word = re.sub('[^A-Za-z]+', '', word)
  return cleaned_word
  
def createFrequencyTable(word_list):
  
  #word count
  word_count = {}
  
  for word in word_list:

    #index  is the word
    if word in word_count:
      word_count[word] += 1
    else:
      word_count[word] = 1
  return word_count

#remove stop words
def remove_stop_words(frequency_list):
  stop_words = get_stop_words('en')
  
  temp_list = []
  
  for key,value in frequency_list:
    if key not in stop_words:
      temp_list.append([key, value])
  return temp_list

#access wiki API. json format. query it for data. search type. shows list of possibilities.
wikipedia_api_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
wikipedia_link = "https://en.wikipedia.org/wiki/"

#if the search word is too small, throws error
if (len(sys.argv) < 2):
  print("enter valid string")
  exit()
  
#get the search word
string_query = sys.argv[1]

#to remove stop words or not
if (len(sys.argv) > 2):
  search_mode = True
else:
  search_mode = False
  
#create our URL
url = wikipedia_api_link + string_query

#try-except block,simple way to deal with exceptions, great for HTTP requests
try:
  
  #use requests to retrieve raw data from wiki API URL we just constructed
  response = requests.get(url)
  
  #format that data as a json directory
  data = json.loads(response.content.decode("utf-8"))
  
  #page title, first option, show this in web browser
  wikipedia_page_tag = data['query']['search'][0]['title']
  
  #get actual wiki page based on retrieved title
  url = wikipedia_link + wikipedia_page_tag
  
  #get list of words from that page
  page_word_list = getWordList(url)
  
  #create table of word counts, dictionary
  page_word_count = createFrequencyTable(page_word_list)
  
  #sort the table by the frequency count
  sorted_word_frequency_list = sorted(page_word_count.items(), key=operator.itemgetter(1), reverse = True)
  
  #remove stop words if user specified
  if(search_mode):
    sorted_word_frequency_list = remove_stop_words(sorted_word_frequency_list)
    
  #sum the total words to calculate frequency
  total_words_sum = 0
  for key,value in sorted_word_frequency_list:
    total_words_sum = total_words_sum + value
  
  #just get the top 20 words
  if len(sorted_word_frequency_list) > 20:
    sorted_word_frequency_list = sorted_word_frequency_list[:20]
  
  #create final list list which contains words, frequency, percentage
  final_list = []
  for key,value in sorted_word_frequency_list:
    percentage_value = float(value * 100)/total_words_sum
    final_list.append([ key, value, round(percentage_value, 4) ])
    
  #headers before table
  print_headers = ['Word', 'Frequency', 'Frequency Percentage']
  
  #print the table with tabulate
  print(tabulate(final_list, headers = print_headers, tablefmt='orgtbl'))
  
#throw an exception in case it breaks
except requests.exceptions.Timeout:
  print("The server didn't respond, please try again later.")

    
  
