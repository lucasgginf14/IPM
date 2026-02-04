import 'source.dart';
import 'intake.dart';
import 'posology.dart';
import 'package:json_annotation/json_annotation.dart';
import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

part 'medicationIntake.g.dart';

class medicationIntakeService{
  Future<List<MedicationIntake>> getIntakes(int id)async{
    final response = await http.get(Uri.parse('$source/patients/$id/intakes')).timeout(
        const Duration(seconds: 3),
        onTimeout: () => http.Response('Error', 408));

        if(response.statusCode == 200){
          String jsonString = utf8.decode(response.bodyBytes);
          List<dynamic> data = jsonDecode(jsonString);
          List<MedicationIntake> medicationIntake = data.map((data) => MedicationIntake.fromJson(data)).toList();
          return medicationIntake;
        }else{
          throw Exception('Problema obteniendo lista de intakes');
        }
  }
}

class testMedIntakeService extends medicationIntakeService {
  @override
  Future<List<MedicationIntake>> getIntakes(int id) {
    return Future(() {
      List<Posology> posologies = [
        Posology(id: 1, hour: 8, minute: 30, medication_id: 1),
        Posology(id: 2, hour: 20, minute: 0, medication_id: 1),
      ];

      List<Intake> intakes = [
        Intake(id: 1, date: '2023-11-20', medication_id: 1),
        Intake(id: 2, date: '2023-11-21', medication_id: 1),
      ];

      List<Posology> posologies2 = [
        Posology(id: 3, hour: 10, minute: 0, medication_id: 2),
        Posology(id: 4, hour: 22, minute: 0, medication_id: 2),
      ];

      List<Intake> intakes2 = [
        Intake(id: 3, date: '2023-11-22', medication_id: 2),
        Intake(id: 4, date: '2023-11-23', medication_id: 2),
      ];

      final hoy = DateTime.now();
      final inicioParacetamol = hoy.subtract(Duration(days: 14));
      final inicioIbuprofeno = hoy.subtract(Duration(days: 5));
      String formattedDateIbu = '${inicioIbuprofeno.year}-${inicioIbuprofeno.month.toString().padLeft(2, '0')}-${inicioIbuprofeno.day.toString().padLeft(2, '0')}';
      String formattedDatePara = '${inicioParacetamol.year}-${inicioParacetamol.month.toString().padLeft(2, '0')}-${inicioParacetamol.day.toString().padLeft(2, '0')}';


      List<MedicationIntake> medicationIntakes = [
        MedicationIntake(
          id: 1,
          name: "Ibuprofen",
          dosage: 10.0,
          start_date: formattedDateIbu,
          treatment_duration: 30,
          patient_id: id,
          posologies_by_medication: posologies,
          intakes_by_medication: intakes,
        ),
        MedicationIntake(
          id: 2,
          name: "Paracetamol",
          dosage: 20.0,
          start_date: formattedDatePara,
          treatment_duration: 35,
          patient_id: id,
          posologies_by_medication: posologies2,
          intakes_by_medication: intakes2,
        ),
      ];
      return medicationIntakes;
    });
  }
}


@JsonSerializable(explicitToJson: true)
class MedicationIntake {
  final int id;
  final String name;
  final double dosage; // Cambié Float a double para ser más adecuado en Dart
  final String start_date;
  final int treatment_duration; // Cambié 'duracion_tratamiento' por 'treatment_duration'
  final int patient_id;
  final List<Posology> posologies_by_medication; // Cambié 'posologiasXmeds' a 'posologiesByMedication'
  final List<Intake> intakes_by_medication; // Cambié 'intakesXmeds' a 'intakesByMedication'

  const MedicationIntake({
    required this.id,
    required this.name,
    required this.dosage,
    required this.start_date,
    required this.treatment_duration,
    required this.patient_id,
    required this.posologies_by_medication,
    required this.intakes_by_medication,
  });

  factory MedicationIntake.fromJson(Map<String, dynamic> data) => _$MedicationIntakeFromJson(data);

  Map<String, dynamic> toJson() => _$MedicationIntakeToJson(this);

}

class MedIntakeModel with ChangeNotifier{
  bool _loading = false;
  List<MedicationIntake>? _medicationIntake;
  String _info = 'Obtener MedicationIntake';

  List<MedicationIntake>? get medicationintake => _medicationIntake;
  String get info => _info;
  bool get loading => _loading;

  late medicationIntakeService service;

  MedIntakeModel({service}){
    this.service = service ?? medicationIntakeService();
  }

  Future<List<MedicationIntake>> getMedIntakesById(int id) async{
    _loading =true;
    //notifyListeners();

    try{
      _medicationIntake = await service.getIntakes(id);
      return _medicationIntake!;
    } catch (e) {
      _medicationIntake = null;
      _info = 'Error al cargar MedicationIntake';
      throw Exception(e);
      // Avisamos a los oyentes al acabar la operación
    } finally {
      _loading = false;
      //notifyListeners();
    }

  }
}