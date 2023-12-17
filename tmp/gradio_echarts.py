import gradio as gr
import os
import pandas as pd
os.environ['NO_PROXY'] = 'localhost'


# 示例 DataFrame
df = pd.DataFrame({
    'category': ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子'],
    'sales': [5, 20, 36, 10, 10, 20]
})

# 将 DataFrame 数据转换为 ECharts 需要的格式
def dataframe_to_echarts(df):
    categories = df['category'].tolist()
    sales = df['sales'].tolist()
    return categories, sales

# Gradio 接口
def generate_chart(x_list,y_list):
    # HTML 模板，其中包含 ECharts 的容器和引入 ECharts 的 JavaScript 库
    html_template = """
<head>
  <title>Awesome-pyecharts</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.1/dist/echarts.min.js"></script>
</head>

<body>
  <div id="main" style="width: 600px;height:400px;"></div>
  <script>
    var myChart = echarts.init(document.getElementById("main"));

    var option = {
      title: {
        text: "ECharts"
      },
      tooltip: {},
      legend: {
        data: ["销量"]
      },
      xAxis: {
        data: ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
      },
      yAxis: {},
      series: [{
        name: "销量",
        type: "bar",
        data: [5, 20, 36, 10, 10, 20]
      }]
    };

    myChart.setOption(option);
  </script>
</body>
"""

    html_template = f"""<iframe style="width: 100%; height: 480px" srcdoc='{html_template}'></iframe>"""

    return html_template

def update_chart():
  x_list, y_list = dataframe_to_echarts(df)
  return generate_chart(x_list,y_list)
  


with gr.Blocks() as app:
    with gr.Tab(label=''):
        with gr.TabItem("1"):
            input_question = gr.Textbox(label="请输入问题：")
            t_button = gr.Button("生成图表")
            output_html = gr.HTML()
    
    t_button.click(update_chart,inputs=[],outputs=[output_html])


app.launch(server_name="0.0.0.0",server_port=8000,share=False,debug=True)

