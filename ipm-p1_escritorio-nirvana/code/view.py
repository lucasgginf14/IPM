from typing import Callable, Protocol, Any
from datetime import datetime
import threading
import gettext

from gi.repository import GLib
from threading import Thread

import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject

_ = gettext.gettext

def run(application_id: str, on_activate: Callable) -> None:
    app = Gtk.Application(application_id=application_id)
    app.connect('activate', on_activate)
    app.run()

class GMed(GObject.GObject):
    def __init__(self, name: str, dosage: int, treatment_duration: int, id: int, start_date: str, patient_id: int):
        super().__init__()
        self.name = name
        self.dosage = dosage
        self.treatment_duration = treatment_duration
        self.id = id
        self.start_date	= start_date
        self.patient_id = patient_id

class GPatient(GObject.GObject):
    def __init__(self, id: int, code: str, name: str, surname: str):
        super().__init__()
        self.id = id
        self.code = code
        self.name = name
        self.surname = surname

class GPos(GObject.GObject):
    def __init__(self, id: int, hour: int, minute: int, medication_id: int):
        super().__init__()
        self.id = id
        self.hour = hour
        self.minute = minute
        self.medication_id = medication_id

class GIntake(GObject.GObject):
    def __init__(self, id: int, date: datetime, medication_id: int):
        super().__init__()
        self.id = id
        self.data = date
        self.medication_id = medication_id

class ViewManejador(Protocol):
    def on_patient_selected(self, enfermo: GPatient) -> None: pass
    def on_buscar_clicked(self) -> None: pass
    def on_campo_modificado(self, query: str) -> None: pass
    def on_entry_modify(self, change: str, guardar: Gtk.Button) -> None: pass
    def on_edit_clicked(self) -> None: pass
    def on_add_clicked(self, enfermo: GPatient) -> None: pass
    def on_add_confirmed(self, name: str, dosage: int, treatment_duration: int, start_date: str, enfermo: GPatient) -> None: pass
    def on_add_posologie_clicked(self, enfermo: GPatient, medication_id: int) -> None: pass
    def on_add_intake_clicked(self, enfermo: GPatient, medication_id: int) -> None: pass
    def on_add_posologie_confirmed(self, minute: str, hour: str, medication_id: int, enfermo: GPatient, dialog: Gtk.Window) -> None: pass
    def on_add_intake_confirmed(self, enfermo: GPatient, medication_id: int, date: str) -> None: pass
    def on_borrar_posologia(self, posologia: GPos, enfermo: GPatient) -> None: pass
    def on_borrar_intake(self, id: int, med_id: int, enfermo: GPatient) -> None: pass
    def volver_a_buscador(self) -> None: pass
    def volver_a_meds(self, enfermo: GPatient) -> None: pass
    def volver_a_edit(self, enfermo: GPatient) -> None: pass
    def delete_med(self, pastilla_id: int, enfermo: GPatient) -> None: pass
    def mostrar_posin_edit(self, pastilla: GMed, chuzao: GPatient) -> None: pass
    def mostrar_posin(self, pastilla: GMed, chuzao: GPatient) -> None: pass
    def guardar_med(self, pastilla: GMed, enfermo: GPatient) -> None: pass

