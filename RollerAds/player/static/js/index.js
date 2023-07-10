
var activeTableBtn = document.getElementById('tables');
// var inactiveTableBtn = document.getElementById('inactive-table')
// console.log(activeTableBtn)

activeTableBtn.addEventListener('click', tableClick);
// inactiveTableBtn.addEventListener('click', inactiveTableClick);


function tableClick(event) {

    if (event.target.classList.contains('deactivate-btn')) {
        console.log('Deactivate Pressed');
    }
    else if (event.target.classList.contains('unload-btn')) {
        console.log('Unload Pressed');
    }
    else if (event.target.classList.contains('activate-btn')) {
        console.log('Activate Pressed');
    }
    else return

    var action = event.target.className
    var send = JSON.stringify(action.slice(action.lastIndexOf(" ") + 1));
    var action = send.slice(2, 3);
    var row = send.slice(3, -1);
    console.log(send);
    console.log(action);
    console.log(row);

    if (action == "e") {

        $.ajax({
            url: "/processAction",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(send)
        });

    }




}
