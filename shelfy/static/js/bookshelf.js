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

  var img_path = '../static/submissions/' + submission_id + '/raw_img/raw_img.jpeg';
  bookshelf_img.src = img_path;

  console.log(img_path);

  bookshelf_img.onload = function(){
    ctx.drawImage(bookshelf_img, bookshelf_img.width, bookshelf_img.height);
  }


}

$(document).ready(function() {
  var submission_id = get_submission_id();

  load_image(submission_id);

});
