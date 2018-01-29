function get_submission_id() {
  var url = window.location.href;
  var submission_id = url.split('/')[4];
  console.log(url);
  console.log(submission_id);

  return submission_id;
}

function load_image(submission_id) {

  // Get canvas and canvas context object
  var canvas = document.getElementById('bookshelf');


  var ctx = canvas.getContext("2d");

  // Create and draw the image
  var bookshelf_img = new Image(canvas.width, canvas.height);

  var img_path = '/static/submissions/' + submission_id + '/raw_img/raw_img.jpg';

  console.log(img_path);

  bookshelf_img.onload = function() {
    console.log(this.width);
    console.log(this.height);
    ctx.drawImage(bookshelf_img, 0, 0);
  }

  bookshelf_img.src = img_path;



}

$(document).ready(function() {
  var submission_id = get_submission_id();

  load_image(submission_id);

});
