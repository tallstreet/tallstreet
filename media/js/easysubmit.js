var url;
var email;
var name;
var title;
var keywords;
var description;
var directories = new Array();
var current_id = 0;
var count = 0;
var submitted = Array();
var unsubmitted = 0;
var proxy = true;

if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function(val, fromIndex) {
		if (typeof(fromIndex) != 'number') fromIndex = 0;
		for (var index = fromIndex,len = this.length; index < len; index++)
			if (this[index] == val) return index;
		return -1;
	}
}

function directory(){
	var url;
	var name;
	var pagerank;
	var submitted = false;
}

function setCookie(name, value, expires, path, domain, secure) {
  var curCookie = name + "=" + escape(value) +
      ((expires) ? "; expires=" + expires.toGMTString() : "") +
      ((path) ? "; path=" + path : "") +
      ((domain) ? "; domain=" + domain : "") +
      ((secure) ? "; secure" : "");
  document.cookie = curCookie;
}

function deleteCookie(name, path, domain) {
  if (getCookie(name)) {
    document.cookie = name + "=" +
    ((path) ? "; path=" + path : "") +
    ((domain) ? "; domain=" + domain : "") +
    "; expires=Thu, 01-Jan-70 00:00:01 GMT";
  }
}

function fixDate(date) {
  var base = new Date(0);
  var skew = base.getTime();
  if (skew > 0)
    date.setTime(date.getTime() - skew);
}

function getCookie(name) {
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  } else
    begin += 2;
  var end = document.cookie.indexOf(";", begin);
  if (end == -1)
    end = dc.length;
  return unescape(dc.substring(begin + prefix.length, end));
}

function savedetails(){
	email = document.getdetails.elements['email'].value;
	url = document.getdetails.elements['url'].value;
	name = document.getdetails.elements['name'].value;
	title = document.getdetails.elements['title'].value;
	keywords = document.getdetails.elements['keywords'].value;
	description = document.getdetails.elements['description'].value;
	
	// create an instance of the Date object
	var now = new Date();
	// fix the bug in Navigator 2.0, Macintosh
	fixDate(now);	
	now.setTime(now.getTime() + 365 * 24 * 60 * 60 * 1000);
	setCookie("easysubmit_url", url, now);	
	setCookie("easysubmit_email", email, now);	
	setCookie("easysubmit_name", name, now);	
	setCookie("easysubmit_title", title, now);	
	setCookie("easysubmit_keywords", keywords, now);	
	setCookie("easysubmit_description", description, now);	
	
	
	displaydirectory('', true);
}

function getdirectories(){
	getUrlAsync('directories.csv', parsedirectories);
}

function parsedirectories(req){
	if (req.readyState != 4 ||
			req.status != 200)
				return;
	var text = req.responseText;
	if (text != '' && directories.length == 0){
		dirs = text.split("\n");
	    for(i=0; i<dirs.length; i++){
			fields = dirs[i].split(",");
			if (fields[1] == '')
				continue;
				
			if (fields[1] == undefined)
				continue;				
				
			dir = new directory();
			dir.url = fields[1];
			dir.name = fields[0];
			dir.pagerank = fields[2];
			
			unsubmitted = unsubmitted + 1;
			directories.push(dir);
			
	    }	    
	}
	
	//alert(current_id);
	if (directories.length != count)
		current_id = 0;

	//alert(count);
	//alert(directories.length);
	// create an instance of the Date object
	var now = new Date();
	// fix the bug in Navigator 2.0, Macintosh
	fixDate(now);	
	now.setTime(now.getTime() + 365 * 24 * 60 * 60 * 1000);
	setCookie("count", directories.length, now);	
	
   	var loading = document.getElementById('numdirectories'); 
	loading.innerHTML = unsubmitted;	

}

