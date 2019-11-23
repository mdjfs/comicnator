
var obtencion = document.getElementById("respuesta").innerHTML;
if (obtencion != "") {
    var lista = obtencion.split(".");
    document.getElementById("id").innerHTML = lista[0];
    document.getElementById("nombre").innerHTML = lista[1];
    document.getElementById("genero").innerHTML = lista[2];
    document.getElementById("origen").innerHTML = lista[3];
    document.getElementById("comienzo").innerHTML = lista[4];
    document.getElementById("capacidad").innerHTML = lista[5];
    document.getElementById("descripcion").innerHTML = lista[6];
}
else {
    document.getElementById("result").hidden = true;
    document.getElementById("response").innerHTML = "No existen sugerencias.";
    document.getElementById("acepto").hidden = true;
    document.getElementById("denego").hidden = true;
}