
// recalculate the table sum
function recalculate_total_price(obj){
  $('#cost_table > tbody  > tr').not(":first").each(function {

    console.log($(this).$('nodeName'));
  });
  //console.log(obj.parent().parent().parent()..prop('nodeName'));
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







// Convert price to floating point number
//function price_to_float(price) {
//  return price.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,')
//}
