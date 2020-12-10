// grab the text which is injected into a data element in the HTML page by Flask
// consulted https://stackoverflow.com/questions/2190801/passing-parameters-to-javascript-files

var this_js_script = $('script[src*=init]');

var text = this_js_script.attr('data-text');
if (typeof text === "undefined" ) {
   var text = 'Zuko here.';
}

function process_text(text){
  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: "/process_text",
    dataType: "json",
    async: true,
    data: JSON.stringify({"text": text}),
    success: function (data) {
        createChordDiagram(data)
    },
    error: function (result) {
        console.log(result)
    }
  })
}

process_text(text)