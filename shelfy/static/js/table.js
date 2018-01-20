$(document).ready(function() {
  $("#form-check-input").change(function(){
    recalculate_total_price();
  });
});



// recalculate the table sum
function recalculate_total_price(){
  console.log('asdf');

}



// Convert price to floating point number
function price_to_float(price) {
  return price.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,')
}
