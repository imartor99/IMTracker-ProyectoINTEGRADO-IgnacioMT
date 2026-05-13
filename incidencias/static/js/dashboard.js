/* ========================================================
   1. VARIABLES GLOBALES Y ESTADO
   ======================================================== */
const isEnglish = window.CURRENT_LANGUAGE === "en";

const dtLanguage = isEnglish
  ? {
      processing: "Processing...",
      lengthMenu: "Show _MENU_ entries",
      zeroRecords: "No matching records found",
      emptyTable: "No data available in table",
      info: "Showing _START_ to _END_ of _TOTAL_ entries",
      infoEmpty: "Showing 0 to 0 of 0 entries",
      infoFiltered: "(filtered from _MAX_ total entries)",
      search: "Search:",
      paginate: {
        first: "First",
        last: "Last",
        next: "Next",
        previous: "Previous",
      },
    }
  : {
      processing: "Procesando...",
      lengthMenu: "Mostrar _MENU_ registros",
      zeroRecords: "No se encontraron resultados",
      emptyTable: "Ningún dato disponible en esta tabla",
      info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
      infoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
      infoFiltered: "(filtrado de un total de _MAX_ registros)",
      search: "Buscar:",
      paginate: {
        first: "Primero",
        last: "Último",
        next: "Siguiente",
        previous: "Anterior",
      },
    };

let tabla;

// FILTROS adicionales
let estadoSeleccionado = "";
let usuariosSeleccionados = [];

// BORRAR incidencias - Modal de confirmación personalizado
let borrarIncidenciaId = null;
let borrarFila = null;

/* ========================================================
   2. FUNCIONES
   ======================================================== */

// Función auxiliar para generar los botones de acción con sus clases CSS BEM y traducciones correctas
function generarBotonesAcciones(inc) {
  let acciones = '<div class="dashboard__actions">';
  const txtActualizar = isEnglish ? "Update" : "Actualizar";
  const txtAsignar = isEnglish ? "Assign" : "Asignar";
  const txtBorrar = isEnglish ? "Delete" : "Borrar";

  if (inc.puede_actualizar) {
    acciones += `
            <button class="btnActualizar dashboard__action-btn dashboard__action-btn--edit" data-id="${inc.id}">
                <i class="bi bi-pencil-square"></i> ${txtActualizar}
            </button>`;
  }

  if (inc.puede_asignar) {
    acciones += `
            <button class="btnAsignar dashboard__action-btn dashboard__action-btn--assign" data-id="${inc.id}">
                <i class="bi bi-person-plus-fill"></i> ${txtAsignar}
            </button>`;
  }

  if (inc.puede_borrar) {
    acciones += `
            <button class="btnBorrar dashboard__action-btn dashboard__action-btn--delete" data-id="${inc.id}">
                <i class="bi bi-trash3"></i> ${txtBorrar}
            </button>`;
  }

  // Botón de PDF siempre disponible para IT/Manager si lo están viendo
  acciones += `
        <a href="/incidencia/${inc.id}/pdf/" target="_blank" class="dashboard__action-btn dashboard__action-btn--pdf">
            <i class="bi bi-file-earmark-pdf-fill"></i> Ticket PDF
        </a>`;

  acciones += "</div>";
  return acciones;
}

// Mensaje de ÉXITO al crear incidencia
function mostrarMensajeFlotante(mensaje) {
  const $mensaje = $("#mensajeExito");
  $mensaje.text(mensaje).fadeIn();
  setTimeout(() => $mensaje.fadeOut(), 3000);
}

// Actualizar CONTADOR
function actualizarContador() {
  $.ajax({
    url: "/contador/",
    type: "GET",
    success: function (response) {
      $("#contador-wrapper").html(
        "<strong>Incidencias no finalizadas:</strong> " + response.contador,
      );
    },
    error: function () {
      console.error("Error al actualizar el contador");
    },
  });
}

