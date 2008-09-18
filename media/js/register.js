
function validate_username() {	
	document.forms['validate']['command'].value = 'validate_username';
	document.forms['validate']['data'].value = document.forms['register']['username'].value;
	postForm('validate', true, function (req) { replaceDivContents(req, 'error'); if (req.responseText != '') { replaceDivClass('highlight', 'username'); } else { replaceDivClass('', 'username');  } });
}

function validate_email() {
	document.forms['validate']['command'].value = 'validate_email';
	document.forms['validate']['data'].value = document.forms['register']['email'].value;
	postForm('validate', true, function (req) { replaceDivContents(req, 'error'); if (req.responseText != '') { replaceDivClass('highlight', 'email'); } else { replaceDivClass('', 'email');} });
	
}

function validate_repeat() {
	document.forms['validate']['command'].value = 'validate_repeat';
	document.forms['validate']['data'].value = 'new_password=' + document.forms['register']['new_password'].value + '&password_confirm=' + document.forms['register']['password_confirm'].value;
	postForm('validate', true, function (req) { replaceDivContents(req, 'error'); if (req.responseText != '') { replaceDivClass('highlight', 'password_confirm'); } else { replaceDivClass('', 'password_confirm'); } });
	
}

function validate_confirm() {
	document.forms['validate']['command'].value = 'validate_confirm';
	document.forms['validate']['data'].value = 'confirm_code=' + document.forms['register']['confirm_code'].value + '&confirm_id=' + document.forms['register']['confirm_id'].value;
	postForm('validate', true, function (req) { replaceDivContents(req, 'error'); if (req.responseText != '') { replaceDivClass('highlight', 'confirm_code'); } else { replaceDivClass('', 'confirm_code'); } });
}

function validate_form() {

}
