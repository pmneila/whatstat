# encoding: utf-8

import sys
import os
import os.path
import codecs
from string import Template

import parser
import whatstat as stats

import networkx as nx

template = Template(u"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart", "table"]});
      google.setOnLoadCallback(draw);
      function draw() {
          drawMessagesChart();
          drawCharactersChart();
          drawTable();
      }
      
      function drawMessagesChart() {
        var data = google.visualization.arrayToDataTable([
          ['Autor', 'Número de mensajes'],
          $messages
        ]);
        
        var options = {
          title: 'Número de mensajes por participante'
        };
        
        var chart = new google.visualization.PieChart(document.getElementById('messages_chart_div'));
        chart.draw(data, options);
      }
      
      function drawCharactersChart() {
        var data = google.visualization.arrayToDataTable([
          ['Autor', 'Número de caracteres'],
          $characters
        ]);
        
        var options = {
          title: 'Cantidad de texto escrito por participante'
        };
        
        var chart = new google.visualization.PieChart(document.getElementById('characters_chart_div'));
        chart.draw(data, options);
      }
      
      function drawTable() {
        var data = new google.visualization.DataTable();
        // data.addColumn('number', 'Ranking');
        data.addColumn('string', 'Palabra');
        data.addColumn('number', 'Número de repeticiones');
        data.addRows([
          $words
        ]);

        var table = new google.visualization.Table(document.getElementById('table_div'));
        table.draw(data, {showRowNumber: true});
      }
    </script>
  </head>
  <body>
    <h1>Estadísticas de "Gracias Sara"</h1>
    <h2>Colaboración</h2>
    <div id="messages_chart_div" style="width: 900px; height: 500px;"></div>
    <div id="characters_chart_div" style="width: 900px; height: 500px;"></div>
    <h2>Positivos</h2>
    <a href="positives.png"><img src="positives.png"/></a>
    <div style="width: 900px; font-size: small;">
        Cada nodo contiene el nombre del participante y entre paréntesis los positivos recibidos.
        Una flecha A---n-->B indica que A dio n positivos a B. El grosor y el color de la flecha
        dependen del número de positivos.</div>
    <h2>Palabras más repetidas (quitando las 1000 más comunes del español)</h2>
    <div id="table_div" style="width: 900px; height: 500px;"></div>
  </body>
</html>
""")

def write_stats(destpath, chat, common_words):
    
    messages_author = stats.messages_per_author(chat)[::-1]
    aux1 = u', '.join(map(lambda x: u'["{0}", {1}]'.format(x[0], x[1]), messages_author))
    characters_author = stats.characters_per_author(chat)[::-1]
    aux2 = u', '.join(map(lambda x: u'["{0}", {1}]'.format(x[0], x[1]), characters_author))
    
    words = stats.most_common_uncommon_words(chat, common_words, 250)
    aux3 = u', '.join(map(lambda x: u'["{0}", {1}]'.format(x[0], x[1]), words))
    
    code = template.substitute(messages=aux1, characters=aux2, words=aux3)
    
    # Save the result.
    if not os.path.exists(destpath):
        os.makedirs(destpath)
    
    # Create the positives graph.
    g = stats.positives(chat)
    destdot = os.path.join(destpath, "positives.dot")
    destpng = os.path.join(destpath, "positives.png")
    nx.write_dot(g, destdot)
    os.system("dot {0} -Tpng > {1}".format(destdot, destpng))
    
    # Create the html.
    desthtml = os.path.join(destpath, "index.html")
    
    # Write the html file.
    f = open(desthtml, "w")
    f.write(code.encode("utf-8"))
    f.close()

if __name__ == '__main__':
    chat = parser.parse(sys.argv[1])
    execfile(sys.argv[2], globals(), locals())
    chat.set_aliases(alias)
    common_words = parser.parse_words(sys.argv[3])
    write_stats(sys.argv[4], chat, common_words)
