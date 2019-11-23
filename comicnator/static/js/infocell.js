async function InfoMinimize() {
    if (document.getElementById("inf").hidden == false) {
        document.getElementById("title").hidden = true;
        document.getElementById("parrafo").hidden = true;
        document.getElementById("infomin").hidden = true;
        var i = 50;
        while (i > 0) {
            i -= 1;
            document.getElementById("inf").style.width = i + "%";
            document.getElementById("inf").style.height = i + "%";
            await sleep(20);
        }
        document.getElementById("go").hidden = false;
        document.getElementById("inf").hidden = true;
    }
}

async function Info() {
    if (document.getElementById("inf").hidden == true) {
        document.getElementById("inf").hidden = false;
        var i = 0;
        document.getElementById("go").hidden = true;
        while (i < 50) {
            i += 1;
            document.getElementById("inf").style.width = i + "%";
            document.getElementById("inf").style.height = i + "%";
            await sleep(20);
        }
        document.getElementById("title").hidden = false;
        document.getElementById("parrafo").hidden = false;
        document.getElementById("infomin").hidden = false;
    }
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}