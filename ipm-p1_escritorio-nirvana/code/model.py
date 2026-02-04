from time import sleep
import requests

SERVER_URL = "http://localhost:8000"

class ExcepcionModelo(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class Paciente:
    def __init__(self, data=None):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)

class ServerStatus:
    def __init__(self):
        pass

    def is_server_down(self) -> bool:
        response = requests.get("http://localhost:8000/patients", timeout=5)
        if response.ok:
            return response.status_code != 200
        else:
            raise ExcepcionModelo(response.json()["detail"])

class ModeloPaciente:

    def __init__(self):
        pass

    def get_all_pacientes(self) -> list:

        sleep(3)

        url = f"{SERVER_URL}/patients"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            lista_pacientes = []
            for datos in dataRecibida:
                lista_pacientes.append(Paciente(datos))
            return lista_pacientes
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

    #   asumo que se formatean los terminos de busqueda en la capa suerior
    #   talvez mirar de poder hacer un metodo que dependiendo si tiene argumentos o no
    #   devuelva la lista de todos los pacientes o solo el peciente elegido

    #   cambiar as condicions de busqueda para q poidas meter varios campos a vez e tal
    def get_paciente_by_query(self, query: str) -> list:

        sleep(3)

        def filtrar_pacientes(pacientes_data: list, query: str) -> list:
            query_lower = query.lower()
            lista_pacientes = []

            for datos in pacientes_data:
                paciente = Paciente(datos)
                campos = vars(paciente)

                nombre = campos["name"].lower()
                apellido = campos["surname"].lower()
                codigo = campos["code"].lower()

                query_terms = query_lower.split()

                if any(term in nombre for term in query_terms) or any(term in apellido for term in query_terms) or any(term in codigo for term in query_terms):
                    lista_pacientes.append(paciente)

            return lista_pacientes

        url = f"{SERVER_URL}/patients"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            if query != "":
                return filtrar_pacientes(dataRecibida, query)
            else:
                return self.get_all_pacientes()
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

#el code es el que sirve para evitar duplicados en la base de datos y la respuesta que da es la 409 si es q existe un conflicto
    def add_paciente(self, name: str, surname: str, code: str) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients"
        newdatos = {"name" : name, "surname" : surname, "code" : code} ###comprobar si se añade solo el id
        respuesta = requests.post(url, json = newdatos)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

#se debe de mostrar el id por pantalla a la hora de buscar
    def edit_paciente(self, name: str, surname: str, code: str, id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{id}"
        editdatos = {"name" : name, "surname" : surname, "code" : code, "id" : id}
        respuesta = requests.patch(url, json = editdatos)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

    def delete_paciente(self, id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{id}"
        respuesta = requests.delete(url)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

class Medicamento:
    def __init__(self, data=None):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)

class ModeloMedicamento:

    def __init__(self):
        pass

    def get_all_meds_paciente(self, id: int) -> list:

        sleep(3)

        url = f"{SERVER_URL}/patients/{id}/medications"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            lista_meds = []
            for datos in dataRecibida:
                lista_meds.append(Medicamento(datos))
            return lista_meds
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

    def get_meds_paciente(self, idPaciente:int , idMedicamiento: int) -> Medicamento:

        sleep(3)

        url = f"{SERVER_URL}/patients/{idPaciente}/medications/{idMedicamiento}"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            return Medicamento(dataRecibida)
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

    def add_meds_paciente(self, name: str, dosage: int, treatment_duration: int, start_date: str, patient_id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications"
        newdatos = {"name": name, "dosage": dosage, "treatment_duration": treatment_duration, "start_date": start_date, "patient_id": patient_id}
        respuesta = requests.post(url, json=newdatos)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

    def edit_meds_paciente(self, name: str, dosage: int, treatment_duration: int, id: int, start_date: str, patient_id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{id}"
        newdatos = {"name": name, "dosage": dosage, "treatment_duration": treatment_duration, "start_date": start_date, "patient_id": patient_id}
        respuesta = requests.patch(url, json=newdatos)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

    def delete_meds_paciente(self, id: int, medication_id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{id}/medications/{medication_id}"
        respuesta = requests.delete(url)
        if respuesta.ok:
            return True
        else:
            datosres = respuesta.json()
            raise ExcepcionModelo(datosres["detail"])

class Posologia:
    def __init__(self, data=None):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)

class ModelPosologia:

    def __init__(self):
        pass

    def add_posologia(self, minute: int, hour: int, patient_id:int, medication_id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{medication_id}/posologies"
        newdatos = {"minute": minute, "hour": hour, "medication_id":medication_id}
        respuesta = requests.post(url, json = newdatos)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

    def get_posologias(self, patient_id: int, medication_id: int) -> list:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{medication_id}/posologies"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            lista_posologias = []
            for datos in dataRecibida:
                lista_posologias.append(Posologia(datos))
            return lista_posologias
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

    def delete_posologias(self, patient_id: int, medication_id: int, posologie_id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{medication_id}/posologies/{posologie_id}"
        respuesta = requests.delete(url)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

class Intake:
    def __init__(self, data=None):
        if data is not None:
            for key, value in data.items():
                setattr(self, key, value)

class ModelIntakes:

    def __init__(self):
        pass

    def add_intake(self, patient_id: int, medication_id: int, date: str) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{medication_id}/intakes"
        newdatos = {"date": date, "medication_id": medication_id}
        respuesta = requests.post(url, json = newdatos)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])

    def get_intakes_by_patient_and_medication(self, patient_id: int, medication_id: int) -> list:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{medication_id}/intakes"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            lista_intakes = []
            for datos in dataRecibida:
                lista_intakes.append(Intake(datos))
            return lista_intakes
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

    def get_intake_patient(self, patient_id: int) -> list:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/intakes"
        respuesta = requests.get(url)
        dataRecibida = respuesta.json()
        if respuesta.ok:
            lista_posologias = []
            for datos in dataRecibida:
                lista_posologias.append(Intake(datos))
            return lista_posologias
        else:
            raise ExcepcionModelo(dataRecibida["detail"])

    def delete_intake(self, patient_id: int, medication_id: int, intake_id: int) -> bool:

        sleep(3)

        url = f"{SERVER_URL}/patients/{patient_id}/medications/{medication_id}/intakes/{intake_id}"
        respuesta = requests.delete(url)
        if respuesta.ok:
            return True
        else:
            raise ExcepcionModelo(respuesta.json()["detail"])
