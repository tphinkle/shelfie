console.log('asdf');

// Total updating function

function sum_table() {
  console.log('123');




}



$(document).ready(function() {
    console.log('Trying to do something');
    $('.form-check-input').each(
      $(this).change(function() {


        // Loop over all of table
        var total = 0;
        var price;
        var number;

        $('#table table-hover > tbody  > tr:not(:first)').each( function(){
            console.log('zws');

            price = $('this > #price').value();

            console.log(price);

            number = Number(price.replace(/[^0-9\.-]+/g,""));
            total = total + number;
          });



        // Format the price
        total.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
        console.log(total);


        // Set value of the label to the total calculated price
        $('#total-label').val(total);
    }));
});
