document.addEventListener("DOMContentLoaded", function() {
    M.AutoInit();

    // Inicializar Datepicker con formato correcto
    M.Datepicker.init(document.querySelectorAll('.datepicker'), {
        format: 'yyyy-mm',
        yearRange: 5,
        autoClose: true,
        firstDay: 1,
        container: 'body'
    });

    // Referencias a elementos
    const modalProcesando = document.getElementById("modalProcesando");
    const modalMensaje = document.getElementById("modalMensaje");
    const mensajeTitulo = document.getElementById("mensajeTitulo");
    const mensajeContenido = document.getElementById("mensajeContenido");

    function mostrarMensaje(titulo, contenido) {
        mensajeTitulo.textContent = titulo;
        mensajeContenido.innerHTML = contenido;
        M.Modal.getInstance(modalMensaje).open();
    }

    function mostrarProcesando() {
        M.Modal.getInstance(modalProcesando).open();
    }

    function ocultarProcesando() {
        M.Modal.getInstance(modalProcesando).close();
    }

    // 📌 Botón "Descargar CSV"
    document.getElementById("btnDescargar").addEventListener("click", function() {
        let fecha = document.querySelector(".datepicker").value;

        if (fecha) {
            let yyyymm = fecha.replace("-", "");
            let url = `/descargar-csv/${yyyymm}`;
            console.log("Intentando descargar:", url); // Debugging en consola

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("El archivo no existe o hubo un error en el servidor.");
                    }
                    return response.blob();
                })
                .then(blob => {
                    let enlace = document.createElement("a");
                    enlace.href = window.URL.createObjectURL(blob);
                    enlace.download = `${yyyymm}.csv`;
                    document.body.appendChild(enlace);
                    enlace.click();
                    document.body.removeChild(enlace);
                    mostrarMensaje("Descarga Completa", "El archivo se ha descargado correctamente.");
                })
                .catch(error => {
                    console.error(error);
                    mostrarMensaje("Error", "No se pudo descargar el archivo.");
                });
        } else {
            mostrarMensaje("Error", "Seleccione una fecha válida.");
        }
    });

    // 📌 Botón "Ejecutar Horas"
    document.getElementById("btnEjecutar").addEventListener("click", function() {
        mostrarProcesando();
        fetch("/ejecutar-horas", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                ocultarProcesando();
                mostrarMensaje("Proceso Completado", data.message);
            })
            .catch(error => {
                ocultarProcesando();
                mostrarMensaje("Error", "Error al ejecutar");
                console.error(error);
            });
    });

    // 📌 Botón "Ver Últimos Archivos"
    document.getElementById("btnListar").addEventListener("click", function() {
        mostrarProcesando();
        fetch("/listar-archivos")
            .then(response => response.json())
            .then(data => {
                ocultarProcesando();
                let lista = document.getElementById("listaArchivos");
                lista.innerHTML = "";

                if (data.archivos.length === 0) {
                    lista.innerHTML = "<li>No hay archivos disponibles</li>";
                } else {
                    data.archivos.forEach(archivo => {
                        let fechaFormateada = new Date(archivo.fecha).toLocaleString("es-ES", {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        });
                        let li = document.createElement("li");
                        li.innerHTML = `<strong>${archivo.nombre}</strong> - ${fechaFormateada}`;
                        lista.appendChild(li);
                    });
                }

                M.Modal.getInstance(document.getElementById("modalArchivos")).open();
            })
            .catch(error => {
                ocultarProcesando();
                mostrarMensaje("Error", "Error al listar archivos");
                console.error(error);
            });
    });
});
