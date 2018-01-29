get_submission_id = function() {
  var url = window.location.href;
  var submission_id = url.split('/')[4];
  console.log(url);
  console.log(submission_id);

  return submission_id;
}

load_image = function(submission_id) {
  var img_path = '/static/submissions/' + submission_id + '/raw_img.png';
  console.log(img_path);

  var canvas = document.getElementById('bookshelf');
  var ctx = canvas.getContext("2d");

  var bookshelf_img = new Image();

  ctx.drawImage(bookshelf_img, 0, 0);

  ctx.fillRect(0,0,500,500);

  bookshelf_img.src = '/static/submissions/' + submission_id + '/raw_img.png';

}

$(document).ready(function() {
  var submission_id = get_submission_id();

  load_image(submission_id);

});
