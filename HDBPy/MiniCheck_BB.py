import csv
import pandas as pd
import numpy as np

def __Action() :
    df = pd.read_csv('minicheck_result.txt')
    df.rename(columns={'C' : 'CHECK'}, inplace=True)
    df.loc[df['CHID'].isnull(),'CHID'] = '---'
    df.loc[df['CHECK'].isnull(),'CHECK'] = 'OK'
    mapping = {'M00|M01' : 'MiniCheck_Inform', 'M02': 'OPRATION_SYSTEM', 'M03': 'DISKS', 'M04' : 'MEMORY', \
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
    df.to_csv('test.txt')

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
    new_GF.loc["전 체", :] = new_GF.sum()
    new_GF['Perc'] = round(new_GF['CHECK_y'] / new_GF['SUM'] * 100, 0)
    return df, new_GF

def __Main_Page(new_GF) :
    new_GF.rename(columns={'CHECK_x' : 'Need to Check'}, inplace=True)
    new_GF.rename(columns={'CHECK_y' : 'Complete'}, inplace=True)
    new_GF.rename(columns={'SUM' : 'Total'}, inplace=True)
    new_GF.rename(columns={'Perc' : 'Checked(%)'}, inplace=True)
    pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>
    html_string = '''
    <html>
      <meta charset="utf-8">
      <head><title>HTML Pandas Dataframe with CSS</title></head>
      <link rel="stylesheet" type="text/css" href="billboard.min.css"/>
      <body>
        {table}
      </body>
    </html>
    '''
    # OUTPUT AN HTML FILE
    with open('BB_Main.html', 'w+t') as f:
        f.write(html_string.format(table=new_GF.to_html(classes='mystyle')))

def __Make_HTML(Check_Index, Check_Value) :
    File_Name = "BB_" +  Check_Index + ".html"
    output = open(File_Name, 'w+t')

    html_string = '''
    <!DOCTYPE html>
    <html style=\"height: 100%\">
    <head>
    <meta http-equiv=\"content-type\" content =\"text/html; charset=UTF-8\">
    <title> </title>
    <script type=\"text/javascript\" src=\"/js/lib/dummy.js\"> </script>
    <link rel=\"stylesheet\" type=\"text/css\" href=\"/css/result-light.css\">
    <script type=\"text/javascript\" src=\"billboard.pkgd.min.js\"> </script>
    <link rel=\"stylesheet\" type=\"text/css\" href=\"billboard.min.css\">
    <style id=\"compiled-css\" type=\"text/css\"> </style>
    </head>
    <body>
    <div id=\"gaugeChart\"> </div>
    <!-- TODO: Missing CoffeeScript 2 -->
    <script type=\"text/javascript\">
    var chart = bb.generate({
              data: { json: { " ''' + str(Check_Index) + '''": ["''' + str(Check_Value) + '''"]}, type: \"gauge\"},
              color : { pattern: [\"#FF0000\", \"#F97600\", \"#F6C600\", \"#60B044\"],
                        threshold : {values: [30, 60, 90, 100]}
              },
              gauge: {min: 0, max: 100},
              size: {height: 120}
              });
    </script>
    </body>
    </html>
    ''' # 30 : 빨강, 60 : 노랑, 90 : 주황, 100 : 녹색
    output.write(html_string)
    output.close()

def __One_Page(Check_Index) :
    output = open('BB_Main.html', 'a')
    output.write("<body>\n")
    output.write("<div id=\"gaugeChart\"> </div>\n")
    output.write("<!-- TODO: Missing CoffeeScript 2 -->\n")
    output.write("<table style=\"margin-left: auto; margin-right: auto; text-align: center;\" border=1>")
    for row in Check_Index :
        output.write("<tr>\n")
        output.write("<td><a href=" + row + ".html>" + row + " 영역 </a></td>\n")
        output.write("<td> <embed type=\"text/html\" src=\"BB_" + row + ".html\"></td>\n")
        output.write("<tr>\n")
    output.write("</table")
    output.write("</body>\n")
    output.write("</html>\n")
    output.close()

def __Category_Page(df_sep) :
    pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>
    html_string = '''
    <html>
      <meta charset="utf-8">
      <head><title>HTML Pandas Dataframe with CSS</title></head>
      <link rel="stylesheet" type="text/css" href="billboard.min.css"/>
      <body>
        {table}
      </body>
    </html>
    '''
    for row in df_sep['Category'].unique() :
        filename = row + ".html"
        output = open(filename, 'w+t')
        df_sep1 = df_sep.loc[df['Category'] == row]
        print(df_sep1)
        output.write(html_string.format(table=df_sep1.to_html(classes='mystyle')))
        # rm OPRATION_SYSTEM.html DISKS.html MEMORY.html TABLES.html STATISTICS.html STATISTICS.html BACKUP.html LOCKS.htm SQL.html APPLICATION.html LICENSE.html OBJECTS.html ADMINISTRATION.html MiniCheck_Inform.html LOCKS.html

if(__name__ == '__main__') :
    df, new_GF = __Action()
    Check_Index, Check_Value = [], []
    for row in new_GF.index:
        Check_Index.append(row)
    for row in new_GF['Perc'] :
        Check_Value.append(row)
    __Main_Page(new_GF)
    for i in range(len(Check_Index)) :
        __Make_HTML(Check_Index[i], Check_Value[i])
    __One_Page(Check_Index)
    df_sep = df.loc[df['CHECK'].str.contains('NOT OK')]
    df_sep = df_sep[['Category', 'DESCRIPTION','VALUE','CHECK']]
    __Category_Page(df_sep)
