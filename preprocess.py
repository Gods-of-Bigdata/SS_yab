# Copyright (C) 2020  Gods of Bigdata
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import re
import json
import math 
import string
from glob import glob
from hazm import POSTagger
from hazm import Normalizer
from hazm import stopwords_list
from hazm import word_tokenize, sent_tokenize
from nltk.util import ngrams

#%%
class sahamyab_preprocess():
    def __init__(self,
                 corpus_path='resources/corpus.json',
                 symbols_json_path='resources/symbols.json',
                 persian_lang_path = 'resources/persian_lang.json',
                 postagger_model_path = 'resources/postagger.model',
                 max_keyword_num=10,min_keyword_occurrences=0.01,expand_corpus=False):
        self.postagger_model_path = postagger_model_path
        self.symbols_json_path = symbols_json_path
        self.corpus_path = corpus_path
        self.corpus = {}
        self.docs_num = 0 
        self.expand_corpus = expand_corpus
        
        if self.corpus_path is not None:
            with open(corpus_path, encoding='utf-8') as json_file:
                corpus =  json.load(json_file)   
            self.corpus = corpus['corpus']
            self.docs_num = corpus['docs_num'] 
            
        with open(symbols_json_path, encoding='utf-8') as json_file:
            data = json.load(json_file)
        lst = list(data.values())
        self.all_symbols_list = [item for sublist in lst for item in sublist]
        
        with open(persian_lang_path, encoding='utf-8') as json_file:
            persian_lang = json.load(json_file)
        
        self.epic_keywords = persian_lang['epic_keywords']
        self.punctuations = persian_lang['punctuations']
        self.persian_alphabet = persian_lang['persian_alphabet']                              
        self.stop_words = persian_lang['stop_words']
        
        self.tagger = POSTagger(model=self.postagger_model_path)
        self.normalizer = Normalizer()
        self.max_keyword_num = max_keyword_num
        self.min_keyword_occurrences = min_keyword_occurrences
   

    def sort_corpus(self):
        self.corpus = {k: v for k, v in sorted(self.corpus.items(),
                                               key=lambda item: item[1],reverse=True)}
        return self.corpus
    
    def save_corpus(self,save_path):
        with open(save_path, 'w', encoding='utf8') as f: 
            corpus = {'docs_num':self.docs_num,'corpus':self.corpus}
            json.dump(corpus, f, ensure_ascii=False, indent=4, separators=(',', ': '))
    
    def get_ngrams(self,words, n):
        n_grams = ngrams(words, n)
        return [ ' '.join(grams) for grams in n_grams]

    def get_symbols(self,words):
        syms = []
        hashtags = []
        for word in words:
            if '#' in word:
                word = word.replace('#','')
                hashtags.append(word)
                if word in self.all_symbols_list:
                    syms.append(word)
            else:
                if word in self.all_symbols_list:
                    syms.append(word)
                

                
        return syms,hashtags

    def calculate_tfidf(self,word,count_in_content,content_len):
        
        tf = count_in_content / content_len
        idf = math.log(self.docs_num / self.corpus.get(word,1)) + 1
        return tf*idf
    
    def get_keywords(self,candidate_words,content_len):
        if self.expand_corpus:
            self.docs_num += 1
        tfidf_list = []
        keywords = []

        for word in list(set(candidate_words)):
            if self.expand_corpus:
                self.corpus[word] = self.corpus.get(word,0)+ 1
            if word in self.epic_keywords:
                keywords.append(word)
            else:
                count_in_content = candidate_words.count(word)
                tfidf = self.calculate_tfidf(word,count_in_content,content_len)
                if  self.corpus.get(word,0) > self.min_keyword_occurrences*self.docs_num:
                    tfidf_list.append((word,tfidf))
        
        sorted_keywords = sorted(tfidf_list,key = lambda x: x[1],reverse=True) 
        keywords += ([kywrd.replace('#','')
                      for (kywrd,score) in sorted_keywords
                      if score>0.1])
        if len(keywords) == 0 :
            return [kywrd for (kywrd,score) in sorted_keywords[:1]]
        return keywords[:self.max_keyword_num]
        
        
    def extract_metadata(self,tweet):
        important_words = []
        syms = []
        hashtags = []
        content_len = 0
        
        content = self.normalizer.normalize(tweet['content'])
        if 'های وب' in content: syms.append('های_وب')
        sentences = sent_tokenize(content)
        for sentence in sentences:
            sentence = sentence.translate(str.maketrans('', '', self.punctuations))
    
            words = word_tokenize(sentence)
            content_len += len(words)
            sent_syms,sent_hashs = self.get_symbols(words)
            syms += sent_syms
            hashtags += sent_hashs
            tags =  self.tagger.tag(words)
            verbs = [word for (word,role) in tags if role=='V']
            
            filtered_words = ([word.replace('#','') 
                               for word in words if word.replace('#','')  not in self.stop_words
                               and word.replace('#','')  not in verbs
                               and set(word.replace('#','') ).intersection(self.persian_alphabet)
                               and len(word.replace('#','')) > 1])
            important_words += filtered_words
        syms = list(set(syms))
        hashtags = list(set(hashtags))
        bigrams = self.get_ngrams(important_words,2)
        trigrams = self.get_ngrams(important_words,3)
        candidate_words = hashtags + syms + important_words + bigrams + trigrams
        keywords = self.get_keywords(candidate_words,content_len)
        return keywords,syms,hashtags
    
    def get_compelete_json(self,tweet):
        content_and_metadata = {}
        keywords,symbols,hashtags = self.extract_metadata(tweet)
        content_and_metadata['id'] = tweet['id']
        content_and_metadata['sendTime'] = tweet['sendTime']
        content_and_metadata['sendTimePersian'] = tweet['sendTimePersian']
        content_and_metadata['hashtags'] = hashtags
        content_and_metadata['keywords'] = keywords
        content_and_metadata['symbols'] = symbols
        content_and_metadata['image'] = tweet['imageUid'] if 'imageUid' in tweet.keys() else []
        content_and_metadata['senderUsername'] =  tweet['senderUsername']
        content_and_metadata['senderName'] =  tweet['senderName']
        content_and_metadata['content'] =  tweet['content']
        return content_and_metadata
    


