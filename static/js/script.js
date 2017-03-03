var urlBase = "https://cs590.herokuapp.com/"

function getData(urlBase, endPoint, callback) {
    url = urlBase + endPoint
    $.getJSON(url, function(json) {
        console.log("Url: " + url);
        callback(json);
    });
}
var p = new Parallel(['NYT', 'washingtonpost', 'WSJ', 'BBC', 'YahooNews']);

p.map(retrieveData);


getData("/", "get_tweets", function(json) {
	console.log("GOT DATA")
    console.log(json);
});

function retrieveData(data) {
    //console.log(data);
    getData("/", "get_tweets", function(json) {
        console.log(json);
    });
}

console.log("hello world");
