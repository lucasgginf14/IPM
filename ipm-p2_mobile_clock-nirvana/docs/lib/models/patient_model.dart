import 'source.dart';
import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// Esta es la dirección de nuestro ordenador para los emuladores

// Servicio que se conecta con la BD
class PatientService {
  Future<Patient> getByCode(String code) async {
    // Hacemos la petición al servidor; si en 3s no obtenemos respuesta lanzamos el error
    final response = await http.get(Uri.parse('$source/patients')).timeout(
        const Duration(seconds: 3),
        onTimeout: () => http.Response('Error', 408));

    // Si la respuesta es un 200 OK, creamos el paciente y lo devolvemos
    if (response.statusCode == 200) {
      return Patient.fromJson(jsonDecode(response.body) as List<dynamic>, code);
      // En otro caso, lanzamos una excepción
    } else {
      throw Exception('Error obteniendo el usuario espicificado');
    }
  }
}

class TestPatientService extends PatientService{

  @override
  Future<Patient> getByCode(String code){
    if (code == '123-45-6789') {
      return Future(() => Patient(id: -1, name: 'Tester', surname: 'Testadez', code: '123456789'));
    }else{
      throw Exception('Error obteniendo el usuario espicificado');
    }
  }

}

// Modelo para el paciente, parte del patrón Provider
class PatientModel with ChangeNotifier {
  // Atributos para la actuar en función de lo que se esté haciendo
  bool _loading = false;
  Patient? _patient;
  String _info = 'Haga click para obtener un paciente';

  Patient? get patient => _patient;
  String get info => _info;
  bool get loading => _loading;

    // Gestión del servicio del modelo
  late PatientService service;

  PatientModel({service}) {
    this.service = service ?? PatientService();
  }

  // Método del modelo que se llama desde los botones de la vista
  Future<Patient> getPatientByCode(String code) async {
    // Establecemos que está cargando y se avisa a los oyentes
    _loading = true;
    notifyListeners();
    // Hacemos la llamda al servicio
    try {
      _patient = await service.getByCode(code);
      return Patient(id:_patient!.id, name: _patient!.name, surname: _patient!.surname, code: _patient!.code);
      // Gestionamos los posibles errores
    } catch (e) {
      _patient = null;
      _info = 'Error al cargar paciente';
      throw Exception(e);
      // Avisamos a los oyentes al acabar la operación
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}

// Clase para representar objetos de tipo paciente
class Patient {
  // Atributos
  final int id;
  final String name;
  final String surname;
  final String code;

  // Constructor
  const Patient({
    required this.id,
    required this.name,
    required this.surname,
    required this.code,
  });

  // Método para generar un objeto Patient a partir de la lista de pacientes
  factory Patient.fromJson(List<dynamic> jsonList, String code) {

    for(var json in jsonList){
      if (json['code'] == code){
        return Patient(id: json['id'], name: json['name'], surname: json['surname'], code: json['code']);
      }
    }
    throw const FormatException('No existe el paciente con ese Codigo');
  }
}
