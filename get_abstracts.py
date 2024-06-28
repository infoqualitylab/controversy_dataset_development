import requests, json, pandas as pd, numpy as np


apikey = ""  #<<< Your API key
insttoken = ""  #<<< Your InstTokn

input_file = "" #<<< specify input filename
with open(input_file,encoding = 'utf-8') as fp:
    data300 = pd.read_csv(fp,header = 0)


missing_dois = 0
missing_scopus = 0
missing_both = 0



for idx in data300.index:
    abstract_og = data300.loc[idx,'abstract']
    abstract = ""
    missing_doi_flag = False
    if str(abstract_og) == 'nan':
        #print(abstract_og)
        one_input = data300.loc[idx,'doi']
        if str(one_input) == 'nan':
            print(one_input)
            missing_dois += 1
            missing_doi_flag = True
        else:
            abstract = ""
            doi = one_input.split('org')[1][1:]
            request_url = "https://api.elsevier.com/content/abstract/doi/" + doi
            response = requests.get(request_url, headers={'Accept': 'application/json','X-ELS-APIKey': apikey,'X-ELS-Insttoken': insttoken})
            get_result = response.content
            data = json.loads(get_result)
            if "abstracts-retrieval-response" in data:
                abstract = data["abstracts-retrieval-response"]["coredata"]["dc:description"]
                data300.loc[idx,'abstract'] = abstract
                print("success!")
            else:
                print(data)
                missing_scopus += 1
                data300.loc[idx,'abstract'] = ""
                if missing_doi_flag:
                    missing_both += 1

            
  
output_file = "" #<<< specify output filename  
with open(output_file,'w',encoding = 'utf-8',newline = "") as outfp:
    data300.to_csv(outfp)