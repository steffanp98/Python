//config pusher
var pusher = new Pusher('3ecaba65a855b30d977a',{
    cluster:'eu',
    encrypted: true
});

var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

$(document).ready(function(){
    var dataTable = $("#dataTable").DataTable()
    var userSession = $("#userSession").DataTable()
    var userPages = $("#pages").DataTable()

    axios.get('/get-all-sessions')
    .then(Response => {
        Response.data.forEach(data => {
            insertDataTable(data)
        });
    //setting date variables which will be used for a search and to upto datatable
    var dt = new Date();
    var updatedAt = `${dt.getFullYear()}/${months[dt.getMonth()]}/${dt.getDay()} ${dt.getHours()}:${dt.getMinutes()}:${dt.getSeconds()}`
    document.getElementById('session-update-time').innerText = updatedAt
    });
    // defining the pusher channel which will send the data to the backend
    var sessionChannel = pusher.subscribe('session');
    sessionChannel.bind('new',function(data){
        insertDataTable(data)
    });

});

//defining the function to insert the data into tab;e 
function insertDataTable(data){
    var dataTable = $("#dataTable").DataTable()
    dataTable.row.add([
        data.time,
        data.ip,
        data.continent,
        data.country,
        data.city,
        data.os,
        data.browser,
        `<a href=${"/dashboard/"+data.session}>View pages visited</a>` 
    ]);
    dataTable.order([0,'desc']).draw();
}
