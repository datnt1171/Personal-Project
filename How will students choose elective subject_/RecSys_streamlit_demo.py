# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 14:34:08 2023

@author: datnt
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import KeyedVectors

# import data
df_graph=pd.read_csv(r'D:\2023_2024\RecommenderSystem\DoAn_RecSys\dataset\df_graph.csv')
df_test = pd.read_csv(r'D:\2023_2024\RecommenderSystem\DoAn_RecSys\dataset\df_test.csv')
    
B_embedded = KeyedVectors.load(r"D:\2023_2024\RecommenderSystem\DoAn_RecSys\model_embedding\node2vec.wordvectors", mmap='r')
    
df_Content_MH =pd.read_csv(r'D:\2023_2024\RecommenderSystem\DoAn_RecSys\dataset\ChiTietMonHoc.csv')
MH_Content_embeddings = np.load(r"D:\2023_2024\RecommenderSystem\DoAn_RecSys\model_embedding\MH_Content_embeddings.npy")
MSSV_Content_embeddings=np.load(r"D:\2023_2024\RecommenderSystem\DoAn_RecSys\model_embedding\MSSV_Content_embeddings.npy")
    
cf_preds_df = pd.read_csv(r'D:\2023_2024\RecommenderSystem\DoAn_RecSys\model_embedding\cf_preds_df.csv')
cf_preds_df.set_index('Ma_MH', inplace=True)

gnn_test_df = pd.read_csv(r"D:\2023_2024\RecommenderSystem\DoAn_RecSys\model_embedding\gnn_test_df.csv")
# Graph Recommender
node_embeddings = {node_id: B_embedded[node_id] for node_id in B_embedded.index_to_key}

def get_rated_items(user_id):
  df=df_graph
  return set(df[df['MSSV'] == user_id]['Ma_MH'])

def get_user_embedding_graph(user_id):
    embeddings = node_embeddings
    return embeddings[str(user_id)]

def calculate_similarities_graph(user_id):

    df=df_graph
    embeddings=node_embeddings

    rated_items = get_rated_items(user_id)
    user_embedding = get_user_embedding_graph(user_id)

    item_similarities = []
    for item_id in set(df['Ma_MH']):
      if item_id not in rated_items:
        item_embedding = embeddings[str(item_id)]
        similarity = cosine_similarity([user_embedding], [item_embedding])[0][0]
        item_similarities.append((item_id, similarity))

    return item_similarities

def recommend_items_graph(user_id, num_items=5):

  item_similarities = calculate_similarities_graph(user_id)

  recommended_items = sorted(item_similarities, key=lambda x: x[1], reverse=True)[:num_items]
  recommended_items_df = pd.DataFrame(recommended_items, columns=['Ma_MH','cosine_similarity'])
  return recommended_items_df

a= recommend_items_graph(16520198)

# Content-Based Recommender
tuples_MH = [(key, value)
          for i, (key, value) in enumerate(zip(list(df_Content_MH['Mã MH']), MH_Content_embeddings))]
dict_MH = dict(tuples_MH)

df_join = df_graph.merge(df_Content_MH, how='left',left_on='Ma_MH',right_on='Mã MH')
df_join=df_join[['MSSV','Ma_MH','Tên MH','Tóm tắt môn học']]
df_join['Tóm tắt môn học']=df_join['Tóm tắt môn học'].fillna('')
df_join['Tên MH']=df_join['Tên MH'].fillna('')

MSSV_profile = df_join.groupby('MSSV')[['Tóm tắt môn học','Tên MH']].agg(lambda x: ', '.join(x)).reset_index()
tuples_SV = [(key, value)
          for i, (key, value) in enumerate(zip(list(MSSV_profile['MSSV']), MSSV_Content_embeddings))]
dict_SV = dict(tuples_SV)

def get_MSSV_embedding(user_id):
  embeddings = dict_SV
  return embeddings[user_id]

def get_MH_embedding(user_id):
  embeddings = dict_MH
  return embeddings[user_id]

def calculate_similarities_CB(user_id):
    df=df_graph

    rated_items = get_rated_items(user_id)
    user_embedding = get_MSSV_embedding(user_id)

    item_similarities = []
    for item_id in set(df['Ma_MH']):
        if item_id not in rated_items:
          try:
            item_embedding = get_MH_embedding(str(item_id))
            similarity = cosine_similarity([user_embedding], [item_embedding])[0][0]
            item_similarities.append((item_id, similarity))
          except:
            item_similarities.append((item_id, 0))

    return item_similarities

