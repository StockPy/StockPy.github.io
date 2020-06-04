import re
import bs4, ssl
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from konlpy.tag import *

hannanum = Hannanum()
kkma = Kkma()
komoran = Komoran()

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from wordcloud import WordCloud
from collections import Counter
import numpy as np

def __Get_Text() :
    print("# Get_Text Function Start")

    File_Name = "New_inform.txt"
    # url = "https://www.clien.net/service/board/news"
    # """
    output = open(File_Name, 'w+t')
    for page_num in range(0, 15) :
        url = "https://www.clien.net/service/board/news?&od=T31&po=" + str(page_num)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' \
                                 'AppleWebKit/537.11 (KHTML, like Gecko) ' \
                                 'Chrome/23.0.1271.64 Safari/537.11', \
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', \
                   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', \
                   'Accept-Encoding': 'none', \
                   'Accept-Language': 'en-US,en;q=0.8', \
                   'Connection': 'keep-alive'}
        req = Request(url=url, headers=headers)

        try :
            html = urlopen(req).read()
        except HTTPError as err:
            if err.code == 404 :
                print("# Error HTTP : 404")
                return

        bs_object = bs4.BeautifulSoup(html, "html.parser")
        Get_Text = bs_object.find_all("span", {'class' : 'subject_fixed'})
        # test_1 = test.text
        # ---> text는 find에서 사용가능??? ---> for 문으로 돌리면 OK
        # AttributeError: ResultSet object has no attribute 'text'.You
        # 're probably treating a list of items like a single item. Did you call find_all() when you meant to call find()?

        for line in Get_Text :
            output.write(line.text + "\n")
    # """
    print("# Get_Text Function End")
    return File_Name

def clean_text(text):
    # cleaned_text = re.sub('[a-zA-z]', '', text)
    # cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"\♥\♡\ㅋ\ㅠ\ㅜ\ㄱ\ㅎ\ㄲ\ㅡ]', '', cleaned_text)
    cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"\♥\♡\ㅋ\ㅠ\ㅜ\ㄱ\ㅎ\ㄲ\ㅡ]', '', text)
    return cleaned_text

def __Cloud(file_name) :
    print("# __Cloud Function Start")
    # data1 = open(file_name).read()
    data1 = open(file_name, encoding='utf8', errors='ignore').read()
    # (result, consumed) = self._buffer_decode(data, self.errors, final)
    # UnicodeDecodeError: 'utf-8' codec can 't decode byte 0x84 in position 1927: invalid start byte
    # str = unicode(str, errors='replace') # or # str = unicode(str, errors='ignore')
    # import codecs
    # with codecs.open(file_name, 'r', encoding='utf-8',
    #                  errors='ignore') as fdata:

    print("# data1")
    print(data1)

    # sentence = clean_text(data1)
    # print("################# clean_text")
    # print(sentence)

    # data2 = kkma.nouns(data1) # 명사 골라내기
    # data2 = kkma.nouns(sentence) # 명사 골라내기
    print("# data2 : 명사 골라내기")
    # print(data2)
    # data2 = Counter(data1) # 명사 Counter
    hannanum = Hannanum()
    data2 = hannanum.nouns(data1)
    # data3 = Counter(sentence) # 명사 Counter
    data3 = Counter(data2)
    print("# data3 : 명사 Counter")
    print(data3)

    # 불용서 제거
    stop_words = open("stop_words.txt").read()
    data3 = [each_word for each_word in data2
             if each_word not in stop_words ]
    print("# data3-불용어 제거")
    print(data3)

    print("# data4")
    # 1글자 이하, 10글자 이상 단어 삭제
    data4 = []
    for i in range(0, len(data3)) :
        if len(data3[i]) >= 2 | len(data3[i]) <= 10 :
            data4.append(data3[i])
    print(data4)

    # 단어 별 빈도 수 집계
    data5 = Counter(data4)
    print("# data5")
    print(data5) # ---> <class 'collections.Counter'> : Counter({'애플': 1, '인수': 1})
    data6 = data5.most_common(50)
    print("# data6")
    print(type(data6)) # ---> <class 'list'> : [('애플', 1), ('인수', 1)]
    print(data6) # ---> [('애플', 1), ('인수', 1)] {'애플': 1, '인수': 1}
    tmp_data = dict(data6)
    print("# __Cloud Function End")

    return tmp_data

