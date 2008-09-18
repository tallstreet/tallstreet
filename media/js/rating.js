var UT_RATING_IMG = '/img/star.gif';
var UT_RATING_IMG_HOVER = '/img/star_hover.gif';
var UT_RATING_IMG_HALF = '/img/star_half.gif';
var UT_RATING_IMG_BG = '/img/star_bg.gif';
var UT_RATING_IMG_REMOVED = '/img/star_removed.gif';
var loadedImage = false;

function UTRating(ratingElementId, maxStars, objectName, formName, ratingMessageId, componentSuffix, size, url_id)
{
	this.ratingElementId = ratingElementId;
	this.maxStars = maxStars;
	this.objectName = objectName;
	this.formName = formName;
	this.ratingMessageId = ratingMessageId;
	this.componentSuffix = componentSuffix;
	this.url_id = url_id;
	this.messages = new Array("Rate this site", "Spam", "Nothing special", "Worth visiting", "Pretty cool", "Awesome!");
	

	this.starTimer = null;
	this.starCount = 0;
	this.hasSet = false;

	if(size=='S') {
		UT_RATING_IMG      = '/img/star_sm.gif'
		UT_RATING_IMG_HALF = '/img/star_sm_half.gif'
		UT_RATING_IMG_BG   = '/img/star_sm_bg.gif'
	}
	
	
	if (!loadedImage){
		// pre-fetch image
		(new Image()).src = UT_RATING_IMG;
		(new Image()).src = UT_RATING_IMG_BG;
		loadedImage = true;
	}

	function showStars(starNum, skipMessageUpdate) {
		if(!this.hasSet){
		this.clearStarTimer();
		this.greyStars();
		this.colorStars(starNum);
		if(!skipMessageUpdate)
			this.setMessage(starNum);
		}
	}

	function setMessage(starNum) {
		document.getElementById(this.ratingMessageId).innerHTML = this.messages[starNum];
	}

	function colorStars(starNum) {
		for (var i=0; i < starNum; i++)
			document.getElementById('star_'  + this.componentSuffix + "_" + (i+1)).src = UT_RATING_IMG;
	}

	function greyStars() {
		for (var i=0; i < this.maxStars; i++)
			if (i <= this.starCount)
				document.getElementById('star_' + this.componentSuffix + "_"  + (i+1)).src = UT_RATING_IMG_BG; // UT_RATING_IMG_REMOVED;
			else
				document.getElementById('star_' + this.componentSuffix + "_"  + (i+1)).src = UT_RATING_IMG_BG;
	}

	function setStars(starNum) {
		if (!this.hasSet){
		this.starCount = starNum;
		this.drawStars(starNum);
		document.forms[this.formName]['rating'].value = this.starCount;
		document.forms[this.formName]['url_id'].value = this.url_id;
		var ratingElementId = this.ratingElementId;
		postForm(this.formName, true, function (req) { replaceDivContents(req, ratingElementId); });
		this.hasSet = true;
		}
	}


	function drawStars(starNum, skipMessageUpdate) {
		this.starCount=starNum;
		this.showStars(starNum, skipMessageUpdate);
	}

	function clearStars() {
		if (!this.hasSet)
		this.starTimer = setTimeout(this.objectName + ".resetStars()", 300);
	}

	function resetStars() {
		this.clearStarTimer();
		if (this.starCount)
			this.drawStars(this.starCount);
		else
			this.greyStars();
		this.setMessage(0);
	}

	function clearStarTimer() {
		if (this.starTimer) {
			clearTimeout(this.starTimer);
			this.starTimer = null;
		}
	}

	this.clearStars = clearStars;
	this.clearStarTimer = clearStarTimer;
	this.greyStars = greyStars;
	this.colorStars = colorStars;
	this.resetStars = resetStars;
	this.setStars = setStars;
	this.drawStars = drawStars;
	this.showStars = showStars;
	this.setMessage = setMessage;

}


