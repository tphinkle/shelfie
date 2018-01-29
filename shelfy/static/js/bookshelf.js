get_submission_id = function() {
  var url = window.location.href;
  var submission_id = url.split('/')[4];
  console.log(url);
  console.log(submission_id);

  return submission_id;
}

load_image = function(submission_id) {

  // Get canvas and canvas context object
  var canvas = document.getElementById('bookshelf');
  var ctx = canvas.getContext("2d");

  // Create and draw the image
  var bookshelf_img = new Image();
  ctx.drawImage(bookshelf_img, 0, 0);
  ctx.fillRect(0,0,500,500);
  var img_path = '/static/submissions/' + submission_id + '/raw_img/raw_img.jpg';
  bookshelf_img.src = img_path;

}

$(document).ready(function() {
  var submission_id = get_submission_id();

  load_image(submission_id);

});
