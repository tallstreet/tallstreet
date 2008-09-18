function getXmlHttpRequest()
{
	var httpRequest = null;
	try
	{
		httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
	}
	catch (e)
	{
		try
		{
			httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
		}
		catch (e)
		{
			httpRequest = null;
		}
	}
	
	if (!httpRequest && typeof XMLHttpRequest != "undefined")
	{
		httpRequest = new XMLHttpRequest();
	}
	
	return httpRequest;
}

function getUrlSync(url)
{
	return getUrl(url, false, null);
}

function getUrlAsync(url, handleStateChange)
{
	return getUrl(url, true, handleStateChange);
}


// call a url
function getUrl(url, async, handleStateChange) {
	var xmlHttpReq = getXmlHttpRequest();

	if (!xmlHttpReq)
		return;

	if (handleStateChange)
	{
		xmlHttpReq.onreadystatechange = function()
			{
				handleStateChange(xmlHttpReq);
			};
	}
	else
	{
		xmlHttpReq.onreadystatechange = function() {;}
	}

	xmlHttpReq.open("GET", url, async);
	xmlHttpReq.send(null);
}

function postUrl(url, data, async, stateChangeCallback)
{ 
	var xmlHttpReq = getXmlHttpRequest(); 

	if (!xmlHttpReq)
		return;

	xmlHttpReq.open("POST", url, async);
	xmlHttpReq.onreadystatechange = function()
		{
			stateChangeCallback(xmlHttpReq);
		};
	xmlHttpReq.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlHttpReq.send(data);
	//alert ('url: ' + url + '\ndata: ' + data);
}

function urlEncodeDict(dict)
{ 
	var result = "";
	for (var i=0; i<dict.length; i++) {
		result += "&" + encodeURIComponent(dict[i].name) + "=" + encodeURIComponent(dict[i].value);
	}
	return result;
}

function execOnSuccess(stateChangeCallback)
{
	return function(xmlHttpReq)
		{
			if (xmlHttpReq.readyState == 4 &&
					xmlHttpReq.status == 200)
				stateChangeCallback(xmlHttpReq);
			//alert(xmlHttpReq + " " + xmlHttpReq.readyState + " " + xmlHttpReq.status);
		};
}


function postFormByForm(form, async, successCallback) {
	var formVars = new Array();
	for (var i = 0; i < form.elements.length; i++)
	{
		var formElement = form.elements[i];
		
		// Special handling for checkboxes (we need an array of selected checkboxes..)!
		if(formElement.type=='checkbox' && !formElement.checked) {
			continue;
		} 
		var v=new Object;
		v.name=formElement.name;
		v.value=formElement.value;
		formVars.push(v);		
	} 
	postUrl(form.action, urlEncodeDict(formVars), async, execOnSuccess(successCallback));
}

function postForm(formName, async, successCallback)
{
	// postFormByName
	var form = document.forms[formName];
	return postFormByForm(form, async, successCallback);
}

function replaceDivContents(xmlHttpRequest, dstDivId)
{
	var dstDiv = document.getElementById(dstDivId);
	dstDiv.innerHTML = xmlHttpRequest.responseText;
}


function replaceDivClass(newClass, dstDivId)
{
	var dstDiv = document.getElementById(dstDivId);
	dstDiv.className = newClass;
}

function getUrlXMLResponseCallback(xmlHttpReq) {
	if(xmlHttpReq.responseXML == null) {
		alert("Error while processing your request.");
		return;
	}
	var root_node = getRootNode(xmlHttpReq);
	var return_code = getNodeValue(root_node, 'return_code');
	//alert("return code " + return_code);

	if(return_code == 0) {
		redirect_val = getNodeValue(root_node, 'redirect_on_success');
		if(redirect_val != null) {
			window.location=redirect_val;
		} else {
			success_message = getNodeValue(root_node, 'success_message');
			if (success_message != null) {
				alert(success_message);
			}
			if(this.successCallback != null) {
				this.successCallback(xmlHttpReq);
			}
		}
	} else {
		var error_msg = getNodeValue(root_node, 'error_message');
		if (error_msg == null || error_msg.length == 0) {
			if(return_code==2) {
				error_msg = "You must be logged in to perform this operation.";
			} else {
				error_msg = "An error occured while performing this operation.";
			}
		}
		alert(error_msg)
	}
}

function getNodeValue(obj,tag)
{
	node=obj.getElementsByTagName(tag);
	if(node!=null && node.length>0) {
		return node[0].firstChild.nodeValue;
	} else {
		return null;
	}
}

function getRootNode(xmlHttpReq) {
	return xmlHttpReq.responseXML.getElementsByTagName('root')[0];
}

function getUrlXMLResponse(url, successCallback) {
	this.successCallback = successCallback;
	this.urlResponseCallback = getUrlXMLResponseCallback;
	getUrl(url, true, execOnSuccess(this.urlResponseCallback)) 
}

function postUrlXMLResponse(url, data, successCallback) {
	this.successCallback = successCallback;
	this.urlResponseCallback = getUrlXMLResponseCallback;
	postUrl(url, data, true, execOnSuccess(this.urlResponseCallback))
}

function confirmAndPostUrlXMLResponse(url, confirmMessage, data, successCallback) {
	if (confirm(confirmMessage)) {
		postUrlXMLResponse(url, data, successCallback);
	}
}

function postFormXMLResponse(formName, successCallback) {
	this.successCallback = successCallback;
	postForm(formName, true, execOnSuccess(getUrlXMLResponseCallback))
}
