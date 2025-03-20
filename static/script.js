document.addEventListener('DOMContentLoaded', function() {
    M.Modal.init(document.querySelectorAll('.modal'));
});

function ejecutarHoras() {
    fetch('/ejecutar-horas', { method: 'POST' })
        .then(response => response.json())
        .then(data => M.toast({html: data.message, classes: 'green'}))
        .catch(error => M.toast({html: 'Error ejecutando el script', classes: 'red'}));
}

function descargarCSV() {
    let yyyymm = document.getElementById("inputYYYYMM").value;
    if (yyyymm) {
        window.location.href = "/descargar-csv/" + yyyymm;
    } else {
        M.toast({html: 'Ingrese una fecha válida', classes: 'red'});
    }
}

function mostrarArchivos() {
    fetch('/listar-archivos')
        .then(response => response.json())
        .then(data => {
            let lista = document.getElementById("listaArchivos");
            lista.innerHTML = "";
            data.archivos.forEach(archivo => {
                let li = document.createElement("li");
                li.innerHTML = `<a href="/csv_reports/${archivo}" target="_blank">${archivo}</a>`;
                lista.appendChild(li);
            });
            M.Modal.getInstance(document.getElementById("modalArchivos")).open();
        })
        .catch(error => M.toast({html: 'Error obteniendo archivos', classes: 'red'}));
}