// Función reutilizable para actualizar una fila del DataTable tras editar una incidencia
function actualizarFilaIncidencia(data) {
  // Construimos el ID esperado para la fila (ej. "incidencia-5")
  const filaId = `incidencia-${data.id}`;

  // Obtenemos el nodo DOM de la fila específica a actualizar
  const fila = document.getElementById(filaId);

  if (!fila) {
    console.warn(`No se encontró la fila con ID ${filaId}`);
    return;
  }

  // Recupera el índice de la fila tal como lo reconoce DataTables
  const rowIndex = tabla.row(fila).index();

  // Validamos que efectivamente se haya encontrado la fila en la tabla
  if (rowIndex === undefined) {
    console.warn(
      `No se pudo obtener el índice para la fila con ID ${filaId}`,
    );
    return;
  }

  // Generar botones usando la función auxiliar
  const acciones = generarBotonesAcciones(data);

  const nuevaData = [
    data.id,
    data.titulo,
    data.descripcion,
    data.usuario,
    data.estado_display,
    data.prioridad_display,
    acciones,
  ];

  // Usamos el índice real de DataTables para actualizar correctamente esa fila
  tabla.row(rowIndex).data(nuevaData).draw(false);

  const claseEstado = data.estado_display
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // Elimina acentos
    .replace(/\s+/g, "-") // Sustituye espacios por guiones
    .replace(/[^\w-]/g, ""); // Elimina caracteres especiales

  $(`#${filaId}`).removeClass().addClass(claseEstado);
}

// Modal para VISTA de incidencia y ACTUALIZAR
function abrirModalDetalle(incidenciaId) {
  $.get(`/incidencia/${incidenciaId}/detalle/`, function (response) {
    if (response.success) {
      const data = response.data;
      const modalContent = $("#modalDetalleIncidencia .modal-card__body");

      modalContent.attr("data-incidencia-id", data.id); // Asigna el ID de la incidencia al modal cada vez que se abre
      $("#detalleTitulo")
        .val(data.titulo)
        .prop("readonly", !data.puede_editar_titulo); //.prop accede a las propiedades del objeto/s que genera el navegador al procesar el HTML(DOM)
      $("#detalleDescripcion")
        .val(data.descripcion)
        .prop("readonly", !data.puede_editar_descripcion);
      $("#detalleUsuario").text(data.usuario);
      $("#detalleObservacion").val(data.observacion || "");

      if (data.puede_cambiar_estado) {
        $("#detalleEstadoSelect").val(data.estado).show();
        $("#detalleEstadoSelect")
          .off("change")
          .on("change", function () {
            const estadoSeleccionado = $(this).val();
            if (
              estadoSeleccionado === "faltan_datos" ||
              estadoSeleccionado === "finalizada"
            ) {
              $("#grupoObservacion").show();
            } else {
              $("#grupoObservacion").hide();
              $("#detalleObservacion").val("");
            }
          });

        // Ejecutar al cargar el modal por si ya está en esos estados
        $("#detalleEstadoSelect").trigger("change");
        $("#detalleEstadoTexto").hide();
      } else {
        $("#detalleEstadoTexto").text(data.estado_display).show();
        $("#detalleEstadoSelect").hide();
      }

      if (data.puede_cambiar_prioridad) {
        $("#detallePrioridadSelect").val(data.prioridad).show();
        $("#detallePrioridadTexto").hide();
      } else {
        $("#detallePrioridadTexto").text(data.prioridad_display).show();
        $("#detallePrioridadSelect").hide();
      }

      // Lógica de Inteligencia Artificial (n8n + Ollama)
      if (data.resumen_ia) {
        $("#grupoIA").removeClass("modal-card__field--hidden");
        $("#detalleResumenIA").text(data.resumen_ia);
        
        // Capitalizar la primera letra para que quede bien ("Alta", "Media", "Baja")
        const prioridadIADisplay = data.prioridad_sugerida_ia 
          ? data.prioridad_sugerida_ia.charAt(0).toUpperCase() + data.prioridad_sugerida_ia.slice(1) 
          : "Desconocida";
          
        $("#detallePrioridadIA").text(prioridadIADisplay);

        // Mostrar aviso si hay discrepancia entre la prioridad del usuario y la sugerida por la IA
        if (data.prioridad_sugerida_ia && data.prioridad !== data.prioridad_sugerida_ia) {
            $("#avisoDiscrepanciaIA").removeClass("modal-card__text--hidden");
        } else {
            $("#avisoDiscrepanciaIA").addClass("modal-card__text--hidden");
        }
      } else {
        $("#grupoIA").addClass("modal-card__field--hidden");
      }

      $("#detalleFechaCreacion").text(data.fecha_creacion);
      $("#detalleFechaAsignacion").text(data.fecha_asignacion);
      $("#detalleFechaResolucion").text(data.fecha_resolucion);

      if (data.imagen_url) {
        $("#detalleImagenContenedor").html(
          `<img src="${data.imagen_url}" alt="Imagen incidencia" class="modal-card__image">`,
        );
      } else {
        $("#detalleImagenContenedor").html("<p>No hay imagen.</p>");
      }

      if (
        data.puede_editar_titulo ||
        data.puede_editar_descripcion ||
        data.puede_cambiar_estado
      ) {
        $("#btnGuardarDetalle").show();
      } else {
        $("#btnGuardarDetalle").hide();
      }

      $("#modalDetalleIncidencia").fadeIn();
    } else {
      alert("Error cargando la incidencia.");
    }
  });
}

