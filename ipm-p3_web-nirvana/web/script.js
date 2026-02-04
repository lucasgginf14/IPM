document.addEventListener("DOMContentLoaded", () => {
    const opcionesPeriodo = document.getElementById("opciones-periodo");
    const extraOpciones = document.getElementById("extra-opciones");
    const formulario = document.getElementById("formulario");

    // Validar formato del código del paciente
    const codigoPaciente = document.getElementById("codigo-paciente");
    codigoPaciente.addEventListener("input", () => {
        const errorMessage = codigoPaciente.nextElementSibling;
        if (!codigoPaciente.validity.valid) {
            errorMessage.textContent = codigoPaciente.title;
            errorMessage.setAttribute("aria-live", "polite");
        } else {
            errorMessage.textContent = "";
        }
    });

    // Mostrar opciones adicionales según período seleccionado
    opcionesPeriodo.addEventListener("change", () => {
        const selectedValue = opcionesPeriodo.value;
        extraOpciones.innerHTML = ""; // Limpiar opciones anteriores

        if (selectedValue === "ultimos-dias") {
            extraOpciones.innerHTML = `
                <label for="dias">Introduce el número de días:</label>
                <input type="number" id="dias" min="1" max="365" placeholder="Ej: 30" required aria-label="Número de días">
            `;
        } else if (selectedValue === "rango-fechas") {
            extraOpciones.innerHTML = `
                <label for="fecha-inicio">Desde:</label>
                <input type="date" id="fecha-inicio" required aria-label="Fecha de inicio">
                <label for="fecha-fin">Hasta:</label>
                <input type="date" id="fecha-fin" required aria-label="Fecha de fin">
            `;
        }
    });

    // Datos estáticos del paciente
    const paciente = {
        name: "Michael",
        code: "175-57-9412",
        id: 10,
        surname: "Sharp"
    };

    const medicacion3 = {
        name: "COLMIBE® Comprimidos",
        dosage: 0.75,
        treatment_duration: 21,
        id: 29,
        start_date: "2024-12-08",
        patient_id: 10
    };

    const posologia = {
        minute: 0,
        hour: 3,
        medication_id: 29,
        id: 77
    };

    const tomas = [
        {"id": 845, "medication_id": 29, "date": "2024-12-08T02:40"},
        {"id": 846, "medication_id": 29, "date": "2024-12-09T03:39"},
        {"id": 847, "medication_id": 29, "date": "2024-12-10T03:51"},
        {"id": 848, "medication_id": 29, "date": "2024-12-11T03:23"},
        {"id": 849, "medication_id": 29, "date": "2024-12-12T02:47"},
        {"id": 850, "medication_id": 29, "date": "2024-12-13T02:14"}
    ];

    formulario.addEventListener("submit", (event) => {
        event.preventDefault();

        const codigoIntroducido = codigoPaciente.value.trim();
        const informeSection = document.getElementById("resultado-informe");

        // Limpiar errores previos
        const errorElement = document.getElementById("codigo-error");
        if (errorElement) errorElement.remove();

        // Validar código del paciente
        if (codigoIntroducido !== paciente.code) {
            const error = document.createElement("p");
            error.id = "codigo-error";
            error.textContent = "Error: El código del paciente no coincide.";
            error.style.color = "red";
            error.setAttribute("role", "alert");
            error.setAttribute("aria-live", "assertive");
            formulario.appendChild(error);
            return;
        }

        // Mostrar información del paciente
        document.getElementById("nombre-paciente").textContent = `Nombre: ${paciente.name} ${paciente.surname}`;
        document.getElementById("codigo-paciente-info").textContent = `Código: ${paciente.code}`;
        document.getElementById("nombre-med").textContent = `Nombre Medicación: ${medicacion3.name}`;
        document.getElementById("dosis").textContent = `Dosis: ${medicacion3.dosage} mg`;
        document.getElementById("duracion-tratamiento").textContent = `Duración: ${medicacion3.treatment_duration} días`;
        document.getElementById("fecha-inicial").textContent = `Fecha inicial: ${medicacion3.start_date}`;
        document.getElementById("hora-posologia").textContent = `Hora de toma: ${posologia.hour}:${String(posologia.minute).padStart(2, '0')}`;

        // Generar lista de tomas esperadas
        const tomasLista = document.getElementById("tomas-lista");
        const erroresDesviaciones = document.getElementById("errores-lista");

        tomasLista.innerHTML = "";
        erroresDesviaciones.innerHTML = "";

        const fechaInicio = new Date(medicacion3.start_date);
        const tomasEsperadas = [];

        // Generar las tomas esperadas
        for (let i = 0; i < medicacion3.treatment_duration; i++) {
            const fechaToma = new Date(fechaInicio);
            fechaToma.setDate(fechaToma.getDate() + i);
            fechaToma.setHours(posologia.hour, posologia.minute, 0, 0);
            tomasEsperadas.push(fechaToma);
        }

        // Filtrar tomas según el período seleccionado
        const periodoSeleccionado = opcionesPeriodo.value;
        let tomasFiltradas = tomasEsperadas;

        if (periodoSeleccionado === "ultimos-dias") {
            const dias = document.getElementById("dias").value;
            if (dias) {
                const fechaLimite = new Date();
                fechaLimite.setDate(fechaLimite.getDate() - dias);
                tomasFiltradas = tomasEsperadas.filter(toma => toma >= fechaLimite);
            }
        } else if (periodoSeleccionado === "rango-fechas") {
            const fechaInicioFiltrado = new Date(document.getElementById("fecha-inicio").value);
            const fechaFinFiltrado = new Date(document.getElementById("fecha-fin").value);
            tomasFiltradas = tomasEsperadas.filter(toma =>
                toma >= fechaInicioFiltrado && toma <= fechaFinFiltrado
            );
        }

		// Comparar tomas esperadas con tomas realizadas
		const tomasRealizadas = tomas.map(toma => new Date(toma.date));

		tomasFiltradas.forEach((esperada) => {
			// Buscar una toma realizada que coincida con el mismo día (sin importar la hora)
			const tomaRealizada = tomasRealizadas.find(realizada =>
				realizada.toDateString() === esperada.toDateString() // Comparamos solo por el día
			);

			const li = document.createElement("li");

			if (tomaRealizada) {
				// Si la toma se realizó, calculamos la desviación
				const diferencia = Math.abs(tomaRealizada - esperada);
				const desviacionHoras = Math.floor(diferencia / (1000 * 60 * 60)); // horas
				const desviacionMinutos = Math.floor((diferencia % (1000 * 60 * 60)) / (1000 * 60)); // minutos
				
				let mensaje = `✅ Toma realizada: ${tomaRealizada.toLocaleDateString("es-ES")} ${tomaRealizada.toLocaleTimeString("es-ES")}`;
				
				// Si hay desviación, lo indicamos
				if (desviacionHoras > 0 || desviacionMinutos > 0) {
				    mensaje += ` (Desviación: ${desviacionHoras} horas y ${desviacionMinutos} minutos respecto a la hora esperada)`;
				}

				li.textContent = mensaje;
				tomasLista.appendChild(li);
			} else {
				// Si no se realizó la toma, mostramos la toma esperada y un mensaje de error
				const fechaActual = new Date();
				if (esperada < fechaActual) {
				    // Crear un mensaje de error para las tomas no realizadas
				    const error = document.createElement("li");
				    error.textContent = `❌ No se registró la toma esperada el ${esperada.toLocaleDateString("es-ES")}`;
				    erroresDesviaciones.appendChild(error);
				}
			}
		});


        // Mostrar la sección de informe
        informeSection.setAttribute("aria-live", "polite");
        informeSection.style.display = "block";
    });
});