function loaddetails(){
	email = getCookie("easysubmit_email");
	url = getCookie("easysubmit_url");
	name = getCookie("easysubmit_name");
	title = getCookie("easysubmit_title");
	keywords = getCookie("easysubmit_keywords");
	description = getCookie("easysubmit_description");
	current_id = parseInt(getCookie("current_id"));
	count = parseInt(getCookie("count"));
	
	if (email == null)
		email = '';
	if (title == null)
		title = '';
	if (name == null)
		name = '';
	if (keywords == null)
		keywords = '';
	if (description == null)
		description = '';
	if (url == null)
		url = 'http://';
	if (getCookie("current_id") == null)
		current_id = 0;		
	if (count == null)
		count = 0;		
		
	getdirectories();
	
}

function urMarkPage(){

    var data;
    
    var dir_overlay = document.getElementById("dir_overlay");	
	if (dir_overlay.contentDocument) //ns6 syntax
		data = dir_overlay.contentDocument;
	else if (dir_overlay.Document) //ie5+ syntax
		data = dir_overlay.Document;
		
   for(i=0; i<data.links.length; i++){
   		if (data.links[i].href == undefined){
   			continue;
   		}
   		if (data.getElementsByTagName('base')[0].href.substr(0,20) != data.links[i].href.substr(0,20) && data.links[i].href.substring(0, 10) != 'javascript')
   			data.links[i].target = "_blank";
		else if (data.links[i].href.substring(0, 10) != 'javascript'){
   			data.links[i].href = "javascript:parent.displaydirectory('"  + data.links[i].href + "',false)";
   		}
   }
   
   
   var keywords_array = keywords.split(',');
   
   for(i=0; i<data.forms.length; i++){
   		if (data.forms[i].action == ''){
   			data.forms[i].action = data.getElementsByTagName('base')[0].href;
   		}
	   	for(j=0; j<data.forms[i].elements.length; j++){   
	   		var field_name = data.forms[i].elements[j].name.toLowerCase();
	   		if (field_name.indexOf("title") != -1){
	   			data.forms[i].elements[j].value = title;
	   		}
	   		
	   		if (field_name.indexOf("url") != -1 || field_name.indexOf("link") != -1){
		   		if (!(field_name.indexOf("rec") != -1))
	   				data.forms[i].elements[j].value = url;
	   		}	   		
	   		
	   		if (field_name.indexOf("des") != -1){
	   			data.forms[i].elements[j].value = description;
	   		}	 
	   		
	   		if (field_name.indexOf("name") != -1 || field_name.indexOf("contact") != -1){
	   			data.forms[i].elements[j].value = name;
	   		}	 
	   		
	   		if (field_name.indexOf("email") != -1){
	   			data.forms[i].elements[j].value = email;
	   		}	 
	   		
	   		if (field_name.indexOf("keywords") != -1){
	   			data.forms[i].elements[j].value = keywords;
	   		}
	   				   		
	   		if (field_name.indexOf("cat") != -1 && data.forms[i].elements[j].type.toLowerCase().indexOf('select') != -1){
	   			done = false;
			   	for(k=0; k<data.forms[i].elements[j].length && !done; k++){ 	   
					for(l=0; l<keywords_array.length && !done; l++){ 	   	
			   			if (data.forms[i].elements[j].options[k].text.match(keywords_array[l], 'i')){	
	   						data.forms[i].elements[j].selectedIndex = k;
	   						done = true;
	   						break;
	   					}
	   				}
	   			}
	   		}	 	   			   			   			   		
	   	}
   }  

   	var loading = document.getElementById('loading'); 
	loading.innerHTML = '';

}

