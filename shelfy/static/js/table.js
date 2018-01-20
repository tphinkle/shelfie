$(document).ready(function () {
    console.log('loaded');
    //iterate through each row in the table
    $('tr').each(function () {
        //the value of sum needs to be reset for each row, so it has to be set inside the row loop
        var sum = 0
        //find the combat elements in the current row and sum it
        $(this).find('td').each(function () {
            var value = $(this).text();
            sum += Number(value.replace(/[^0-9/.-]+/g,""));
        });
        //set the value of currents rows sum to the total-combat element in the current row
        $('.total-price', this).html(sum);
    });
});
