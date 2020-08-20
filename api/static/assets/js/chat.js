// JavaScript Document

(function($){
	var inputEmail = document.querySelector('.password');
inputEmail.onkeyup = function(e) {
    var max = 1; // The maxlength you want
    if(inputEmail.value.length > max) {
      inputEmail.value = inputEmail.value.substring(0, max);
    }
};




	