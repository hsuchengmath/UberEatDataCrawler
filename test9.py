









import pymongo
StageMongodbUrl = 'mongodb://140.116.52.210:27018/'
collection_name = 'MenuTEST'
db_name = 'MenuTEST'
myclient = pymongo.MongoClient(StageMongodbUrl) 
mydb = myclient[db_name] 
mycol = mydb[collection_name] 
#mydict = {'MongodbUrl' : StageMongodbUrl, 'db_name' : db_name, 'db_name' : db_name, 'return' : 200}
#mycol.insert_one(mydict)  
# test


FoodNameList = []
for x in mycol.find():
    FoodNameList.append(x['FoodName'])
print(set(FoodNameList))