class View:
    def __init__(self):
        self.handler = None
        self.dataenfermos = Gio.ListStore(item_type=GPatient)
        self.datameds = Gio.ListStore(item_type=GMed)
        self.datapos = Gio.ListStore(item_type=GPos)
        self.dataintakes = Gio.ListStore(item_type=GIntake)

    #################### foking pop up!

    def mensaje_pop_up(self, msg: str) -> None:
        titulo = _("Advertencia")
        dialog = Gtk.Window(
            title=titulo, modal=True, resizable=False, transient_for=self.window)
        if len(msg) > 200:
            dialog.set_default_size(120, 120)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                      margin_top=24, margin_bottom=24, margin_start=48, margin_end=48)

        msg_translate = _(msg)

        box.append(Gtk.Label(label=msg_translate, wrap=True))

        accept_boton = Gtk.Button.new_with_label(_("Cerrar"))
        accept_boton.connect("clicked", lambda _: dialog.close())

        box.append(accept_boton)
        dialog.set_child(box)
        dialog.present()

    #################### foking pop up!

    def set_handler(self, handler: ViewManejador) -> None:
        self.handler = handler

    def on_activate(self, app: Gtk.Application) -> None:
        self.construir_ui(app)
        self.handler.init_list()

    def set_pacientes(self, pacientes: list) -> None:
        self.dataenfermos.remove_all()
        for enfermo in pacientes:
            self.dataenfermos.append(GPatient(enfermo.id, enfermo.code, enfermo.name, enfermo.surname))

    def set_posologies(self, posologies: list) -> None:
        self.datapos.remove_all()
        for posologia in posologies:
            self.datapos.append(GPos(posologia.id, posologia.hour, posologia.minute, posologia.medication_id))

    def set_intakes(self, intakes: list) -> None:
        self.dataintakes.remove_all()
        for toma in intakes:
            self.dataintakes.append(GIntake(toma.id, toma.date, toma.medication_id))

    def not_found(self) -> None:
        self.dataenfermos.remove_all()

    def actualize_list(self, query: str) -> None:
        self.handler.list_by_query(query)

    def volver_a_buscador(self) -> None:
        self.window.set_title(_(f"Lista Pacientes"))
        self.window.set_child(self.pantallaPacientes)

    def volver_a_edit(self) -> None:
        self.window.set_title(_(f"Editar Medicamentos"))
        self.window.set_child(self.pantallaEdit)

    def volver_a_meds(self) -> None:
        self.window.set_title(_(f"Medicamentos"))
        self.window.set_child(self.pantallaMeds)

    def cargando_datos(self):
        box = Gtk.Box(hexpand=True, vexpand=True)
        spinner = Gtk.Spinner(hexpand=True, vexpand=True)
        spinner.start()
        box.append(spinner)
        self.window.set_title(_(f"Cargando..."))
        self.window.set_child(box)

    def construir_ui(self, app: Gtk.Application) -> None:
        self.window = win = Gtk.ApplicationWindow(
            title= _(f"Lista Pacientes"), hexpand=True)
        win.set_default_size(1200, 600)
        app.add_window(win)
        win.connect("destroy", lambda win: win.close())
        win.present()

    def construir_vista_add_posologia(self, enfermo: GPatient, medication_id: int):
        dialog = Gtk.Window(title=_(f"Añadir Posologia"), modal=True, resizable=False, transient_for=self.window)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=15, margin_bottom=15,
                       margin_start=15, margin_end=15)

        hora_label = Gtk.Label(label=_(f"Hora:"), hexpand=True, halign=Gtk.Align.START)
        hora = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        hora.set_placeholder_text(_(f"Ejemplo: 22"))

        minuto_label = Gtk.Label(label=_(f"Minuto:"), hexpand=True, halign=Gtk.Align.START)
        minuto = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        minuto.set_placeholder_text(_(f"Ejemplo: 10"))

        aceptar = Gtk.Button(label=_(f"Aceptar"), hexpand=True)
        aceptar.connect("clicked", lambda _: self.handler.on_add_posologie_confirmed(minuto.get_text(), hora.get_text(), medication_id, enfermo))

        cerrar = Gtk.Button(label=_(f"Cerrar"), hexpand=True)
        cerrar.connect("clicked", lambda _: dialog.close())

        hora_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hora_box.append(hora_label)
        hora_box.append(hora)

        minuto_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        minuto_box.append(minuto_label)
        minuto_box.append(minuto)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, hexpand=True)
        buttons_box.append(aceptar)
        buttons_box.append(cerrar)

        vbox.append(hora_box)
        vbox.append(minuto_box)
        vbox.append(buttons_box)

        dialog.set_child(vbox)
        dialog.present()

    def construir_vista_add_intake(self, enfermo: GPatient, medication_id: int):
        dialog = Gtk.Window(title=_(f"Añadir Ingesta"), modal=True, resizable=False, transient_for=self.window)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=15, margin_bottom=15,
                       margin_start=15, margin_end=15)

        fecha_label = Gtk.Label(label=_(f"Fecha:"), hexpand=True, halign=Gtk.Align.START)
        fecha_entry = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        fecha_entry.set_placeholder_text(_(f"Ejemplo: 2024-09-01-T09:10"))

        aceptar = Gtk.Button(label=_(f"Aceptar"), hexpand=True)
        aceptar.connect("clicked", lambda _: self.handler.on_add_intake_confirmed(enfermo, medication_id, fecha_entry.get_text()))

        cerrar = Gtk.Button(label=_(f"Cerrar"), hexpand=True)
        cerrar.connect("clicked", lambda _: dialog.close())

        fecha_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        fecha_box.append(fecha_label)
        fecha_box.append(fecha_entry)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, hexpand=True)
        buttons_box.append(aceptar)
        buttons_box.append(cerrar)

        vbox.append(fecha_box)
        vbox.append(buttons_box)

        dialog.set_child(vbox)
        dialog.present()

    def construir_vista_posologias_intakes_edit(self, medication_id: int, chuzao: GPatient):

        def creando_filas_posologia(item: GPos, user_data: Any) -> Gtk.Widget:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_start=8, margin_end=8, margin_top=8, margin_bottom=8)

            identificador = _(f"ID: ")
            hora = _(f"Hora: ")
            minuto = _(f"Minuto: ")
            identificador_med = _(f"ID Medicación: ")

            box.append(Gtk.Label(label=identificador + f"{item.id}", hexpand=True))
            box.append(Gtk.Label(label=hora + f"{item.hour}", hexpand=True))
            box.append(Gtk.Label(label=minuto + f"{item.minute}", hexpand=True))
            box.append(Gtk.Label(label=identificador_med + f"{item.medication_id}", hexpand=True))
            boton = Gtk.Button(label=_(f"Borrar"), hexpand=True, halign=Gtk.Align.END)
            boton.connect("clicked", lambda _: self.handler.on_borrar_posologia(item, chuzao))
            box.append(boton)

            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.append(box)
            vbox.append(separator)
            return vbox

        def creando_filas_intake(item: GIntake, user_data: Any) -> Gtk.Widget:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_start=8, margin_end=8, margin_top=8, margin_bottom=8)

            identificador = _(f"ID: ")
            fecha = _(f"Fecha: ")
            identificador_med = _(f"ID Medicación: ")

            box.append(Gtk.Label(label=identificador + f"{item.id}", hexpand=True))
            box.append(Gtk.Label(label=fecha + f"{item.data}", hexpand=True))
            box.append(Gtk.Label(label=identificador_med + f"{item.medication_id}", hexpand=True))
            boton = Gtk.Button(label=_(f"Borrar"), hexpand=True, halign=Gtk.Align.END)
            boton.connect("clicked", lambda _: self.handler.on_borrar_intake(item.id, item.medication_id, chuzao))
            box.append(boton)

            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.append(box)
            vbox.append(separator)
            return vbox

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        grid_top = Gtk.Grid(margin_start=32, margin_end=16, margin_top=16)

        volver = Gtk.Button(label=f"<", halign=Gtk.Align.START, hexpand=True)
        volver.connect("clicked", lambda _: self.handler.volver_a_edit(chuzao))

        grid_top.attach(volver, 0, 0, 1, 1)
        main_box.append(grid_top)

        big_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label_posologias = Gtk.Label(label=_(f"Posologías"), halign=Gtk.Align.CENTER, margin_bottom=8)
        label_intakes = Gtk.Label(label=_(f"Ingestas"), halign=Gtk.Align.CENTER, margin_bottom=8)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                          margin_start=16, margin_end=16, margin_bottom=16)
        left_box.append(label_posologias)
        posologias = Gtk.ListBox(hexpand=True, vexpand=True)
        posologias.bind_model(self.datapos, creando_filas_posologia, None)
        scrolledwindow_pos = Gtk.ScrolledWindow(vexpand=True)
        scrolledwindow_pos.set_child(posologias)

        addpos = Gtk.Button(label=_(f"Añadir Posología"), halign=Gtk.Align.END, margin_top=8)
        addpos.connect("clicked", lambda _: self.handler.on_add_posologie_clicked(chuzao, medication_id))

        left_box.append(scrolledwindow_pos)
        left_box.append(addpos)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                          margin_start=16, margin_end=16, margin_bottom=16)
        right_box.append(label_intakes)
        intakes = Gtk.ListBox(hexpand=True, vexpand=True)
        intakes.bind_model(self.dataintakes, creando_filas_intake, None)
        scrolledwindow_in = Gtk.ScrolledWindow(vexpand=True)
        scrolledwindow_in.set_child(intakes)

        addin = Gtk.Button(label=_(f"Añadir Ingesta"), halign=Gtk.Align.END, margin_top=8)
        addin.connect("clicked", lambda _: self.handler.on_add_intake_clicked(chuzao, medication_id))

        right_box.append(scrolledwindow_in)
        right_box.append(addin)

        big_box.append(left_box)
        big_box.append(right_box)

        main_box.append(big_box)

        self.window.set_title(_(f"Posologías & Ingestas"))
        self.window.set_child(main_box)

    def construir_vista_posologias_intakes(self, medication_id: int, chuzao: GPatient):
        def creando_filas_posologia(item: GPos, user_data: Any) -> Gtk.Widget:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_start=8, margin_end=8, margin_top=8, margin_bottom=8)

            identificador = _(f"ID: ")
            hora = _(f"Hora: ")
            minuto = _(f"Minuto: ")
            identificador_med = _(f"ID Medicación: ")

            box.append(Gtk.Label(label=identificador + f"{item.id}", hexpand=True))
            box.append(Gtk.Label(label=hora + f"{item.hour}", hexpand=True))
            box.append(Gtk.Label(label=minuto + f"{item.minute}", hexpand=True))
            box.append(Gtk.Label(label=identificador_med + f"{item.medication_id}", hexpand=True))

            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.append(box)
            vbox.append(separator)
            return vbox

        def creando_filas_intake(item: GIntake, user_data: Any) -> Gtk.Widget:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_start=8, margin_end=8, margin_top=8, margin_bottom=8)

            identificador = _("ID: ")
            fecha = _("Fecha: ")
            identificador_med = _("ID Medicación: ")

            box.append(Gtk.Label(label=identificador + f"{item.id}", hexpand=True))
            box.append(Gtk.Label(label=fecha + f"{item.data}", hexpand=True))
            box.append(Gtk.Label(label=identificador_med + f"{item.medication_id}", hexpand=True))

            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.append(box)
            vbox.append(separator)
            return vbox

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        grid_top = Gtk.Grid(margin_start=32, margin_end=16, margin_top=16)

        volver = Gtk.Button(label=f"<", halign=Gtk.Align.START, hexpand=True)
        volver.connect("clicked", lambda _: self.handler.volver_a_meds(chuzao))

        grid_top.attach(volver, 0, 0, 1, 1)
        main_box.append(grid_top)

        big_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label_posologias = Gtk.Label(label=_(f"Posologías"), halign=Gtk.Align.CENTER, margin_bottom=8)
        label_intakes = Gtk.Label(label=_(f"Ingestas"), halign=Gtk.Align.CENTER, margin_bottom=8)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                          margin_start=16, margin_end=16, margin_bottom=16)
        left_box.append(label_posologias)
        posologias = Gtk.ListBox(hexpand=True, vexpand=True)
        posologias.bind_model(self.datapos, creando_filas_posologia, None)
        scrolledwindow_pos = Gtk.ScrolledWindow(vexpand=True)
        scrolledwindow_pos.set_child(posologias)

        left_box.append(scrolledwindow_pos)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                          margin_start=16, margin_end=16, margin_bottom=16)
        right_box.append(label_intakes)
        intakes = Gtk.ListBox(hexpand=True, vexpand=True)
        intakes.bind_model(self.dataintakes, creando_filas_intake, None)
        scrolledwindow_in = Gtk.ScrolledWindow(vexpand=True)
        scrolledwindow_in.set_child(intakes)

        right_box.append(scrolledwindow_in)

        big_box.append(left_box)
        big_box.append(right_box)

        main_box.append(big_box)

        self.window.set_title(_(f"Posologías & Ingestas"))
        self.window.set_child(main_box)

    def construir_vista_add(self, enfermo: GPatient):
        dialog = Gtk.Window(title=_(f"Add Medication"), modal=True, resizable=False, transient_for=self.window)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=15, margin_bottom=15,
                       margin_start=15, margin_end=15)

        name_label = Gtk.Label(label=_(f"Medication Name:"),hexpand=True, halign=Gtk.Align.START)
        name = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        name.set_placeholder_text(_(f"Ejemplo: CLOTRIMAZOL Polvo"))

        dosis_label = Gtk.Label(label=_(f"Dosage:"),hexpand=True, halign=Gtk.Align.START)
        dosis = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        dosis.set_placeholder_text(_(f"Ejemplo: 1.0"))

        tratamiento_label = Gtk.Label(label=_(f"Treatment:"),hexpand=True, halign=Gtk.Align.START)
        tratamiento = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        tratamiento.set_placeholder_text(_(f"Ejemplo: 94"))

        inicio_label = Gtk.Label(label=_(f"Start Date:"),hexpand=True, halign=Gtk.Align.START)
        inicio = Gtk.Entry(hexpand=True, halign=Gtk.Align.END)
        inicio.set_placeholder_text(_(f"Ejemplo: 2014-01-02"))

        aceptar = Gtk.Button(label=_(f"Aceptar"), hexpand=True)
        aceptar.connect("clicked", lambda _: self.handler.on_add_confirmed(
            name.get_text(), dosis.get_text(), tratamiento.get_text(), inicio.get_text(), enfermo))

        cerrar = Gtk.Button(label=_(f"Cerrar"), hexpand=True)
        cerrar.connect("clicked", lambda _: dialog.close())

        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        name_box.append(name_label)
        name_box.append(name)

        dosis_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        dosis_box.append(dosis_label)
        dosis_box.append(dosis)

        tratamiento_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        tratamiento_box.append(tratamiento_label)
        tratamiento_box.append(tratamiento)

        inicio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        inicio_box.append(inicio_label)
        inicio_box.append(inicio)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, hexpand=True)
        buttons_box.append(aceptar)
        buttons_box.append(cerrar)

        vbox.append(name_box)
        vbox.append(dosis_box)
        vbox.append(tratamiento_box)
        vbox.append(inicio_box)

        vbox.append(buttons_box)

        dialog.set_child(vbox)
        dialog.present()

    def construir_vista_edit(self, enfermo: GPatient) -> None:

        def llamada_aux_boton_guardar(button, row):
            pastilla = row.pastilla
            chuzao = row.chuzao
            self.handler.guardar_med(pastilla, chuzao, row.name, row.dosage, row.duration)

        def llamada_aux_boton_borrar(button, row):
            pastilla = row.pastilla
            chuzao = row.chuzao
            self.handler.delete_med(pastilla.id, chuzao)

        def llamada_aux_boton_posin(button, row):
            pastilla = row.pastilla
            chuzao = row.chuzao
            self.handler.mostrar_posin_edit(pastilla, chuzao)

        def on_entry_edited(entry, row, field):
            try:
                new_text = entry.get_text()
                if new_text == "":
                    return
                if field == "dosis":
                    row.dosage = float(new_text)
                elif field == "duracion":
                    row.duration = int(new_text)
                else:
                    row.name = new_text
            except Exception as e:
                self.mensaje_pop_up(_(f"Error editando: {str(e)}"))

        editbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=16, margin_end=16, margin_top=8,
                          margin_bottom=16)
        self.pantallaEdit = editbox

        meds_listbox = Gtk.ListBox()

        cabezeras = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, hexpand=True)

        header = [_("\t\t      Nombre"), _("\t\t\t\t\t   Dosis"), _("\t\t\t\t\tDuracion"), _("\t\t    Fecha Inicio"), _("      Guardar"), _("\t Borrar"), _("\t Editar Posologias & Ingestas")]
        for title in header:
            nthbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, hexpand=False)
            label = Gtk.Label(label=title)
            nthbox.append(label)
            cabezeras.append(nthbox)

        meds_listbox.append(cabezeras)

        for med in self.datameds:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            name_entry = Gtk.Entry(text=med.name)
            name_entry.connect("changed", on_entry_edited, row, "nombre")
            row.append(name_entry)

            dosage_entry = Gtk.Entry(text=str(med.dosage))
            dosage_entry.connect("changed", on_entry_edited, row, "dosis")
            row.append(dosage_entry)

            duration_entry = Gtk.Entry(text=str(med.treatment_duration))
            duration_entry.connect("changed", on_entry_edited, row, "duracion")
            row.append(duration_entry)

            start_date_label = Gtk.Label(label=med.start_date)
            row.append(start_date_label)

            save_button = Gtk.Button(label=_("Guardar"))
            save_button.connect("clicked", llamada_aux_boton_guardar, row)
            row.append(save_button)

            delete_button = Gtk.Button(label=_("Borrar"))
            delete_button.connect("clicked", llamada_aux_boton_borrar, row)
            row.append(delete_button)

            posin_button = Gtk.Button(label=_("Editar Posologias & Ingestas"))
            posin_button.connect("clicked", llamada_aux_boton_posin, row)
            row.append(posin_button)

            row.name = med.name
            row.dosage = med.dosage
            row.duration = med.treatment_duration
            row.pastilla = med
            row.chuzao = enfermo

            meds_listbox.append(row)

        grid_top = Gtk.Grid(margin_start=16, margin_end=16, margin_top=8, margin_bottom=32)
        paciente = Gtk.Label(
            label=_(f"Paciente:") + f"{enfermo.name} {enfermo.surname}\t" + _(f"Codigo: ") + f"{enfermo.code}\t" + _(f"ID: ") + f"{enfermo.id}",
            halign=Gtk.Align.END, hexpand=True)
        volver = Gtk.Button(label=f"<", halign=Gtk.Align.START, hexpand=True)
        volver.connect("clicked", lambda _: self.handler.volver_a_meds(enfermo=enfermo))

        add = Gtk.Button(label=_(f"Añadir"), hexpand=True, halign=Gtk.Align.END, margin_top=16, margin_end=16)
        add.connect("clicked", lambda _: self.handler.on_add_clicked(enfermo))

        grid_top.attach(volver, 0, 0, 1, 1)
        grid_top.attach(paciente, 1, 0, 1, 1)

        scrolledwindow = Gtk.ScrolledWindow(vexpand=True)
        scrolledwindow.set_child(meds_listbox)

        editbox.append(grid_top)
        editbox.append(scrolledwindow)
        editbox.append(add)

        self.window.set_title(_(f"Editar Medicamentos"))
        self.window.set_child(editbox)

    def construir_vista_paciente(self, enfermo: GPatient) -> None:

        self.handler.fill_meds_list(enfermo)

    def ejecutar_construcion(self, enfermo: GPatient) -> None:

        def llamada_aux_boton(cell, path):
            meds_iter = meds_liststore.get_iter(path)
            pastilla = meds_liststore[meds_iter][6]
            chuzao = meds_liststore[meds_iter][7]
            self.handler.mostrar_posin(cell, path, pastilla, chuzao)

        meds_liststore = Gtk.ListStore(str, float, int, int, str, int, object, object)

        for med in self.datameds:
            meds_liststore.append([med.name, med.dosage, med.treatment_duration, med.id, med.start_date, med.patient_id, med, enfermo])

        treeview = Gtk.TreeView(model=meds_liststore)
        treeview.get_selection().set_mode(Gtk.SelectionMode.NONE)

        for i, column_title in enumerate([_("Nombre"), _("Dosis"), _("Duracion"), _("ID"), _("Fecha Inicio"), _("ID de Paciente")]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            treeview.append_column(column)

        toggle_renderer = Gtk.CellRendererToggle(radio=True)
        toggle_renderer.connect("toggled", llamada_aux_boton)
        button_column = Gtk.TreeViewColumn(_("Ver Posologias & Ingestas"), toggle_renderer)
        treeview.append_column(button_column)

        Medsbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=16, margin_end=16, margin_top=8,
                          margin_bottom=16)
        self.pantallaMeds = Medsbox

        grid_top = Gtk.Grid(margin_start=16, margin_end=16, margin_top=8, margin_bottom=32)

        paciente = Gtk.Label(
            label=_(f"Paciente:") + f"{enfermo.name} {enfermo.surname}\t" + _(f"Codigo: ") + f"{enfermo.code}\t" + _(f"ID: ") + f"{enfermo.id}",
            halign=Gtk.Align.END, hexpand=True)
        volver = Gtk.Button(label=f"<", halign=Gtk.Align.START, hexpand=True)
        volver.connect("clicked", lambda _: self.handler.volver_a_buscador())

        edit = Gtk.Button(label=_(f"Editar"), hexpand=True, halign=Gtk.Align.END, margin_top=16, margin_end=16)
        edit.connect("clicked", lambda _: self.handler.on_edit_clicked(enfermo))

        grid_top.attach(volver, 0, 0, 1, 1)
        grid_top.attach(paciente, 1, 0, 1, 1)

        scrolledwindow = Gtk.ScrolledWindow(vexpand=True)
        scrolledwindow.set_child(treeview)

        Medsbox.append(grid_top)
        Medsbox.append(scrolledwindow)
        Medsbox.append(edit)

        self.window.set_title(_(f"Medicamentos"))
        self.window.set_child(Medsbox)

    def construir_busqueda(self, query: str):

        def on_create_row(item: GPatient, user_data: Any) -> Gtk.Widget:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_start=16, margin_end=16, margin_top=8, margin_bottom=8)

            nombre = _(f"Nombre:")
            codigo = _(f"Código: ")
            identificador = _(f"ID: ")


            box.append(Gtk.Label(label=nombre + f"{item.name} {item.surname}", hexpand=True, halign=Gtk.Align.START))
            box.append(Gtk.Label(label=codigo + f"{item.code}", hexpand=True, halign=Gtk.Align.CENTER))
            box.append(Gtk.Label(label=identificador + f"{item.id}", hexpand=True, halign=Gtk.Align.END))
            boton = Gtk.Button(label=_(f"Ver"), hexpand=True, halign=Gtk.Align.END)
            boton.connect("clicked", lambda _: self.handler.on_patient_selected(item))
            box.append(boton)
            return box

        patientsBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, homogeneous=False, vexpand=True, spacing=16,
            margin_start=16, margin_top=16, margin_end=16, margin_bottom=16)
        self.pantallaPacientes = patientsBox

        top_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, homogeneous=False, hexpand=True, spacing=16,
            margin_start=4, margin_top=4, margin_end=4, margin_bottom=4)
        bottom_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, homogeneous=False, vexpand=True, spacing=16,
            margin_start=0, margin_top=0, margin_end=0, margin_bottom=0)
        grid = Gtk.Grid()

        boton = Gtk.Button(label=_(f"Buscar"), hexpand=True)
        boton.connect("clicked", lambda _: self.handler.on_buscar_clicked(entry.get_text()))

        boton2 = Gtk.Button(label=_(f"Mostrar Lista Completa"), hexpand=True)
        boton2.connect("clicked", lambda _: self.handler.on_buscar_clicked(""))

        entry = Gtk.Entry(hexpand=True)
        entry.set_placeholder_text(_(f"Nombre, Apellido, Codigo..."))
        entry.connect("activate", lambda _: self.handler.on_campo_modificado(entry.get_text()))

        if query != "":
            entry.set_text(query)

        grid.attach(child=entry, column=0, row=0, width=1, height=1)
        grid.attach(child=boton, column=1, row=0, width=1, height=1)
        grid.attach(child=boton2, column=2, row=0, width=1, height=1)
        top_box.append(grid)

        self.listbox = Gtk.ListBox(hexpand=True, vexpand=True)
        self.listbox.bind_model(self.dataenfermos, on_create_row, None)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_child(self.listbox)
        bottom_box.append(scrolledwindow)

        patientsBox.append(top_box)
        patientsBox.append(bottom_box)

        self.window.set_title(_(f"Lista Pacientes"))
        self.window.set_child(patientsBox)