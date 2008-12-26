
function addRow(keyword){
	if (keyword != '' && document.invest.elements['keyword[' + i + ']'].value == ""){
		document.invest.elements['keyword[' + i + ']'].value = keyword;
	} else {
		i = i + 1;
	    var tbody = document.getElementById('keywords').getElementsByTagName("TBODY")[1];
	    var row = document.createElement("TR");
		row.setAttribute('id','row' + i); 
	    var td1 = document.createElement("TD");
		td1.setAttribute('align','right'); 
	    td1.innerHTML = '<input type="text" size="10" name="investment[' + i + ']" value="0" onkeyup="update_balance();">';
	    var td2 = document.createElement("TD");
		td2.setAttribute('align','left'); 
		td2.innerHTML = '<input type="text" size="32" maxlength="32" name="keyword[' + i + ']" value="' + keyword + '" onkeyup="update_keyword(' + i + ');">';
	    var td3 = document.createElement("TD");
		td3.setAttribute('align','left'); 
		td3.setAttribute('id','keywordlink' + i); 
		td3.innerHTML = '';
	    row.appendChild(td1);
	    row.appendChild(td2);
	    row.appendChild(td3);
	    tbody.appendChild(row);
    }
    keywords[keyword] = '';
    print_keywords();
	update_keyword(i);
}


function print_keywords(){
	var dstDiv = document.getElementById('TagCloud');
	dstDiv.innerHTML = '';
	for (tag in keywords) {
		if (typeof keywords[tag] != 'function'){
			dstDiv.innerHTML += keywords[tag];
		}
	}	
	dstDiv.innerHTML += ' &nbsp;<a href="javascript:addRow(\'\')" style="font-size: 10px; color: blue;">New Keyword</a>&nbsp;';
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

function update_balance(num){

	keyword = document.invest.elements['keyword[' + num + ']'].value;
	money = document.invest.elements['investment[' + num + ']'].value;
	var errorDiv = document.getElementById('error');
	errorDiv.innerHTML = "";
	
	var dstDiv = document.getElementById('balance');
	dstDiv.innerHTML = '';
	var balance = total_balance;
	balance += this_investment;
	
	for(j=0; j<=i; j++)
	{
		if (document.invest.elements['investment[' + j + ']'].value == "")
			continue;
			
		var value = parseInt(document.invest.elements['investment[' + j + ']'].value);
		
		if (isNaN(value)){
			var errorDiv = document.getElementById('error');
			errorDiv.innerHTML = "You must enter a positive integer amount";
			replaceDivClass('highlight', 'row' + j);			
		} else {
			replaceDivClass('', 'row' + j);			
		}
			
		balance -= value;
	}	
	
	if (balance < 0)
		dstDiv.innerHTML = '<font color="red">' + formatCurrency(balance) + '</font>';
	else
		dstDiv.innerHTML = formatCurrency(balance);
		
}


function update_keyword(num){

	keyword = document.invest.elements['keyword[' + num + ']'].value;
	if (keyword == ""){
		return;
	}
	
	if (keyword.indexOf(",") != -1){
		var errorDiv = document.getElementById('error');
		errorDiv.innerHTML = "You should sperate new keywords onto a new line";
		replaceDivClass('highlight', 'row' + num);	

		var new_keyword = keyword.substring(keyword.indexOf(",") + 1, keyword.length);		
		
		if (new_keyword != "")
			errorDiv.innerHTML += ". Click <a href='javascript: fix_keyword(" + num + ")'>here</a> to seperate " + new_keyword + " onto a new line";
	} else {

		var errorDiv = document.getElementById('error');
		errorDiv.innerHTML = "";
		replaceDivClass('', 'row' + num);		
		
	}
	
	var dstDiv = document.getElementById('keywordlink' + num);
	dstDiv.innerHTML = '<a href="/view/' + keyword.replace(/ /g, '_') + '/" target=_blank>' + keyword + '</a>';	
	
	
		
}


function fix_keyword(num){

	
	var keyword = document.invest.elements['keyword[' + num + ']'].value;
	
	if (keyword.indexOf(",") != -1){
		var dstDiv = document.getElementById('error');
		dstDiv.innerHTML = "";
		replaceDivClass('', 'row' + num);	

		var new_keyword = keyword.substring(keyword.indexOf(",") + 1, keyword.length);		
		var old_keyword = keyword.substring(0, keyword.indexOf(","));		
		document.invest.elements['keyword[' + num + ']'].value = old_keyword.replace(/^\s*|\s*$/g,"");
		addRow(new_keyword.replace(/^\s*|\s*$/g,""));
	}
	update_keyword(num);
	
}

