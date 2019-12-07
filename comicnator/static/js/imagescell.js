var resultado = document.getElementById('1').innerHTML;

if (!(resultado.indexOf("tu personaje") >= 0)) {
    resultado = resultado.substring(24, resultado.length);
    resultado = resultado.toLowerCase();
    resultado = resultado.replace(/ /g, "");
    resultado = resultado.substring(1, resultado.length)
    document.getElementById("personaje").src = url_for_static(resultado + ".jpg")
    document.getElementById("final").innerHTML = "No es el personaje que pensabas?";
    document.getElementById("irfinal").value = "Dime en quien pensabas";
}
else {
    document.getElementById("final").innerHTML = "No encuentras tu personaje?";
    document.getElementById("irfinal").value = "Dime en quien pensabas";
}
function imagenotfound() {
    document.getElementById("personaje").src = url_for_static("notfound.jpg")
}