// Obtenemos la lista de usuarios de IT
function cargarUsuariosIT() {
  $.getJSON("/obtener_usuarios_filtros/", function (data) {
    data.usuarios.forEach(function (usuario) {
      $("#filtrosUsuarios").append(
        `<button class="filtro-usuario" data-id="${usuario.id}">${usuario.first_name} ${usuario.last_name}</button>`,
      );
    });
  });
}

// Funcion que realiza la llamada ajax en funcion de los filtros activos
function aplicarFiltros() {
  $.ajax({
    url: "/filtrar_incidencias/",
    type: "GET",
    data: {
      estado: estadoSeleccionado,
      usuarios: usuariosSeleccionados,
    },
    traditional: true, //Esta opción le dice a jQuery cómo serializar los arrays en la URL cuando haces peticiones GET, asi django los reconoce bien
    success: function (response) {
      if (response.success) {
        tabla.clear();

        response.incidencias.forEach((inc) => {
          // Generar botones usando la función auxiliar
          let acciones = generarBotonesAcciones(inc);

          tabla.row.add([
            inc.id,
            inc.titulo,
            inc.descripcion,
            inc.usuario,
            inc.estado_display,
            inc.prioridad_display,
            acciones,
          ]);
        });

        tabla.draw();
        actualizarContador();
      }
    },
    error: function () {
      console.error("Error al aplicar los filtros.");
    },
  });
}

// Configurar CSRF desde las cookies (funciona automáticamente para todos los $.ajax())
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/* ========================================================
   3. EVENTOS Y MAIN
   ======================================================== */

