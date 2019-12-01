function sendjson() {
    var formData = {
        'probabilidad': [0, 0, 0, 0],
        'exclusion': [0, 0, 0, 0]
    }
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: "/pruebajson",
        data: JSON.stringify(formData),
        success: console.log("listo"),
        dataType: 'json'
    });
}