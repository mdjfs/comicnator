
function disable(disabled, actions) {
    var x = document.getElementById(actions);
    if (!x.checked) {
        document.getElementById(disabled).disabled = true;
    }
    else {
        document.getElementById(disabled).disabled = false;
    }
}