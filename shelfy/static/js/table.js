$(document).ready(function() {
  $("input[type=checkbox]").change(function(){
    recalculate();
  });
}



// recalculate the table sum
function recalculate(){
    var sum = 0;

    $("input[type=checkbox]:checked").each(function(){
      sum += price_to_float($(this).attr("rel"));
    });

    alert(sum);
}



// Convert price to floating point number
function price_to_float(price) {
  return price.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,')
}
