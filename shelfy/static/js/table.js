console.log('asdf');

// Total updating function

function sum_table() {
  return 3;
  //var price = $(this).val()
  //var number = Number(price.replace(/[^0-9\.-]+/g,""));
}



$(document).ready(function() {
    console.log('Trying to do something');
    $('.form-check-input').each(
      $(this).change(function() {
        console.log('asdf');
        $('#total-label').val(sum_table());
    }));
});
