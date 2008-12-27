
function addRow(keyword){
	if (keyword != '' && $("input[name='keyword[" + i + "]']").val() == ""){
		$("input[name='keyword[" + i + "]']").val(keyword)
	} else {
		var newrow = $("#row" + i).clone().insertAfter($("#row" + i))
		i = i + 1;
		newrow.attr("id", "row" + i)
		$("#row" + i + " input[name='keyword[" + (i-1) + "]']").attr({name: "keyword[" + i + "]"}).val(keyword).keyup(function() {update_keyword(this)})
		$("#row" + i + " input[name='investment[" + (i-1) + "]']").attr({name: "investment[" + i + "]"}).val(0).keyup(function() {update_balance(this)})
		$("#row" + i + " input[name='edit[" + (i-1) + "]']").attr("name", "edit[" + i + "]").val(true)
		$("#row" + i + " #keywordlink" + (i-1)).attr("id", "keywordlink" + i).html('')
	}
	keywords[keyword] = '';
	print_keywords();
	update_keyword($("input[name='keyword[" + i + "]']")[0]);
}


function print_keywords(){
	var dstDiv = $('#TagCloud').empty()
	for (tag in keywords) {
		if (typeof keywords[tag] != 'function'){
			dstDiv.append(keywords[tag])
		}
	}	
	dstDiv.append(' &nbsp;<a href="javascript:addRow(\'\')" style="font-size: 10px; color: blue;">New Keyword</a>&nbsp;')
}

function formatCurrency(num) {
	num = num.toString().replace(/\$|\,/g,'');
	if(isNaN(num))
	num = "0";
	sign = (num == (num = Math.abs(num)));
	num = Math.floor(num*100+0.50000000001);
	cents = num%100;
	num = Math.floor(num/100).toString();
	if(cents<10)
	cents = "0" + cents;
	for (var i = 0; i < Math.floor((num.length-(1+i))/3); i++)
	num = num.substring(0,num.length-(4*i+3))+','+
	num.substring(num.length-(4*i+3));
	return (((sign)?'':'-') + String.fromCharCode(162) + num);
}

function update_balance(balance_ele){

	var num = balance_ele.name.replace("investment[", "").replace("]", "")
	var keyword = $("input[name='keyword[" + num + "]']").val();
	var money = balance_ele.value
	$.lastupdated.keyword = keyword
	$.lastupdated.money = money
	$('#error').html('')
	
	var balance = total_balance;
	balance += this_investment;
	
	for(j=0; j<=i; j++)
	{
		if ($("input[name='investment[" + j + "]']").val() == "")
			continue;
			
		var value = parseInt(document.invest.elements['investment[' + j + ']'].value);
		
		if (isNaN(value) || value < 0){
			$('#error').html('You must enter a positive integer amount')
			$('#row' + j).addClass('highlight')		
		} else {
			$('#row' + j).removeClass('highlight')
		}
			
		balance -= value;
	}	
	
	if (balance < 0)
		$('#balance').html('<font color="red">' + formatCurrency(balance) + '</font>')
	else
		$('#balance').html(formatCurrency(balance))
		
}


function update_keyword(keyword_ele){
	var num = keyword_ele.name.replace("keyword[", "").replace("]", "")
	var keyword = keyword_ele.value;
	var money = $("input[name='investment[" + num + "]']").val();
	$.lastupdated.keyword = keyword
	$.lastupdated.money = money
	if (keyword == ""){
		return;
	}
	
	if (keyword.indexOf(",") != -1){
		$('#error').html("You should sperate new keywords onto a new line")
		$('#row' + num).addClass('highlight')

		var new_keyword = keyword.substring(keyword.indexOf(",") + 1, keyword.length);		
		
		if (new_keyword != "")
			$('#error').append(". Click <a href='javascript: fix_keyword(" + num + ")'>here</a> to seperate " + new_keyword + " onto a new line");
	} else {
		$('#error').html('')
		$('#row' + num).removeClass('highlight')
		
	}
	
	$('#keywordlink' + num).html('<a href="/view/' + keyword.replace(/ /g, '_') + '/" target=_blank>' + keyword + '</a>')

}


function fix_keyword(num){
	var keyword = $("input[name='keyword[" + num + "]']").val();
	
	if (keyword.indexOf(",") != -1){
		$('#error').html('')
		$('#row' + num).removeClass('highlight')

		var new_keyword = keyword.substring(keyword.indexOf(",") + 1, keyword.length);		
		var old_keyword = keyword.substring(0, keyword.indexOf(","));
		$("input[name='keyword[" + num + "]']").val(old_keyword.replace(/^\s*|\s*$/g,""))
		addRow(new_keyword.replace(/^\s*|\s*$/g,""));
	}
	update_keyword($("input[name='keyword[" + num + "]']")[0]);
	
}

$(document).ready(function() {
	$.lastupdated = {
		keyword : $("input[name='keyword[" + i + "]']").val(),
		money : $("input[name='investment[" + i + "]']").val()
	}
	
	$("input[name*='keyword']").keyup(function() {update_keyword(this)})
	$("input[name*='investment']").keyup(function() {update_balance(this)})
	FB_RequireFeatures(["XFBML"], function()
	{
			FB.Facebook.init("9669d802ca3cdcc15172ccd7b4636646", "/xd_receiver.htm");
	});

	FB.Connect.get_status().waitForValue(1, function() {
		$("#invest").submit(function() {
			var comment_data = {"money": $.lastupdated.money, "site": "<a href=" + url + ">" +  title + "</a>", "link":url, "tag_raw": $.lastupdated.keyword, "tag": "<a href=http://www.tallstreet.com/view/" + $.lastupdated.keyword + ">" + $.lastupdated.keyword + "</a>"}
			FB.Connect.showFeedDialog(54707748376, comment_data, null, null, null, FB.RequireConnect.doNotRequire, function() { $("#invest").unbind("submit").submit() });
			//FB.Connect.showFeedDialog(54707748376, comment_data, null, null, null, FB.RequireConnect.require);
			return false
		});	
	})
});

