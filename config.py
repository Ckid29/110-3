import pymongo
import certifi

con_str = "mongodb+srv://RinCaspers:n3bMPCNb19CxZ8iQ@cluster0.d1y5x.mongodb.net/?retryWrites=true&w=majority"


client = pymongo.MongoClient(con_str, tlsCAFile=certifi.where())

db = client.get_database("Videogames")