def recommend_items_CB(user_id, num_items=5):

    item_similarities = calculate_similarities_CB(user_id)

    recommended_items = sorted(item_similarities, key=lambda x: x[1], reverse=True)[:num_items]
    recommended_items_df = pd.DataFrame(recommended_items, columns = ['Ma_MH','cosine_similarity'])
    return recommended_items_df


b= recommend_items_CB(16520198)

# Collaborative Filtering

def recommend_items_CF(user_id, num_items=5):

    rated_items = get_rated_items(user_id)

    item_similarities = cf_preds_df[str(user_id)].drop(labels=rated_items) \
                        .sort_values(ascending = False).head(num_items)

    item_similarities_df = pd.DataFrame(item_similarities)
    item_similarities_df.reset_index(inplace=True)
    item_similarities_df.columns = ['Ma_MH','cosine_similarity']
    return item_similarities_df


c=recommend_items_CF(16520198)

# Hybrid Recommender
def recommend_items_hybrid(user_id, num_items = 5):

  num_items_multiple = num_items*2
  CB_pred = recommend_items_CB(user_id,num_items_multiple)
  CF_pred = recommend_items_CF(user_id,num_items_multiple)
  graph_pred = recommend_items_graph(user_id,num_items_multiple)

  CB_pred['cosine_similarity'] = CB_pred['cosine_similarity']/20
  CF_pred['cosine_similarity'] = CF_pred['cosine_similarity']/2
  # concat recommneded items of all model
  df_concat = pd.concat([CB_pred,CF_pred,graph_pred])

  # if a subject is recommended by more model, it will have higher weight
  temp1=df_concat['Ma_MH'].value_counts().rename_axis('Ma_MH').reset_index(name='counts')
  temp2=temp1.merge(df_concat, how='left',on='Ma_MH')
  temp3=temp2.groupby("Ma_MH")['cosine_similarity'].sum()
  temp4=temp3.rename_axis('Ma_MH').reset_index(name='cosine_similarity')
  temp4 = temp4.merge(temp1[['Ma_MH','counts']],on='Ma_MH')
  temp5=temp4.sort_values(by=['counts','cosine_similarity'],ascending=False)
  min_temp5 = temp5['cosine_similarity'].min()
  max_temp5 = temp5['cosine_similarity'].max()
  temp5['cosine_similarity'] = (temp5['cosine_similarity']-min_temp5)/(max_temp5-min_temp5)
  df_mixed = temp5.head(5)
  df_mixed = df_mixed[['Ma_MH','cosine_similarity']]


  return df_mixed

d = recommend_items_hybrid(16520198)
from sentence_transformers import SentenceTransformer
SBert = SentenceTransformer('bert-base-nli-mean-tokens')

def recommend_items_from_builder(user_input, num_items=5):
    
    tempp1 = user_input.upper().split()
    tempp2 = df_Content_MH[df_Content_MH['Mã MH'].isin(tempp1)]
    tempp3 = tempp2[['Tóm tắt môn học','Tên MH']].agg(lambda x: ', '.join(x)).reset_index().transpose()
    tempp3.columns = tempp3.iloc[0]
    tempp3 = tempp3[1:]
    temp4 =  tempp3['Tên MH'] + " " + tempp3['Tóm tắt môn học']
    bad_chars = [';', ',', ':', ".", '▪','–','/','(',')','-','•','\r','...']
    for i in bad_chars:
        temp4 = temp4.str.replace(i, ' ', regex=False)
    
    df=df_graph

    rated_items = tempp1
    user_embedding = SBert.encode(temp4)
    user_embedding = user_embedding.reshape(768,)
    item_similarities = []
    for item_id in set(df['Ma_MH']):
        if item_id not in rated_items:
            try:
              item_embedding = get_MH_embedding(str(item_id))
              similarity = cosine_similarity([user_embedding], [item_embedding])[0][0]
              item_similarities.append((item_id, similarity))
            except:
              item_similarities.append((item_id, 0))

    
    
    recommended_items = sorted(item_similarities, key=lambda x: x[1], reverse=True)[:num_items]
    recommended_items_df = pd.DataFrame(recommended_items, columns = ['Ma_MH','cosine_similarity'])
    
    return recommended_items_df

e=recommend_items_from_builder("EC001 IS208 nt402")

