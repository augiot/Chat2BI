import configparser
from pandas import DataFrame
import pandas as pd
import numpy as np
import os
import sys



from pyecharts.charts import Line,Bar,Grid,Tab
import pyecharts.options as opts
# from pyecharts.render import make_snapshot
# from snapshot_selenium import snapshot

# TODO:切换服务器需要更换路径

# 获取系统路径 e:\GPT\project\chatafm
parent_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(parent_dir)
grandparent_dir = os.path.dirname(grandparent_dir)
# 将父级目录的父级目录添加到系统路径中
sys.path.append(grandparent_dir)
# print(grandparent_dir)


from utils.database.db_connect import Database


static_html_path = grandparent_dir + "/utils/data/show.html"



# 判定是否为数字的函数
def is_numeric(column):
    try:
        pd.to_numeric(column)
        return True
    except ValueError:
        return False


def preprocess_columns(df:DataFrame):
    x_default = ['日期']
    groupby = []
    indicators = []
    headers = df.columns
    # print(headers)          

    # print(numeric_cols)
    for headar in headers:  
        if headar == '日期':
            continue

        if is_numeric(df[headar]):
            indicators.append(headar)
        else:
            groupby.append(headar)
    
    return x_default, groupby, indicators

def draw_show_type(df:DataFrame,show_type:str):

    x_default, groupby, indicators = preprocess_columns(df)

    if show_type == 'line':
        show = Line()
    else:
        show = Bar()
    # 如果只查询某天同时，同时具有groupby信息
    if len(groupby) > 0 and len(df[x_default[0]].unique()) == 1:
        
        show.add_xaxis(xaxis_data = df[groupby[0]].to_list())

        for index,item in enumerate(indicators): 
            show.add_yaxis(item, df[item].to_list())
        show.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
            legend_opts=opts.LegendOpts(type_='scroll'),
            datazoom_opts=opts.DataZoomOpts()
            
        )
        # show.render(static_html_path)

    else:
        if len(groupby) > 0 :

            df_pivot = df.pivot(index=x_default, columns=groupby, values=indicators).reset_index()
        else:
            df_pivot = df
        # print(df_pivot.columns)


        show = Line()
        no_show_dict = {}
        show.add_xaxis(xaxis_data = df_pivot[x_default[0]].to_list())
        for index,item in enumerate(df_pivot.columns):  
            item_name = "".join(item)
            
            if item_name == '日期':
                continue
            show.add_yaxis(item_name, df_pivot[item].to_list())
            # 默认只展示5个图例
            if index >= 6:
                no_show_dict[item_name] = False
    
        show.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
            legend_opts=opts.LegendOpts(type_='scroll',selected_map=no_show_dict),
            datazoom_opts=opts.DataZoomOpts()
            
        )
        # show.render(static_html_path)
    return show

def draw_table(df:DataFrame):
    line = draw_show_type(df,"line")
    bar = draw_show_type(df,"bar")
    tab = Tab()
    tab.add(line, "line")
    tab.add(bar, "bar")
    tab.render(static_html_path)

    return static_html_path


if __name__ == '__main__':

   

    sql = """
SELECT stat_date as 日期,((sum(ct_por * prod_corr * ok_num)/sum(ttl_time)/3600)*100) ::decimal(10, 2) as OEE FROM cnc_pdata.v_phm_floor_manage_result WHERE stat_date>='2023-08-01' and stat_date<='2023-08-31'and factory='GL' and area_floor_id='GL-C06-5F' and project='237M' and work_station='CNC6'  GROUP by stat_date
"""
    sql = """
SELECT stat_date as 日期,equipment_name as 機臺,max(stand_oee)::decimal(10, 2) as 標準OEE,((sum(ct_por * prod_corr * ok_num)/sum(ttl_time)/3600)*100) ::decimal(10, 2) as OEE FROM cnc_pdata.v_phm_floor_manage_result WHERE stat_date>='2023-12-01' and stat_date<='2023-12-05'and factory='GL' and area_floor_id='GL-C06-5F' and project='237M' and work_station='CNC5-P' and line_no='A' GROUP by stat_date,equipment_name
"""
    sql1 = """
SELECT stat_date as 日期,equipment_name as 機臺,((sum(ct_por * prod_corr * ok_num)/sum(ttl_time)/3600)*100) ::decimal(10, 2) as OEE FROM cnc_pdata.v_phm_floor_manage_result WHERE stat_date>='2023-12-01' and stat_date<='2023-12-05'and factory='GL' and area_floor_id='GL-C06-5F' and project='237M' and work_station='CNC5-P' and line_no='A' GROUP by stat_date,equipment_name
"""
    sql = """
SELECT stat_date as 日期,work_station as 工站,((sum(ct_por * prod_corr * ok_num)/sum(ttl_time)/3600)*100) ::decimal(10, 2) as OEE,max(stand_oee)::decimal(10, 2) as 標準OEE FROM cnc_pdata.v_phm_floor_manage_result WHERE stat_date>='2023-12-01' and stat_date<='2023-12-16'and factory='GL' and area_floor_id='GL-B05-3F' and project='233M' GROUP by stat_date,work_station

"""
    sql = """
SELECT stat_date as 日期,line_no as 線別,(case when sum(all_num)>0 and sum(aps_plan_num_class)>0 then (sum(all_num)*100*6/sum(aps_plan_num_class))::decimal(10, 2) else 0 end) as 生產達成率,coalesce(sum(aps_plan_num_class)/6,0) as 排配數量,coalesce(sum(all_num),0) as 實際產量 FROM cnc_pdata.v_phm_floor_manage_result WHERE stat_date='2023-12-05' and factory='GL' and area_floor_id='GL-C06-4F' and project='233M' and work_station='CNC7' GROUP by stat_date,line_no

"""


    #### 数据库连接  读取数据位df
    config = configparser.ConfigParser()
    config.read('conf/dbConfig.ini')   
    # 连接到PostgreSQL数据库
    pg_db = Database(config, "75")
    pg_db.connect()

    df=pd.read_sql(sql,con=pg_db.engine)
    df = df.sort_values(by='日期',ascending=True)

    html_path = draw_table(df)

   

    

    
