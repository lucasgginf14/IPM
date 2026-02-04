from model import ModeloPaciente, ModeloMedicamento, ModelPosologia, ModelIntakes, ServerStatus
from view import View, run, GPatient, GMed, Gtk, GPos, GIntake
from gi.repository import GLib
from threading import Thread
from time import sleep
from typing import Any
import threading
import gettext

_ = gettext.gettext

def threaded(funcion):
    def wrapper(*args, **kwargs):
        Thread(target=funcion, args=args, kwargs=kwargs).start()
    return wrapper

class PacientePresenter:
    def __init__(self, modelpac: ModeloPaciente, viewpac: View, modelmed: ModeloMedicamento,
                 modelpos: ModelPosologia, modelin: ModelIntakes, modelserver: ServerStatus):
        self.enfermos = modelpac
        self.verenfermos = viewpac
        self.meds = modelmed
        self.posologia = modelpos
        self.intake = modelin
        self.server = modelserver

    def run(self, application_id: str):
        self.verenfermos.set_handler(self)
        run(application_id, on_activate=self.verenfermos.on_activate)

    @threaded
    def init_list(self) -> None:
        try:
            self.verenfermos.cargando_datos()
            pacientes = self.enfermos.get_all_pacientes()
            if len(pacientes) > 0:
                GLib.idle_add(self.verenfermos.set_pacientes , pacientes)
                GLib.idle_add(self.verenfermos.construir_busqueda, "")
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("No hay pacientes"))
                GLib.idle_add(self.verenfermos.construir_busqueda, "")
        except Exception as e:
            GLib.idle_add(self.verenfermos.mensaje_pop_up, str(e))
            GLib.idle_add(self.verenfermos.construir_busqueda, "")

    @threaded
    def list_by_query(self, query: str) -> None:
        try:
            self.verenfermos.cargando_datos()
            pacientes_found = self.enfermos.get_paciente_by_query(query)
            if len(pacientes_found) > 0:
                GLib.idle_add(self.verenfermos.set_pacientes, pacientes_found)
                GLib.idle_add(self.verenfermos.construir_busqueda, query)
            else:
                GLib.idle_add(self.verenfermos.not_found)
                GLib.idle_add(self.verenfermos.construir_busqueda, query)
        except Exception as e:
            GLib.idle_add(self.verenfermos.mensaje_pop_up, str(e))
            GLib.idle_add(self.verenfermos.construir_busqueda, "")

    @threaded
    def fill_meds_list(self, enfermo: GPatient):
        try:
            self.verenfermos.cargando_datos()
            self.verenfermos.datameds.remove_all()
            meds = self.meds.get_all_meds_paciente(self=self, id=enfermo.id)
            for empastillado in meds:
                GLib.idle_add(self.verenfermos.datameds.append, GMed(empastillado.name, empastillado.dosage, empastillado.treatment_duration, empastillado.id, empastillado.start_date, empastillado.patient_id))
            GLib.idle_add(self.verenfermos.ejecutar_construcion, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_buscador)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, str(e))

    @threaded
    def on_patient_selected(self, enfermo: GPatient) -> None:
        try:
            self.verenfermos.cargando_datos()
            if self.server.is_server_down():
                GLib.idle_add(self.verenfermos.volver_a_buscador)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("El servidor está caído"))
            else:
                GLib.idle_add(self.verenfermos.construir_vista_paciente, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_buscador)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error con el perfil del paciente: ") + str(e))

    def on_buscar_clicked(self, query: str) -> None:
        try:
            self.verenfermos.actualize_list(query)
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error búsqueda: ") + str(e))

    def on_campo_modificado(self, query: str) -> None:
        try:
            self.verenfermos.actualize_list(query)
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error campo búsqueda: ") + str(e))

    def on_entry_modify(self, guardar: Gtk.Button) -> None:
        try:
            guardar.show()
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error editando: ") + str(e))

    def volver_a_buscador(self) -> None:
        try:
            self.verenfermos.volver_a_buscador()
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error al volver al buscador: ") + str(e))

    @threaded
    def volver_a_meds(self, enfermo: GPatient) -> None:
        try:
            self.verenfermos.cargando_datos()
            self.verenfermos.datameds.remove_all()
            meds = self.meds.get_all_meds_paciente(self=self, id=enfermo.id)
            for empastillado in meds:
                GLib.idle_add(self.verenfermos.datameds.append, GMed(empastillado.name, empastillado.dosage, empastillado.treatment_duration, empastillado.id, empastillado.start_date, empastillado.patient_id))
            GLib.idle_add(self.verenfermos.volver_a_meds)
            GLib.idle_add(self.verenfermos.construir_vista_paciente, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error al volver a los medicamentos: ") + str(e))

    @threaded
    def volver_a_edit(self, enfermo: GPatient) -> None:
        try:
            self.verenfermos.cargando_datos()
            self.verenfermos.datameds.remove_all()
            meds = self.meds.get_all_meds_paciente(self=self, id=enfermo.id)
            for empastillado in meds:
                GLib.idle_add(self.verenfermos.datameds.append,
                    GMed(empastillado.name, empastillado.dosage, empastillado.treatment_duration, empastillado.id,
                         empastillado.start_date, empastillado.patient_id))
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error al volver a la edición: ") + str(e))

    def on_edit_clicked(self, enfermo: GPatient) -> None:
        try:
            self.verenfermos.construir_vista_edit(enfermo)
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error al mostrar la vista de edición: ") + str(e))

    @threaded
    def delete_med(self, pastilla_id: int, enfermo: GPatient) -> None:
        try:
            self.verenfermos.cargando_datos()
            if self.meds.delete_meds_paciente(self=self, id=enfermo.id, medication_id=pastilla_id):
                self.verenfermos.datameds.remove_all()
                meds = self.meds.get_all_meds_paciente(self=self, id=enfermo.id)
                for empastillado in meds:
                    self.verenfermos.datameds.append(
                        GMed(empastillado.name, empastillado.dosage, empastillado.treatment_duration, empastillado.id,
                             empastillado.start_date, empastillado.patient_id))
                GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("El medicamento fue borrado correctamente en la base de datos!"))
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("ERROR = No se pudo realizar el borrado!"))
                GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error borrando el medicamento: ") + str(e))

    def on_add_clicked(self, enfermo: GPatient) -> None:
        try:
            self.verenfermos.construir_vista_add(enfermo)
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error al añadir el medicamento: ") + str(e))

    @threaded
    def on_add_confirmed(self, name: str, dosage: int, treatment_duration: int, start_date: str, enfermo: GPatient):
        try:
            self.verenfermos.cargando_datos()
            if self.meds.add_meds_paciente(self=self, name=name, dosage=dosage, treatment_duration=treatment_duration, start_date=start_date, patient_id=enfermo.id):
                self.verenfermos.datameds.remove_all()
                meds = self.meds.get_all_meds_paciente(self=self, id=enfermo.id)
                for empastillado in meds:
                    self.verenfermos.datameds.append(
                        GMed(empastillado.name, empastillado.dosage, empastillado.treatment_duration, empastillado.id,
                             empastillado.start_date, empastillado.patient_id))
                GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Se añadió correctamente"))
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("No se ha podido añadir!"))
                GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error añadiendo: ") + str(e))

    @threaded
    def guardar_med(self, pastilla: GMed, enfermo: GPatient, name: str, dosage: str, tratamient: str) -> None:
        try:
            self.verenfermos.cargando_datos()
            if self.meds.edit_meds_paciente(self=self, name=name, dosage=dosage, treatment_duration=tratamient, id=pastilla.id, start_date=pastilla.start_date, patient_id=enfermo.id):
                self.verenfermos.datameds.remove_all()
                meds = self.meds.get_all_meds_paciente(self=self, id=enfermo.id)
                for empastillado in meds:
                    self.verenfermos.datameds.append(
                        GMed(empastillado.name, empastillado.dosage, empastillado.treatment_duration, empastillado.id,
                             empastillado.start_date, empastillado.patient_id))
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Guardado correctamente!"))
                GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("No se ha podido guardar!"))
                GLib.idle_add(self.verenfermos.construir_vista_edit, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error guardando valores: ") + str(e))

    @threaded
    def mostrar_posin_edit(self, pastilla: GMed, chuzao: GPatient):
        try:
            self.verenfermos.cargando_datos()
            posologias = self.posologia.get_posologias(self=self, patient_id=chuzao.id, medication_id=pastilla.id)
            intakes = self.intake.get_intakes_by_patient_and_medication(patient_id=chuzao.id, medication_id=pastilla.id)
            GLib.idle_add(self.verenfermos.set_posologies, posologias)
            GLib.idle_add(self.verenfermos.set_intakes, intakes)
            GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, pastilla.id, chuzao)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error mostrando edit Posologías e Ingestas: ") + str(e))

    @threaded
    def mostrar_posin(self, cell, path, pastilla: GMed, chuzao:GPatient):
        try:
            self.verenfermos.cargando_datos()
            posologias = self.posologia.get_posologias(self=self, patient_id=chuzao.id, medication_id=pastilla.id)
            intakes = self.intake.get_intakes_by_patient_and_medication(patient_id=chuzao.id, medication_id=pastilla.id)
            GLib.idle_add(self.verenfermos.set_posologies, posologias)
            GLib.idle_add(self.verenfermos.set_intakes, intakes)
            GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes, pastilla.id, chuzao)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_meds)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error mostrando Posologías e Ingestas: ") + str(e))

    @threaded
    def fill_posologies_list(self, medication_id: int, enfermo_id: int):
        try:
            self.verenfermos.cargando_datos()
            posologias = self.posologia.get_posologias(self=self, patient_id=enfermo_id, medication_id=medication_id)
            GLib.idle_add(self.verenfermos.set_posologies, posologias)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error llenando la lista de Posologías: ") + str(e))

    @threaded
    def fill_intakes_list(self, medication_id: int, enfermo_id: int):
        try:
            self.verenfermos.cargando_datos()
            intakes = self.intake.get_intakes_by_patient_and_medication(patient_id=enfermo_id, medication_id=medication_id)
            GLib.idle_add(self.verenfermos.set_intakes, intakes)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error llenando la lista de Ingestas: ") + str(e))

    @threaded
    def on_borrar_posologia(self, posologia: GPos, enfermo: GPatient):
        try:
            self.verenfermos.cargando_datos()
            if self.posologia.delete_posologias(self=self, patient_id=enfermo.id, medication_id=posologia.medication_id , posologie_id=posologia.id):
                GLib.idle_add(self.fill_posologies_list, posologia.medication_id, enfermo.id)
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, posologia.medication_id, enfermo)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Borrado realizado en la base de datos!"))
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("ERROR = No se pudo realizar el borrado!"))
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, posologia.medication_id, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error borrando Posología: ") + str(e))

    @threaded
    def on_borrar_intake(self, id: int, med_id: int , enfermo: GPatient):
        try:
            self.verenfermos.cargando_datos()
            if self.intake.delete_intake(patient_id=enfermo.id, medication_id=med_id , intake_id=id):
                GLib.idle_add(self.fill_intakes_list, med_id, enfermo.id)
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, med_id, enfermo)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Borrado realizado en la base de datos!"))
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("ERROR = No se pudo realizar el borrado!"))
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, med_id, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.volver_a_edit)
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error borrando Ingesta: ") + str(e))

    @threaded
    def on_add_posologie_confirmed(self, minute: str, hour: str, medication_id: int, enfermo: GPatient):
        try:
            self.verenfermos.cargando_datos()
            if self.posologia.add_posologia(self=self, minute=int(minute), hour=int(hour), patient_id=enfermo.id, medication_id=medication_id):
                GLib.idle_add(self.fill_posologies_list, medication_id, enfermo.id)
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, medication_id, enfermo)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Se añadió correctamente"))
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("No se ha podido añadir!"))
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, medication_id, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error añadiendo posología: ") + str(e))
            GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, medication_id, enfermo)

    @threaded
    def on_add_intake_confirmed(self, enfermo: GPatient, medication_id: int, date: str):
        try:
            self.verenfermos.cargando_datos()
            if self.intake.add_intake(patient_id=enfermo.id, medication_id=medication_id, date=date):
                GLib.idle_add(self.fill_intakes_list, medication_id, enfermo.id)
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, medication_id, enfermo)
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Se añadió correctamente"))
            else:
                GLib.idle_add(self.verenfermos.mensaje_pop_up, _("No se ha podido añadir!"))
                GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, medication_id, enfermo)
        except Exception as e:
            GLib.idle_add(self.verenfermos.mensaje_pop_up, _("Error añadiendo ingesta: ") + str(e))
            GLib.idle_add(self.verenfermos.construir_vista_posologias_intakes_edit, medication_id, enfermo)

    def on_add_posologie_clicked(self, enfermo: GPatient, medication_id: int):
        try:
            self.verenfermos.construir_vista_add_posologia(enfermo, medication_id)
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error añadiendo posología: ") + str(e))

    def on_add_intake_clicked(self, enfermo: GPatient, medication_id: int):
        try:
            self.verenfermos.construir_vista_add_intake(enfermo, medication_id)
        except Exception as e:
            self.verenfermos.mensaje_pop_up(_("Error añadiendo ingesta: ") + str(e))