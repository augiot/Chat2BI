# -*- coding: UTF-8 -*-
"""
Author: SuTo
Date: 2023-09-25 08:28:03
LastEditors: Do not edit
LastEditTime: 2023-10-05 17:15:15
Description: 
"""


# 解决代理错误
import configparser
import os
import zhconv
from datetime import datetime
import traceback
os.environ['NO_PROXY'] = 'localhost'
import sys


# 获取系统路径 e:\GPT\project\chatafm
parent_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(parent_dir)
grandparent_dir = os.path.dirname(grandparent_dir)


# 将父级目录的父级目录添加到系统路径中
sys.path.append(grandparent_dir)
# print(grandparent_dir)

from log import log_main
import time
import gradio as gr


from utils.database.db_connect import Database
from main import main
import pandas as pd



value_string_file = os.path.join(grandparent_dir,"conf/cnc.txt")
# 从文本文件读取列表  
data_list = []  

with open(value_string_file, 'r',encoding='utf-8') as f:  
        for line in f.readlines():  
            data_list.append(line.strip().split(',')) 



# 最後一個字段進行聚合，不使用其值
columns_values = [item[:5] for item in data_list] 
columns_values = list(set(tuple(sublist) for sublist in columns_values))

columns_values = [",".join(item) for item in columns_values]
# print(columns_values[0])




'''
description: 
param {*} question 询问的问题
return {*}
author: SuTo
'''
def responder(question, request:gr.Request):
    # 转为简体
    question = zhconv.convert(question, 'zh-cn')
    
    ip = request.client.host
    # print(ip)
    log_main.info(f'ip: {ip}')
    log_main.info(f'question: {question}')
    
    current_time = datetime.now()
    # print("当前时间：",current_time)

    # 先调用大模型接口解析为标准语句
    start_time = time.time()
    threshold = 0.1
    config_path = grandparent_dir + "/conf/cnc_oee_configuration.json"
    sql = "暫時無法理解您的問題，請更換問法，重新提問！"
   
    try:
        sql = main(config_path, question, threshold)
        # log_main.info(f'answer: {sql}')    
        # print("LLM查询时间:",time.time()-start_time)
        log_main.info(f'LLM查詢時間:",{time.time()-start_time}')

        config = configparser.ConfigParser()
        config.read(grandparent_dir + '/conf/dbConfig.ini')

        
        # 连接到PostgreSQL数据库
        pg_db = Database(config, "75")
        pg_db.connect()

        df=pd.read_sql(sql,con=pg_db.engine) 
        table_df = df


    except:

        # print("查询数据库报错")
        # print(traceback.format_exc())
        log_main.error(f'查询数据库出错：{traceback.format_exc()}') 
        data = {'狀況': [ '問題條件不符，請仔細檢查後重新提問', ], '情況': ['查詢數據庫出錯',]}
        table_df = pd.DataFrame(data)

    # print("LLM+可视化时间:",time.time()-start_time)
    log_main.info(f'LLM+数据库时间:",{time.time()-start_time}')
    # print(sql,img_path,table_df,table_df)      
    return sql  ,table_df


    

text_str = """
### 請注意：目前查詢支持範圍
- 支持條件：日期，廠區（觀瀾），樓層，機種，工站，線別，機台
- 支持指標：OEE，生產達成率，良率，時間稼動率，性能稼動率，排配數量，標準OEE，實際產量，標準性能稼動率，標準時間稼動率
- 指標計算維度：天
### 提問示例：
#### 單指標
- 能否告知近一周的觀瀾廠區GL-C06-5F樓層237M機種的CNC6工站的OEE數據？  
- 本月觀瀾廠區的GL-B06-3F樓層233M機種CNC2.5工站的生產達成率  
- 本周的gl廠區的GL-B12-4F樓層237M機種的CNC1.1-1工站各線別的生產達成率  
- 能否告知20231205的GL廠區GL-C06-4F樓層233M機種的CNC7工站的C線和D線的生產達成率  
- 查詢2023年12月1日到2023年12月5日GL工廠GL-C06-5F樓層237M機種的CNC5-P工站的生產達成率？  
- 查詢20231201到20231205的GL工廠GL-C06-5F樓層237M機種的CNC5-P工站A線別所有機台的性能稼動率？
- 查詢20231201到20231206的GL工廠GL-C06-5F樓層237M機種的CNC5-P工站A線別各機台良率
#### 多指標
- 查詢20231201到20231206的GL工廠GL-C06-5F樓層237M機種的CNC5-P工站A線別所有機台的生產達成率、排配數量、實際產量    
- 本月觀瀾廠區的GL-B06-3F樓層233M機種CNC2.5工站的oee、標準oee  
- 本月觀瀾廠區的GL-B12-4F樓層237M機種CNC1.1-1工站的標準性能稼動率、性能稼動率、標準時間稼動率、時間稼動率  
"""

if __name__ == "__main__":
  

    with gr.Blocks() as demo:
        
  
        
        with gr.Tab("Text2SQL模型調測頁面，後續頁面由簡劃平臺呈現"):
            introduction = gr.Markdown(value=text_str,label="使用說明")
            table_condition= gr.Dropdown(choices = columns_values,label="數據庫存在條件,僅為測試進行參照：樓層、機種、工站、線別")
            with gr.Row():
                text_input = gr.Textbox(label="問題")               
                text_button = gr.Button(value="查詢")
            text_output = gr.HTML(label="解析的sql",render=True)
            table_df = gr.DataFrame(label="數據表")       
        static_html_path = grandparent_dir + "/utils/data/show.html"
        # 打开HTML文件
        with open(static_html_path, 'r',encoding='utf-8') as file:
            # 读取文件内容
            html_content = file.read()

        print(html_content)
       
        gr.HTML(value=html_content)

        gr.HTML(value="<h1>歡迎使用Text2SQL模型調測頁面，後續頁面由簡劃平臺呈現</h1>")

        text_button.click(responder, inputs=[text_input], outputs=[text_output,table_df])

    demo.queue().launch(server_name="0.0.0.0",server_port=8000,max_threads=20)


