var resultado = document.getElementById('1').innerHTML;
resultado = resultado.substring(17, resultado.length - 1);

if (!(resultado.indexOf("tu personaje") >= 0)) {
    resultado = resultado.toLowerCase();
    resultado = resultado.replace(/ /g, "");
    document.getElementById("personaje").src = Flask.url_for("static", { "filename": resultado + ".jpg" });
    document.getElementById("final").innerHTML = "No es el personaje que pensabas?";
    document.getElementById("irfinal").value = "Dime en quien pensabas";
}
else {
    document.getElementById("final").innerHTML = "No encuentras tu personaje?";
    document.getElementById("irfinal").value = "Dime en quien pensabas";
}
function imagenotfound() {
    document.getElementById("personaje").src = Flask.url_for("static", { "filename": "notfound.jpg" });
}