def recommend_items_GNN(user_id, num_items=5):
  df = gnn_test_df[['MSSV','Ma_MH','rating']]

  rated_items = get_rated_items(user_id)
  list_rated_items = list(rated_items)
  df = gnn_test_df[['MSSV','Ma_MH','rating']]
  df = df[df['MSSV']==20521176]
  df = df[~df['Ma_MH'].isin(list_rated_items)]
  df = df.sort_values(by='rating',ascending=False)
  df = df[['Ma_MH','rating']].head(num_items)
  df.columns = ['Ma_MH','cosine_similarity']
  return df

f=recommend_items_GNN(20521176)
###################################################################################################################################
###################################################################################################################################
# Web_app
import streamlit as st

list_MSSV = set(df_graph['MSSV'])
list_MSSV = list(list_MSSV)
list_rec = [recommend_items_CB, recommend_items_CF, recommend_items_graph, recommend_items_hybrid, recommend_items_GNN]
num_list = list(range(1,11))

st.sidebar.markdown('__UIT Course Recommender__  \nAn app by '
                    '[datnt1171](https://courses.uit.edu.vn/user/profile.php?id=14366)')
st.sidebar.image('image/ISE.png', use_column_width=True)
st.sidebar.markdown('# Choose your Student ID')
st.sidebar.markdown('')

ph = st.sidebar.empty()
selected_MSSV = ph.selectbox('Select your student ID '
                              '(If it exists in my database)',
                              [''] + list_MSSV, key='default',
                              format_func=lambda x: 'Select your ID' if x == '' else x)  
                 
ph_model = st.sidebar.empty()
selected_model = ph_model.selectbox('Choose a model',
                              [''] + list_rec,
                              format_func=lambda x: 'Choose a model' if x == '' else x.__name__)  

ph_num_items = st.sidebar.empty()
selected_num = ph_num_items.selectbox('Choose number of courses',
                              [''] + num_list,
                              format_func=lambda x: 'Choose number of cources' if x == '' else x)

st.sidebar.markdown("# Did not find your ID?")
user_input = st.sidebar.text_area("type courses ID you have learn")
st.sidebar.markdown("Click on the button :point_down:")
btn = st.sidebar.button("Build your profile")


# Recommendation
if btn:
    selected_MSSV = 'Select your ID'

    st.markdown("# The recommended courses for you are:")
    rec_df_1 = recommend_items_from_builder(user_input)
    rec_df_vebose_1 = rec_df_1.merge(df_Content_MH, how='left', left_on='Ma_MH', right_on='Mã MH')
    rec_df_vebose_1 = rec_df_vebose_1[['Ma_MH','cosine_similarity','Tên MH','Tóm tắt môn học']]
    rec_df_vebose_1['Tên MH'].fillna('Không tìm thấy tên môn học', inplace=True)
    rec_df_vebose_1['Tóm tắt môn học'].fillna('Không tìm thấy nội dung môn học', inplace=True)
            
    for idx, row in rec_df_vebose_1.iterrows():
        st.markdown('### {} - {} - {}'.format(str(idx + 1), row['Ma_MH'], row['Tên MH']))
        st.markdown('cosine similarity with your profile are {}'.format(row['cosine_similarity']))
        st.markdown('{}'.format(row['Tóm tắt môn học']))

else:
    if selected_MSSV:
        if selected_model:
            if selected_num:
                rec_df = selected_model(selected_MSSV, selected_num)
                rec_df_vebose = rec_df.merge(df_Content_MH, how='left', left_on='Ma_MH', right_on='Mã MH')
                rec_df_vebose = rec_df_vebose[['Ma_MH','cosine_similarity','Tên MH','Tóm tắt môn học']]
                rec_df_vebose['Tên MH'].fillna('Không tìm thấy tên môn học', inplace=True)
                rec_df_vebose['Tóm tắt môn học'].fillna('Không tìm thấy nội dung môn học', inplace=True)
                
                st.markdown("# The recommended courses for {} are:".format(selected_MSSV))
                
                get_learned = get_rated_items(selected_MSSV)
                get_learned = list(get_learned)
                get_learned = " ".join(get_learned)
                st.markdown(f"## Courses you have taken are: {get_learned}")
                
                for idx, row in rec_df_vebose.iterrows():
                    st.markdown('### {} - {} - {}'.format(str(idx + 1), row['Ma_MH'], row['Tên MH']))
                    st.markdown('cosine similarity with your profile are {}'.format(row['cosine_similarity']))
                    st.markdown('{}'.format(row['Tóm tắt môn học']))




    
    
    


































