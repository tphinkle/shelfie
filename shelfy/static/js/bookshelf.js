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
  var bookshelf_img = new Image();

  var img_width = bookshelf_img.naturalWidth;
  var img_height = bookshelf_img.naturalHeight;

  var img_path = '/static/submissions/' + submission_id + '/raw_img/raw_img.jpg';

  console.log(img_path);

  bookshelf_img.onload = function() {

    // Get dimensions of canvas
    var canvas_height = canvas.height;
    var canvas_width = canvas.width;

    // Get scaled width of image to display
    var width = canvas_height/this.height*canvas_width;
    ctx.drawImage(bookshelf_img, 0, 0, canvas_width, canvas_height);
  }

  bookshelf_img.src = img_path;



}

$(document).ready(function() {
  var submission_id = get_submission_id();

  load_image(submission_id);

});