// Función que agrupa todos los Listeners del DOM
function configurarEventos() {
  // Mostrar modal
  $("#btnAbrirModal").click(() => $("#modalIncidencia").fadeIn());

  // Cerrar modal
  $("#btnCerrarModal").click(() => {
    $("#modalIncidencia").fadeOut();
    $("#formIncidencia")[0].reset();
    $("#errores").html("");
  });

  // ENVIAR INCIDENCIA por AJAX (con CSRF y sin recargar la página)
  $("#formIncidencia").submit(function (e) {
    e.preventDefault();

    const formData = new FormData(this); // crea los datos del formulario incluyendo archivos

    $.ajax({
      url: "/crear_incidencia_ajax/", //url a la que se envia petición
      type: "POST", //método de petición
      data: formData, // datos a enviar
      processData: false, // Si no pongo estas dos ultimas propiedades , jQuery intenta convertir el formData a un string
      contentType: false, // y Django no podra procesar los datos correctamente
      success: function (response) {
        if (response.success) {
          const inc = response.data;

          // Generar botones usando la función auxiliar
          let acciones = generarBotonesAcciones(inc);

          const fila = [
            inc.id,
            inc.titulo,
            inc.descripcion,
            inc.usuario,
            inc.estado_display,
            inc.prioridad_display,
            acciones,
          ];

          const nuevaFila = tabla.row.add(fila).draw(false).node(); //false en .draw evita que cambie de pagina en la tabla. Con .node nos devuelve el elemento HTML <tr> correspondiente a la nueva fila que se acaba de añadir. Permite, por ejemplo, modificar directamente la clase o el ID de la fila recién insertada.

          const claseEstado = inc.estado_display
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/\s+/g, "-")
            .replace(/[^\w-]/g, "");

          $(nuevaFila)
            .attr("id", `incidencia-${inc.id}`)
            .removeClass()
            .addClass(claseEstado);

          $("#modalIncidencia").hide();
          $("#formIncidencia")[0].reset();
          $("#errores").html("");
          actualizarContador();
          // Selecciono el mensaje según el idioma activo
          const msg = isEnglish
            ? "Incident created successfully"
            : "Incidencia creada con éxito";
          mostrarMensajeFlotante(msg);
        } else if (response.errors) {
          let errores = "";
          for (let campo in response.errors) {
            errores += `<p><strong>${campo}:</strong> ${response.errors[campo].join(", ")}</p>`;
          }
          $("#errores").html(errores);
        } else {
          $("#errores").html("<p>Error desconocido</p>");
        }
      },
      error: function () {
        $("#errores").html("<p>Error en la comunicación con el servidor.</p>");
      },
    });
  });

  // Cerrar modal detalle/actualizar
  $("#btnCerrarDetalle").click(function () {
    $("#modalDetalleIncidencia").fadeOut();
    $("#formDetalleIncidencia")[0].reset();
    $("#modalDetalleIncidencia .modal-card__body").removeAttr(
      "data-incidencia-id",
    ); // Limpiar el ID del modal al cerrarlo
  });

  // Abrir modal de detalle desde el botón Actualizar
  $("#tablaIncidencias tbody").on("click", ".btnActualizar", function (e) {
    e.stopPropagation(); //impide que el evento se propague a elementos padres en el DOM
    const incidenciaId = $(this).data("id");
    abrirModalDetalle(incidenciaId);
  });

  // Guardar cambios del modal detalle/actualizar
  $("#formDetalleIncidencia").submit(function (e) {
    e.preventDefault();
    const incidenciaId = $("#modalDetalleIncidencia .modal-card__body").attr(
      "data-incidencia-id",
    ); // Leer el ID directamente del atributo para evitar cache de jQuery

    const estado = $("#detalleEstadoSelect").val();
    const observacion = $("#detalleObservacion").val().trim();

    //console.log("Actualizando incidencia con ID:", incidenciaId);   //DEPURACION

    $.ajax({
      url: `/incidencia/${incidenciaId}/editar/`,
      type: "POST",
      data: {
        titulo: $("#detalleTitulo").val(),
        descripcion: $("#detalleDescripcion").val(),
        estado: estado,
        observacion: observacion,
        csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
      },
      success: function (response) {
        if (response.success) {
          // Traducción de la alerta
          alert(
            isEnglish
              ? "Incident updated successfully."
              : "Incidencia actualizada correctamente.",
          );
          $("#modalDetalleIncidencia").fadeOut();

          if (response.data) {
            actualizarFilaIncidencia(response.data);

            // Actualizar el contador si el backend lo indica (al pasar hacia o desde 'finalizada')
            if (
              typeof response.actualizar_contador !== "undefined" &&
              response.actualizar_contador
            ) {
              actualizarContador();
            }
          }
        } else {
          alert("Error al actualizar: " + (response.error || ""));
        }
      },
      error: function () {
        alert("Error al enviar datos.");
      },
    });
  });

  $("#tablaIncidencias").on("click", ".btnBorrar", function () {
    borrarIncidenciaId = $(this).data("id");
    borrarFila = $(this).closest("tr");
    $("#modalConfirmarBorrar").fadeIn();
  });

  // Confirmar borrado
  $(document).on("click", "#btnConfirmarBorrar", function () {
    if (!borrarIncidenciaId) return;
    $.ajax({
      url: `/borrar_incidencia/${borrarIncidenciaId}/`,
      type: "POST",
      success: function (response) {
        if (response.success) {
          tabla.row(borrarFila).remove().draw();
          actualizarContador();
          // Traducción del mensaje flotante
          const msg = isEnglish
            ? "Incident deleted successfully"
            : "Incidencia eliminada correctamente";
          mostrarMensajeFlotante(msg);
        }
      },
      error: function () {
        alert("Error al intentar borrar la incidencia.");
      },
      complete: function () {
        $("#modalConfirmarBorrar").fadeOut();
        borrarIncidenciaId = null;
        borrarFila = null;
      }
    });
  });

  // Cancelar borrado
  $(document).on("click", "#btnCancelarBorrar, #btnCerrarBorrar", function () {
    $("#modalConfirmarBorrar").fadeOut();
    borrarIncidenciaId = null;
    borrarFila = null;
  });

  // ASIGNAR incidencias (vamos a usar AJAX pero de manera más simplificada con un atajo de jQuery)

  // Abrir modal al pulsar "Asignar"
  $("#tablaIncidencias tbody").on("click", ".btnAsignar", function () {
    let incidenciaId = $(this).data("id");
    $("#incidenciaIdAsignar").val(incidenciaId);

    // Limpiar select
    $("#selectUsuario").empty();

    // Obtener usuarios IT e incidencia ID (vemos si ya esta signada a alguien)
    $.when(
      //método de jQuery para esperar varias peticiones AJAX.
      $.getJSON("/obtener_usuarios_it/"),
      $.getJSON(`/obtener_incidencia/${incidenciaId}/`),
    )
      .done(function (usuariosData, incidenciaData) {
        //se ejecuta cuando todas las peticiones en $.when(...) han tenido éxito.
        $("#selectUsuario").empty();

        let usuarios = usuariosData[0].usuarios;
        let asignadoNombre = incidenciaData[0].asignado_a || null;

        if (usuarios.length === 0) {
          $("#selectUsuario").append(
            '<option value="">No hay usuarios disponibles</option>',
          );
        } else {
          usuarios.forEach(function (usuario) {
            let nombreCompleto =
              (usuario.first_name + " " + usuario.last_name).trim() ||
              usuario.username;
            let seleccionado =
              nombreCompleto === asignadoNombre ? "selected" : "";
            $("#selectUsuario").append(
              `<option value="${usuario.id}" ${seleccionado}>${nombreCompleto}</option>`,
            );
          });

          // Si no hay asignado, añadir opción vacía para desasignar
          if (!asignadoNombre) {
            $("#selectUsuario").prepend(
              '<option value="" selected>Sin asignar</option>',
            ); //prepend inserta contenido al principio de un elemento HTML o DOM.
          }
        }

        // Mostrar modal
        $("#modalAsignar").fadeIn();
      })
      .fail(function () {
        alert("Error al cargar usuarios o incidencia.");
        $("#modalAsignar").fadeOut();
      });
  });

  // Enviar asignación
  $("#formAsignar").submit(function (e) {
    e.preventDefault();
    let formData = $(this).serialize();

    $.post("/asignar_incidencia/", formData, function (response) {
      if (response.success) {
        // Traducción del mensaje flotante
        const msg = isEnglish
          ? "Incident assigned successfully"
          : "Incidencia asignada correctamente";
        mostrarMensajeFlotante(msg);
        $("#modalAsignar").fadeOut();

        // Redibuja la fila si el backend devuelve data
        if (response.data) {
          actualizarFilaIncidencia(response.data);
        }
      } else {
        alert("Error: " + response.error);
      }
    });
  });

  // Aplicar filtros estado
  $(document).on("click", ".filtro-estado", function () {
    $(".filtro-estado").removeClass("activo");
    $(this).addClass("activo");
    estadoSeleccionado = $(this).data("estado");
    aplicarFiltros();
  });

  // Aplicar filtros de usuario(te muestra a quien está asignada la incidencia)
  $(document).on("click", ".filtro-usuario", function () {
    const id = $(this).data("id");
    $(this).toggleClass("activo");
    if ($(this).hasClass("activo")) {
      usuariosSeleccionados.push(id);
    } else {
      usuariosSeleccionados = usuariosSeleccionados.filter((uid) => uid !== id);
    }
    aplicarFiltros();
  });
}