function displaydirectory(directory_link, first){

	directory = directories[current_id];
	if (directory_link == '')
		directory_link = directory.url;
	var body = document.getElementById('body');
	if (current_id >= directories.length){
		body.innerHTML = '<form class="form" style="width: 500px;" method="post" name="getdetails" onSubmit="savedetails(); return false;"><fieldset><legend>Finished<span></span></legend>Proudly brought to you by <a href="http://www.tallstreet.com/">Tall Street</a></form>';
		return;
	}
	
	if (directory.submitted == true)
		submitted_text = ' - (Submitted ' + (current_id + 1) + ' of ' + directories.length;
	else
		submitted_text = ' - ' + (current_id + 1) + ' of ' + unsubmitted;
	body.innerHTML = '<center><a href="javascript: displayform()">Edit Details</a><div id="title" style="width:800px"><div class="titlecenter"><div class="titleleft"><div class="titleright"><div style="float:left" id="prev"><a href="javascript: prev()"><font color=#ffffff>Prev</font></a></div><div style="float:right" id="next"><a href="javascript: next()"><font color=#ffffff>Next</font></a> &nbsp;&nbsp;</div><div style="float:center"><a target="_blank" href="' + directory_link + '"><font color=#ffffff>' + directory.name + '</font></a> PR ' + directory.pagerank + ' <span id="loading">- [Loading]</span> ' + submitted_text + '</div></div></div></div><iframe name="directory_overlay" id="dir_overlay" frameborder="0" width="800" height="600" src="easysubmit_getdirectories.php?url=' + directory_link + '&first=' + first + '"></iframe><center>';    
	
	if (current_id == 0){
		var prev = document.getElementById('prev');
		prev.innerHTML = '';	
	}	
}

function next(){
	submitted.push(directories[current_id].url);
	// create an instance of the Date object
	var now = new Date();
	// fix the bug in Navigator 2.0, Macintosh
	fixDate(now);	
	now.setTime(now.getTime() + 365 * 24 * 60 * 60 * 1000);
	setCookie("current_id", current_id, now);	
		
	current_id = current_id + 1;
	displaydirectory('', true);
}

function prev(){
	current_id = current_id - 1;
	displaydirectory('', true);
}

function displayform(){
	var body = document.getElementById('body');
	body.innerHTML = '<form class="form" style="width: 500px;" method="post" name="getdetails" onSubmit="savedetails(); return false;"><fieldset><legend>Easy Directory Submit <span></span></legend><table border=0 align=center cellpadding=4 cellspacing=0 width="400px">\n<tr><td align="right" width="180px">Name:</td><td align="left"><input name="name" type="text" size="40" value="' + name + '"></td></tr>\n<tr><td align="right" width="180px">Email:</td><td align="left"><input name="email" type="text" id="email" size="40" value="' + email + '"></td></tr>\n<tr><td align="right">URL:</td><td align="left"><input name="url" type="text" size="40" maxlength="255" value="' + url + '"></td></tr><tr><td align="right">Title:</td><td align="left"><input name="title" type="text" size="40" value="' + title + '"></td></tr><tr><td align="right">Keywords (used to choose categories, seperate by comma):</td><td align="left"><input name="keywords" type="text" size="40" value="' + keywords + '"></td></tr>\n<tr><td align="right">Description:</td><td align="left"><input name="description" type="text" size="40" value="' + description + '"></td></tr>\n</table><p align="center"><input type="submit" value="Submit"></p></form>';
}

function about(){
	loaddetails();
	var body = document.getElementById('body');
	body.innerHTML = '<form class="form" style="width: 500px;" method="post" name="about" onSubmit="displayform(); return false;"><fieldset><legend>Easy Directory Submit <span></span></legend><iframe style="float: left; margin-right: 20px" src="http://digg.com/api/diggthis.php?u=http%3A%2F%2Fdigg.com%2Fsoftware%2FEasily_submit_your_site_to_454_directories_with_this_AJAX_app_and_for_Free" height="82" width="55" frameborder="0" scrolling="no"></iframe>Manually submit your site to <span id="numdirectories">' + directories.length + '</span> directories, with the help of Easy Submit, which takes you to each directory and copies and pastes repeated information for you. <br><br><ul><li> All directories are SEO friendly and from <a href="http://info.vilesilencer.com/">info vilesilencer</a> </li><li>AJAX</li><li>No Installs</li><li>No Spyware</li><li>Free</li><li>Increase your google page rank</li></ul><BR> Proudly brought to you by <a href="http://www.tallstreet.com/">Tall Street</a> <p align="center"><input type="submit" value="Submit"></p></form>';
}

function startup(){
	about();
}
