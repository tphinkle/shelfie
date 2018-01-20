
// recalculate the table sum
function recalculate_total_price(){
  console.log('asdf');
}

$(document).ready(function() {

  console.log('page loaded');

  // Loop over all checkboxes
  $.each("#form-check-input", function(i) {

    // Set the callback for the checkbox
    //$(this).change(function(){
//      recalculate_total_price();
    //})


  });

});







// Convert price to floating point number
function price_to_float(price) {
  return price.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,')
}