// Consultar API de festivos nacionales (Nager.Date)
function consultarFestivos() {
  $.get("/api/festivos/", function (data) {
    // Si hoy es festivo, muestro el banner de aviso
    if (data.es_festivo) {
      const texto = isEnglish
        ? `Today is a public holiday (${data.nombre_festivo}). Response times may be longer than usual.`
        : `Hoy es festivo (${data.nombre_festivo}). Los tiempos de respuesta podrían ser más largos de lo habitual.`;
      $("#bannerFestivo").text(texto).fadeIn();
    }

    // Muestro los próximos festivos en la sidebar
    if (data.proximos_festivos && data.proximos_festivos.length > 0) {
      let html = "";
      data.proximos_festivos.forEach(function (f) {
        html += `<li><strong>${f.fecha}</strong> — ${f.nombre}</li>`;
      });
      $("#listaFestivos").html(html);
      $("#seccionFestivos").fadeIn();
    }
  });
}

const main = () => {
  // 1. Configurar seguridad AJAX
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      const csrfSafeMethod = /^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type); //Solo añade el token si el método no es seguro (POST, PUT, DELETE, etc.).
      if (!csrfSafeMethod && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
      }
    },
  });

  // 2. Inicializar datatable y configuro el lenguaje en español/inglés dinámicamente
  tabla = $("#tablaIncidencias").DataTable({
    // He pasado la configuración dinámica dtLanguage al parámetro 'language' de DataTable
    language: dtLanguage,
    scrollX: true, // Permite scroll horizontal en móviles

    // Cada vez que redibuje la tabla(paginacion,recarga...)mantiene estilos css definidos por mi
    createdRow: function (row, data, dataIndex) {
      // data[4] es el estado mostrado en la tabla: 'Pendiente', 'En curso', 'Resuelta'
      let estado = data[4].toLowerCase().replace(/\s+/g, "-"); // "En curso" -> "en-curso"
      const id = data[0];
      $(row).addClass(estado).attr("id", `incidencia-${id}`);
    },
  });

  // 3. Cargar datos iniciales
  cargarUsuariosIT();

  // 4. Activar los listeners del DOM
  configurarEventos();

  // 5. Consultar festivos nacionales (API externa Nager.Date)
  consultarFestivos();
};

document.addEventListener("DOMContentLoaded", main);