def __Line_Chart(SubNAME, x_List, y_List) :
    print("# __Line_Chart Function Start")

    # SubNAME_DF_value = str(SubNAME_DF) + "_value"
    x_date = x_List
    SubNAME_DF_value = y_List

    File_Name = SubNAME + ".html"
    output = open(File_Name, 'w+t')

    output.write("<html>\n \
    <head>\n \
    <meta charset = \"utf-8\">\n \
    <title> ECharts </title>\n \
    <!-- including ECharts file -->\n \
    <script src = \"echarts.js\"> </script>\n \
    </head>\n \
    <body>\n \
    <!-- prepare a DOM container with width and height -->\n \
    <div id = \"main\" style = \"width: 1200px;height:700px;\"> </div>\n \
    <script type = \"text/javascript\">\n \
    // based on prepared DOM, initialize echarts instance\n \
    var myChart = echarts.init(document.getElementById('main'));\n \
    // specify chart configuration item and data\n \
    var\n \
    option = {\n \
      title: {\n \
      text: 'ECharts entry example'\n \
      },\n \
      tooltip: {trigger: 'axis'},\n \
      legend: {\n \
        data: ['Sales']\n \
      },\n \
      xAxis: {\n \
      data: \n \
    [ ")

    for item in x_date:
        output.write("'%s'," % item)
    output.write("]")
    output.write("\n")
    output.write("          },\n")
    output.write("          yAxis: [")
    output.write("                  {\n")
    output.write("                  type: 'value', name: '%s',\n" % SubNAME)
    output.write("                  min: '0', max: %s, interval: '50',\n" % (max(SubNAME_DF_value)))
    output.write("                  axisLabel: { formatter: '{value} n' }\n")
    output.write("                  },\n")
    output.write("                  ],\n")
    output.write("          series: [\n")
    output.write("          {\n")
    output.write("              name: '%s',\n" % SubNAME)
    output.write("              type: '%s',\n" % "line")
    output.write("              data: ")
    output.write("[")
    for row in SubNAME_DF_value :
        output.write("'%s'," % row)
    output.write("],\n")
    output.write("              markPoint: {\n")
    output.write("              data: [{type: 'max', name: 'MAX'},\n")
    output.write("              {type: 'min', name: 'MIN'}]\n")
    output.write("              },\n")
    output.write("              markLine: {\n")
    output.write("              data: [{type: 'average', name: 'AVG'}]\n")
    output.write("              }\n")
    output.write("          },\n")
    output.write("]\n")
    output.write("};\n")
    output.write("// use configuration item and data specified to show chart\n")
    output.write("myChart.setOption(option);\n")
    output.write("</script>\n")
    output.write("</body>\n")
    output.write("</html>\n")

    output.close()
    print("# __Line_Chart Function End")

def __Bar_Chart(SubNAME, x_List, y_List) :
    print("# __Bar_chart Function Start")

    SubNAME_DF_x = []
    # SubNAME_DF_value = str(SubNAME_DF) + "_value"
    SubNAME_DF_x = x_List
    SubNAME_DF_value = y_List

    File_Name = SubNAME + ".html"
    output = open(File_Name, 'w+t')

    output.write("<!DOCTYPE html>\n \
    <html>\n \
    <head>\n \
    <meta charset = \"utf-8\">\n \
    <title> ECharts </title>\n \
    <!-- including ECharts file -->\n \
    <script src = \"echarts.js\"> </script>\n \
    </head>\n \
    <body>\n \
    <!-- prepare a DOM container with width and height -->\n \
    <div id = \"main\" style = \"width: 800px;height:500px;\"> </div>\n \
    <script type = \"text/javascript\">\n \
    // based on prepared DOM, initialize echarts instance\n \
    var myChart = echarts.init(document.getElementById('main'));\n \
    // specify chart configuration item and data\n \
    var option = {\n \
    title: {    text: 'ECharts entry example' },\n \
    tooltip: {},\n \
    legend: { data: ['")
    output.write(SubNAME)
    output.write("'] \
    },\n \
    xAxis: {\n \
        data: [ ")
    for row in SubNAME_DF_x :
        output.write("\"%s\", " % (row))
    output.write(" ]\n \
    },\n \
    yAxis: {},\n \
    series: [{\n \
        name: '")
    output.write(SubNAME)
    output.write("', \n \
            type: 'bar',\n \
        data: [ ")
    for row in SubNAME_DF_value :
        output.write("%d, " % (row))
    output.write("]\n \
    }]\n \
    };\n \
    // use configuration item and data specified to show chart\n \
    myChart.setOption(option);\n \
    </script>\n\
    </body>\n\
    </html>\n")

    output.close()
    print("# __Bar_chart Function End")

if __name__ == '__main__' :
    print("# Main Start")

    File_Name = __Get_Text()
    # file_name = "Hot_Spot.txt"
    tmp_data = __Cloud(File_Name)

    dict_key, dict_value  = [], []
    for key, value in tmp_data.items():
        dict_key.append(key)
        dict_value.append(value)
    print("# Dict Key")
    print(dict_key)
    print(dict_value)

    SubNAME = "WordCloud_Line_Chart"
    __Line_Chart(SubNAME, dict_key, dict_value)
    SubNAME = "WordCloud_Bar_Chart"
    __Bar_Chart(SubNAME, dict_key, dict_value)

    font_path = '/Library/Fonts/AppleGothic.ttf'
    wc = WordCloud(width=1000, height=600, background_color="white", font_path=font_path)
    plt.imshow(wc.generate_from_frequencies(tmp_data))
    plt.axis("off")
    plt.show()

    print("# Main End")
