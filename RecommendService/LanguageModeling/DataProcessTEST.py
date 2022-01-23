

import random
import pymongo
from tqdm import tqdm
StageMongodbUrl = 'mongodb://140.116.52.210:27018/'


def StripHtml(data):
    import re
    p = re.compile(r'<.*?>')
    return p.sub('', data)
 


def StripPunctuation(data):
    import string
    p = data.strip(string.punctuation)
    return p


def PttArticleDataClean(text=str, data_type=str, max_charator_length=int):
    if data_type == 'title':
        # filter main title by "[xxx]"
        main_title = text.split(']')[1:]
        if len(main_title) == 1:
            main_title = main_title[0]
        else:
            main_title = ' '.join(main_title)
        if len(main_title) >= max_charator_length:
            main_title = ''
        return main_title

    elif data_type == 'article':
        # remove html
        text = StripHtml(data=text)

        # split by \n\n (we find \n\n, it means one of paragraph)
        sentence_list = text.split('。')
        sentence_list_deep = []
        for sentence in sentence_list:
             sentence_list_deep += sentence.split('\n\n')

        # remove pununctuation for each sentence
        sentence_list_wo_pun = list()
        for i in range(len(sentence_list_deep)):
            sentence = StripPunctuation(data=sentence_list_deep[i]).strip()
            if max_charator_length > len(sentence) >= 2:
                sentence_list_wo_pun.append(sentence)
        return sentence_list_wo_pun



def MaskAnnotationLayer(sent=str, mask_prob=float):
    chr_num = len(sent)
    return random.sample([i for i in range(chr_num)], int(chr_num * mask_prob))



 

def CollectCorpusData(config=dict): 
    db_name = config['db_name']
    collection_name = config['collection_name']
    myclient = pymongo.MongoClient(StageMongodbUrl) 
    mydb = myclient[db_name] 
    mycol = mydb[collection_name] 
    ArticleList = []
    for x in mycol.find():
        data = {'title':x['title'], 'content':x['content']}
        ArticleList.append(data)
    return ArticleList



def DataProcessTEST(config=dict):

    organic_data_list, train_data = [], []
    
    ArticleList = CollectCorpusData(config=config)
    ArticleList = ArticleList[4:]
    print(len(ArticleList))

    for i in tqdm(range(len(ArticleList))):
        title_content = ArticleList[i]
        title = title_content['title']
        title = PttArticleDataClean(text=title, data_type='title', max_charator_length=config['max_charator_length'])
        content = title_content['content']
        sentence_list = PttArticleDataClean(text=content, data_type='article', max_charator_length=config['max_charator_length'])
        organic_data_list.append([title] + sentence_list)

    for i in tqdm(range(len(organic_data_list))):
        organic_data = organic_data_list[i]
        for j in range(len(organic_data)-1):
            # positive data
            train_data.append([organic_data[j], organic_data[j+1], 1, MaskAnnotationLayer(sent=organic_data[j], mask_prob=config['mask_prob'])])
            # negative data
            neg_index = random.sample(list(set(range(len(organic_data))) - {j+1}), 1)[0]
            train_data.append([organic_data[j], organic_data[neg_index], 0, MaskAnnotationLayer(sent=organic_data[j], mask_prob=config['mask_prob'])])
    print('----BasicInfo----')
    print('data number : ', len(train_data))
    return train_data

''' 
example_dataset = [['肯德基好好吃', '肯德基', 1] ,['好吃', '吃', 0]]
'''

if __name__ == '__main__':

    config = \
        {
        'num_labels' : 2, 
        'import_lm_name' : "bert-base-chinese", 
        'unfreeze_layer' : ['layer.11', 'bert.pooler','out.'],
        'hidden_size' : 768,
        'hidden_dropout_prob' : 0.1,
        'epoch' : 1,
        'learning_rate': 1e-5,
        'batch_size' : 128,
        'max_charator_length' : 512,
        'db_name' : 'PttCorpus-Food',
        'collection_name' : 'PttCorpus'
        }
    train_data = DataProcessTEST(config=config)
    max_len = []
    for data in train_data:
        max_len.append(len(data[0]))
        max_len.append(len(data[1]))
    print(max(max_len))