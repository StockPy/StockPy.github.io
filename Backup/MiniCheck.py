def __Action() :
    import csv
    import pandas as pd
    import numpy as np
    df = pd.read_csv('minicheck_result.txt')
    df.rename(columns={'C' : 'CHECK'}, inplace=True)
    df.loc[df['CHID'].isnull(),'CHID'] = '---'
    df.loc[df['CHECK'].isnull(),'CHECK'] = 'OK'
    mapping = {'M00|M01' : 'OPERATION SYSTEM', 'M02': 'DISKS', 'M04' : 'MEMORY', \
               'M05' : 'TABLES', 'M06' : 'TRACES', 'M07' : 'STATISTICS', 'M08' : 'TRANSACTIONS', \
               'M09' : 'BACKUP', 'M10' : 'LOCKS', 'M11' : 'SQL', 'M12' : 'APPLICATION', \
               'M13' : 'SECURITY', 'M14' : 'LICENSE', 'M15' : 'NETWORK', 'M16' : 'XS', \
               'M17' : 'NAMESERVER', 'M18' : 'REPLICATION', 'M19' : 'OBJECTS', 'M20' : 'BW', \
               'M21': 'CONSISTENCY', 'M22': 'SMART', 'M23': 'ADMINISTRATION', 'M24': 'TABLE-REP', \
               'M25': 'SLT', 'M26': 'ENTERPRISE-SEARCH'
               }
    for k, v in mapping.items():
        df.loc[df['CHID'].str.contains(k), 'Category'] = v
    df.loc[df['CHECK'].str.contains('X'), 'CHECK'] = 'NOT OK'

    grouped = df.groupby('Category')
    df_grouped = grouped.count()

    df_check = df[{'Category', 'CHECK'}]
    NOT_OK = df_check.loc[df['CHECK'].str.contains('NOT OK')]
    NOT_OK_GR = NOT_OK.groupby('Category')
    NOT_OK_GRN = NOT_OK_GR.count()

    OK = df_check.loc[df['CHECK'].str.contains('OK')]
    OK_GR = OK.groupby('Category')
    OK_GRN = OK_GR.count()

    new_GF = pd.merge(NOT_OK_GRN, OK_GRN, on='Category')
    new_GF['SUM'] = new_GF['CHECK_x'] + new_GF['CHECK_y']
    new_GF['Perc'] = round(new_GF['CHECK_y'] / new_GF['SUM'] * 100)
    new_GF['100%'] = 100
    return new_GF

def __Make_HTML(Check_Index, Check_Value) :
    File_Name = "Echart_" +  Check_Index + ".html"
    output = open(File_Name, 'w+t')

    output.write("<!DOCTYPE html>\n")
    output.write("<html style = \"height: 100%\">\n")
    output.write("<head> <meta charset = \"utf-8\"> </head>\n")
    output.write("<body style = \"height: 100%; margin: 0\">\n")
    output.write("<div id = \"container\" style = \"height: 100%\"> </div>\n")
    output.write("<script type = \"text/javascript\" src = \"echarts.min.js\"> </script>\n")
    output.write("<script type = \"text/javascript\">\n")
    output.write("var dom = document.getElementById(\"container\");\n")
    output.write("var myChart = echarts.init(dom);\n")
    output.write("var app = {};\n")
    output.write("option = null; option = {\n")
    output.write("    tooltip: {\n")
    output.write("        formatter: '{a} <br/>{b} : {c}%'\n")
    output.write("    },\n")
    output.write("    series: [\n")
    output.write("        {\n")
    output.write("              type: 'gauge',\n")
    output.write("              data: [{value: " + str(Check_Value) + ", name: '" + str(Check_Index) + "'}] \n")
    output.write("      }\n")
    output.write("     ]\n")
    output.write("    };\n")

    output.write("    if (option && typeof option == \"object\") {\n")
    output.write(" myChart.setOption(option, false);\n")
    output.write(" }\n")
    output.write(" </script>\n")
    output.write(" </body>\n")

if(__name__ == '__main__') :
    new_GF = __Action()
    Check_Index, Check_Value = [], []
    for row in new_GF.index:
        Check_Index.append(row)
    for row in new_GF['Perc'] :
        Check_Value.append(row)
    for i in range(len(Check_Index)) :
        print(Check_Index[i], Check_Value[i])
        __Make_HTML(Check_Index[i], Check_Value[i])
