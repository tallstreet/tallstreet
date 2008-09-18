
function clk(url_id) {
	document.forms['clkForm']['url_id'].value = url_id;
	var ratingElementId = this.ratingElementId;
	postForm('clkForm', true, function (req) { });
	this.hasSet = true;
}

onLoadFunctionList = new Array();
function performOnLoadFunctions()
{
	for (var i in onLoadFunctionList)
	{
		onLoadFunctionList[i]();
	}
}


function drawRating(url, id, stars){

	document.write('<li class="rating"><div id="ratingDiv' + id + '">\n');
	document.write('<div id="ratingMessage' + id + '" class="label">Rate this site</div>\n');
	document.write('<script language="javascript">\n');
	document.write('ratingComponent' + id + ' = new UTRating(\'ratingDiv' + id + '\', 5, \'ratingComponent' + id + '\', \'ratingForm\', \'ratingMessage' + id + '\', \'' + id + '\', \'L\', \'' + url + '\');\n');
	document.write('ratingComponent' + id + '.starCount=' + stars + ';\n');
	document.write('onLoadFunctionList.push(function() { ratingComponent' + id + '.drawStars(' + stars + ', true); });\n');
	document.write('</script>\n');
	document.write('</div><div>	<nobr>\n');
	document.write('<a href="#" onclick="ratingComponent' + id + '.setStars(1); return false;" onmouseover="ratingComponent' + id + '.showStars(1);" onmouseout="ratingComponent' + id + '.clearStars();"><img src="/img/star_bg.gif" id="star_' + id + '_1"></a>');
	document.write('<a href="#" onclick="ratingComponent' + id + '.setStars(2); return false;" onmouseover="ratingComponent' + id + '.showStars(2);" onmouseout="ratingComponent' + id + '.clearStars();"><img src="/img/star_bg.gif" id="star_' + id + '_2"></a>');
	document.write('<a href="#" onclick="ratingComponent' + id + '.setStars(3); return false;" onmouseover="ratingComponent' + id + '.showStars(3);" onmouseout="ratingComponent' + id + '.clearStars();"><img src="/img/star_bg.gif" id="star_' + id + '_3"></a>');
	document.write('<a href="#" onclick="ratingComponent' + id + '.setStars(4); return false;" onmouseover="ratingComponent' + id + '.showStars(4);" onmouseout="ratingComponent' + id + '.clearStars();"><img src="/img/star_bg.gif" id="star_' + id + '_4"></a>');
	document.write('<a href="#" onclick="ratingComponent' + id + '.setStars(5); return false;" onmouseover="ratingComponent' + id + '.showStars(5);" onmouseout="ratingComponent' + id + '.clearStars();"><img src="/img/star_bg.gif" id="star_' + id + '_5"></a>');
	document.write('</nobr>	</div> </li>\n');

}

function toggleLayer(whichLayer)
{
if (document.getElementById)
{
// this is the way the standards work
var style2 = document.getElementById(whichLayer).style;
style2.display = style2.display? "":"block";
}
else if (document.all)
{
// this is the way old msie versions work
var style2 = document.all[whichLayer].style;
style2.display = style2.display? "":"block";
}
else if (document.layers)
{
// this is the way nn4 works
var style2 = document.layers[whichLayer].style;
style2.display = style2.display? "":"block";
}
}