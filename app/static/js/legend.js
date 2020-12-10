/*
Condensed and customized version of:
https://observablehq.com/@d3/color-legend
https://observablehq.com/@mumairofficial/color-legend
*/

function legend({
  color,
  title,
  svg,
  tickSize = 6,
  width = 320,
  height = 44 + tickSize,
  marginTop = 18,
  marginRight = 0,
  marginBottom = 16 + tickSize,
  marginLeft = 0,
  ticks = width / 64,
  tickFormat,
  tickValues
} = {}) {

  legend = svg.append("g")
    .attr("class", "legend")


  let tickAdjust = g => g.selectAll(".tick line").attr("y1", marginTop + marginBottom - height);
  let x;

  // remove all but the continuous case
  const n = Math.min(color.domain().length, color.range().length);

  x = color.copy().rangeRound(d3.quantize(d3.interpolate(marginLeft, width - marginRight), n));

  legend.append("image")
        .attr("x", marginLeft)
        .attr("y", marginTop)
        .attr("width", width - marginLeft - marginRight)
        .attr("height", height - marginTop - marginBottom)
        .attr("preserveAspectRatio", "none")
        .attr("xlink:href", ramp(color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))).toDataURL());

  legend.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(d3.axisBottom(x)
        .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
        .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
        .tickSize(tickSize)
        .tickValues(tickValues))
      .call(tickAdjust)
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
        .attr("x", marginLeft)
        .attr("y", marginTop + marginBottom - height - 6)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .attr("font-size", "20px")
        .text(title));



  legend.selectAll(".tick text")
       .attr("font-size","15px")
       .attr("transform", "translate(0, -45)")

  // custom lock to adjust our label text location
  legend.selectAll(".tick text").filter(function (d, i) {return i == 0}).attr("x", 15)
  legend.selectAll(".tick text").filter(function (d, i) {return i == 2}).attr("x", -15)

  return legend;
}

function ramp(color, n = 256) {
  var canvas = document.createElement('canvas');
  canvas.width = n;
  canvas.height = 1;
  const context = canvas.getContext("2d");
  for (let i = 0; i < n; ++i) {
    context.fillStyle = color(i / (n - 1));
    context.fillRect(i, 0, 1, 1);
  }
  return canvas;
}