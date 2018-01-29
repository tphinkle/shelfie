get_submission_id = function() {
  var url = window.location.href;
  var submission_id = url.split('/')[3];

  console.log(submission_id);
}

load_image = function() {
  var canvas = document.getElementById('bookshelf');
  var ctx = canvas.getContext("2d");

  var bookshelf_img = new Image();

  ctx.drawImage(bookshelf_img, 0, 0);

  ctx.fillRect(0,0,500,500);

  bookshelf_img.src = '/static/submissions/'

}

$(document).ready(function() {
  get_submission_id();

  load_image();

});
