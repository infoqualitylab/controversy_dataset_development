import stanza, gensim, string, json, pandas as pd
from gensim.models import Word2Vec
from sklearn.cluster import KMeans


def get_POS_lists(headlines):
    '''
    some code in this function is referenced from:
    https://stanfordnlp.github.io/stanza/depparse.html
    '''
    nounlist = set()
    verblist = set()
    
    stanza.download('en')
    nlp = stanza.Pipeline(lang = 'en')
    
    arclistlist = []
    
    for i in range(len(headlines)):
        doc = nlp(headlines[i])
        
        arclist = []
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos in ["NOUN","PRON","PROPN"]:
                    nounlist.add(word.text)
                if word.upos == "VERB":
                    verblist.add(word.text)
                    
    return list(nounlist),list(verblist)
    
def train_sim_model(lists):
    data = []
    #go through word lists, make data out of them
    for wordlist in lists:
        row = []
        for word in wordlist:
            word = word.lower().strip(string.punctuation)
            if len(word) > 0:
                row.append(word)
        if len(row) > 0:
            print(row)
            data.append(row)
            
    #train model on list of tokens, return the model      
    sim_model = Word2Vec(data, min_count = 1, vector_size = 100, window = 5)
    
    return sim_model
    
           
def get_sim_mat(model,words):
    '''
    some code in this function is referenced from:
    https://www.geeksforgeeks.org/python-word-embedding-using-word2vec/
    https://radimrehurek.com/gensim/models/word2vec.html
    '''
    simmat = []
    #make and return similarity matrix of given words in a list using existing model
    GetRidOf = []
    for word in words:
        word = word.lower().strip(string.punctuation).strip()
        row = []
        for word2 in words:
            word2 = word2.lower().strip(string.punctuation)
            try:
                row.append(model.wv.similarity(word,word2))
            except:
                print(word)
                print(word2)
                if word2 not in GetRidOf:
                    GetRidOf.append(word2)
                continue
        simmat.append(row)
    print(GetRidOf)
        
    return pd.DataFrame(data = simmat, index = words, columns = words)
    
def get_groups(sim_mat):
    '''
    some code in this function is referenced from: 
    https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans
    https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans.predict
    '''
    kmeans = KMeans(n_clusters=4, random_state=0).fit(sim_mat.values)
    
    groups = {}
    predictions = kmeans.predict(sim_mat)
    for i in range(len(predictions)):
        groupnum = str(predictions[i])
        if groupnum not in groups:
            groups[groupnum] = []
        groups[groupnum].append(str(sim_mat.columns[i]))
        
    return groups

def main():
    input_file = "" #<<<specify your input file
    
    keywords = []
    with open(input_file, encoding = "utf-8") as fp:
        for line in fp.readlines():
            line_ = " ".join(line.split("|")).strip()
            line_ = " ".join(line_.split(",")).strip()
            keywords.extend(line_.split())
    keywords = list(set(keywords))
    print(keywords)
    if '' in keywords:
        print("empty in keywords")
    if " " in keywords:
        print("space in keywords")


    training_data = "Improved Training Data (Abstract + Title + keywords).txt"
    trainingData = []
    with open(training_data, encoding = "utf-8") as fp:
        for line in fp.readlines():
            trainingData1 = " ".join(line.split("|"))
            trainingData2 = trainingData1.split()
            trainingData.extend(trainingData2)
        print(trainingData)
    if '' in trainingData:
        print("empty in train")
    if " " in trainingData:
        print("space in train")

    sim_model = train_sim_model([trainingData])
    
    keywords_sim = get_sim_mat(sim_model, keywords)
    
    keywords_group = get_groups(keywords_sim)
    
    #make general tag for each group - save groups for later use
    with open("keyword_groups.txt","w",encoding = "utf-8") as fp:
        fp.write(json.dumps(keywords_group, indent = 4))

if __name__ == "__main__":
    main()



