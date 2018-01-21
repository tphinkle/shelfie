

// Convert price to floating point number
function price_to_float(price) {
  return price.replace(/\D/g,'')/100.0;
}

function format_price(price) {
  return '$' + price.toFixed(2);
}

// recalculate the table sum
function recalculate_total_price(){
  var total_price = 0;
  $('#cost_table > tbody  > tr').each(function() {
  //$('#cost_table > tbody  > tr').not(":first").each(function() {

    // Check if item is selected
    if ($(this).children('td[name="checkbox"]').find('input').is(':checked')) {

      // If selected, update the total price
      console.log('this one is checked');
      total_price += price_to_float($(this).children('td[name="price_row"]').text());
  }

  });

 return total_price;

}

function reset_total_price(){
  var total_price = recalculate_total_price();
  var formatted_total_price = format_price(total_price);
  $('#total-label').text('Your shelf is worth at least ' + formatted_total_price);
}



$(document).ready(function() {

  console.log('page loaded');
  reset_total_price();

  // Loop over all checkboxes
  $('.form-check-input').each(function(i, obj) {
    $(this).change(function(){
      reset_total_price();
    });
  });
    // Set the callback for the checkbox
    //$(this).change(function(){
//      recalculate_total_price();
    //})


});
