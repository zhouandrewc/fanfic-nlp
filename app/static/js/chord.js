/*
d3 chord diagram for my Flask character interaction visualization app

A lot of online code was referenced and will be cited here:

(chord diagram)
https://www.d3-graph-gallery.com/graph/chord_colors.html
https://www.d3-graph-gallery.com/graph/chord_basic.html
https://www.d3-graph-gallery.com/graph/chord_axis_labels.html
https://bl.ocks.org/mbostock/1308257
http://bl.ocks.org/syntagmatic/9eadf19bd2976653fa50

(tooltip)
http://bl.ocks.org/mstanaland/6100713

(legend)
https://bl.ocks.org/starcalibre/6cccfa843ed254aa0a0d
https://observablehq.com/@d3/color-legend
https://observablehq.com/@mumairofficial/color-legend
(a fork of the former for d3v5, though not sure how much custom work it has)
*/


function createChordDiagram(char_data) {
  // create the svg area

  var margin = {top: 0, right: 20, bottom: 20, left: 20},
      width = 700 - margin.left - margin.right,
      height = 600 - margin.top - margin.bottom;

  var trans_x = margin.left + width/2
  var trans_y = margin.top + height/2

  var innerRadius = 230
  var outerRadius = 260

  char_list = char_data["char_list"]
  char_freqs = char_data["char_freqs"]
  matrix = char_data["pair_freqs"]
  pair_sentiments = char_data["pair_sentiments"]

  /*var margin = {top: 75, right: 30, bottom: 120, left: 120},
      width = 800 - margin.left - margin.right,
      height = 680 - margin.top - margin.bottom;*/

  var svg = d3.select("#chord")
    .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + trans_x + "," + trans_y + ")")

  var char_colors = {"Aang": "#fcdc7b", "Sokka": "#349eeb", "Katara": "#3ce5e8", "Zuko": "#b30000", "Toph": "#009933", "Azula": "red", "Ozai": "red", "Iroh": "red", "Ursa": "red", "Zhao": "red"}

  var colors = []
  for (i = 0; i < char_list.length; i++)
      colors.push(char_colors[char_list[i]])

  // give this matrix to d3.chord(): it will calculates all the info we need to draw arc and ribbon
  var res = d3.chord()
      .padAngle(0.0)     // padding between entities (black arc)
      .sortSubgroups(d3.descending)
      (matrix)


  var sentimentScale = d3.scaleLinear().domain([-1,0,1])
    .range(["red", "white", "blue"])


  var group = svg
    .datum(res)
    .append("g")
    .selectAll("g")
    .data(function(d) { return d.groups; })
    .enter().append("g")

  group.append("path")
    .style("fill", function(d,i){return colors[i]})
    .style("stroke", "black")
    .attr("d", d3.arc()
      .innerRadius(innerRadius)
      .outerRadius(outerRadius))
    .attr("id", function(d,i){return "group"+i})
    .on("mouseover", function() { tooltip.style("display", null); })
    .on("mouseout", function() { tooltip.style("display", "none"); })
    .on("mousemove", function(d, i) {
      var xPosition = d3.mouse(this)[0] - 35;
      var yPosition = d3.mouse(this)[1] - 55;
      tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
      var char = char_list[i]
      //tooltip.select("text").html(c1 + " & " + c2 + "<br>" + score);
      tooltip.select("#pair-name").html(char)
      tooltip.select("#pair-freq").html("Frequency: " + (100*char_freqs[i]).toFixed(1) + "%")
      tooltip.select("#pair-score").html("")

    })

  group.append("text")
      .attr("dx", function(d, i) {
        return 10
      })
      .attr("dy", 25)
    .append("textPath")
      .attr("class", "label")
      .attr("xlink:href", function(d, i) { return "#group" + i; })
      .text(function(d, i) {
        if (d.value > 0.03) {
          return char_list[i];
        } else {
          return ""
        }
      })
      .style("fill", function(d, i) { return "black"; })

  var legendFullHeight = 500;
  var legendFullWidth = 50;

  var legendMargin = { top: 20, bottom: 20, left: 5, right: 20 };

  var legendWidth = legendFullWidth - legendMargin.left - legendMargin.right;
  var legendHeight = legendFullHeight - legendMargin.top - legendMargin.bottom;

  svg.append("g")
      .attr("transform", 'translate(' + 100 + ',' + 100 + ')')
      .append("rect")
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#gradient)');


  // Add the links between groups
  svg
    .datum(res)
    .append("g")
    .selectAll("path")
    .data(function(d) { return d; })
    .enter()
    .append("path")
      .attr("d", d3.ribbon()
        .radius(innerRadius)
      )
      .style("fill", function(d, i) {
        if (d.source.index == d.target.index) {
          return "#909090"
        }
        return sentimentScale(pair_sentiments[d.source.index][d.target.index])
      })
      .style("stroke", "black")
      .on("mouseover", function() { tooltip.style("display", null); })
      .on("mouseout", function() { tooltip.style("display", "none"); })
      .on("mousemove", function(d) {
        var xPosition = d3.mouse(this)[0] - 35;
        var yPosition = d3.mouse(this)[1] - 55;
        tooltip.attr("transform", "translate(" + xPosition + "," + yPosition + ")");
        var c1 = char_list[d.source.index]
        var c2 = char_list[d.target.index]
        var score = pair_sentiments[d.source.index][d.target.index].toFixed(2)
        //tooltip.select("text").html(c1 + " & " + c2 + "<br>" + score);
        tooltip.select("#pair-name").html(c1 + " & " + c2)
        tooltip.select("#pair-freq").html("Frequency: " + (d.source.value*100).toFixed(1) + "%")
        if (c1 != c2) {
          tooltip.select("#pair-score").html("Sentiment: " + score)
        } else {
          tooltip.select("#pair-score").html("")
        }
        t

      })
      .on("click", function(d) {
        sentences = char_data["pair_sentences"][d.source.index][d.target.index]
        $("#interactions").empty()
        //$("#interactions").append("<table class='int-line'>")
        var c1 = char_list[d.source.index]
        var c2 = char_list[d.target.index]

        table_html = "<table id='int-table' style='width:100%' class='int-table'>"

        for (i = 0; i < sentences.length; i++) {
          var sentence = sentences[i][0]
          var sentiment = sentences[i][1]
          var color = d3.color(sentimentScale(sentiment)).formatHex()


          sentence = sentence.replaceAll(c1, "<span style='font-weight:bold; color: " + char_colors[c1] + "'>" + c1 + "</span>")
          sentence = sentence.replaceAll(c2, "<span style='font-weight:bold; color: " + char_colors[c2] + "'>" + c2 + "</span>")
          // maybe highlight the characters' names?
          table_html += "<tr>"
          table_html += "<td style='width:40px' bgcolor='" + color + "'> </th>"
          table_html += "<td>" + sentence + " (" + sentiment.toFixed(2) + ")" + "</td>"
          table_html += "<tr>"
          /*$("#interactions").append("<tr>")
          $("#interactions").append("<td class='col-1' bgcolor='" + sentimentScale(sentiment) + "'>TESST")
          $("#interactions").append("</td>")
          $("#interactions").append("<td class='col-2'>")
          $("#interactions").append(sentences[i][0])
          $("#interactions").append("</td>")
          $("#interactions").append("</td>")
          $("#interactions").append("</tr>")*/
          //$("#interactions").append("<span class='left-bar' style='background-color:" + sentimentScale(sentiment) + "'>test</span>")
          //$("#interactions").append("<span class='right-text'>" + sentences[i][0]+ "</span></div>")
        }
        table_html += "</table>"
        $("#interactions").append(table_html)
        $("#int-chars").text("Interactions: " + char_list[d.source.index] + " & " + char_list[d.target.index])
      })

  var tooltip = svg.append("g")
  .attr("class", "tooltip")
  .style("display", "none");

  tooltip.append("rect")
    .attr("class", "tooltip-rect")
    .attr("fill", "lightsteelblue")
    .attr("rx", 8)
    .attr("ry", 8)

  tooltip.append("text")
    .attr("x", 8)
    .attr("dy", "1.2em")
    .attr("id", "pair-name")

  tooltip.append("text")
    .attr("x", 8)
    .attr("dy", "2.4em")
    .attr("id", "pair-freq")

  tooltip.append("text")
    .attr("x", 8)
    .attr("dy", "3.6em")
    .attr("id", "pair-score")

  legend({
    color: d3.scaleLinear([-1, 0, 1], ["red", "white", "blue"]),
    title: "",
    svg,
    width: 440,
    height: 60,
    ticks: 3,
    tickFormat: function(d, i) {
      return ["Negative (-1)", "Neutral (0)", "Positive (1)"][i]
    },
    tickValues: [-1, 0, 1]
  }).attr("transform", "rotate(-90) translate(-200, -330)")//"translate(-330,-360)")

}