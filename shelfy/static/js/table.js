

// Convert price to floating point number
function price_to_float(price) {
  return price.replace(/\D/g,'')/100.0;
}

// recalculate the table sum
function recalculate_total_price(obj){
  var total_price = 0;
  $('#cost_table > tbody  > tr').not(":first").each(function() {
    total_price += price_to_float($(this).children('td[name="price_row"]').text());
  });

  console.log(total_price);
}



$(document).ready(function() {

  console.log('page loaded');

  // Loop over all checkboxes
  $('.form-check-input').each(function(i, obj) {
    console.log('asdf');
    $(this).change(function(){
      recalculate_total_price($(this));
    });
  });
    // Set the callback for the checkbox
    //$(this).change(function(){
//      recalculate_total_price();
    //})


});
