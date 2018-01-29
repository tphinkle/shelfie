
var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");
ctx.fillStyle = "#FF0000";
ctx.fillRect(0,0,150,75);


get_submission_id = function() {
  url = window.location.href;
  console.log(url);
}

load_image = function() {
  var canvas = $('#bookshelf');
  var ctx = canvas.getContext("2d");

  var bookshelf_img = new Image();

  ctx.drawImage(bookshelf_img, 0, 0);

  ctx.fillRect(0,500,500);

  bookshelf_img.src = '/static/submissions/'

}

$(document).ready(function() {

  load_image();
  get_submission_id();

});
