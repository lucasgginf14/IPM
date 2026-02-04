import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';

import 'source.dart';
import 'package:json_annotation/json_annotation.dart';
import 'dart:async';

import 'package:http/http.dart' as http;

part 'intake.g.dart';


@JsonSerializable()
class Intake{
  final int id;
  final String date;
  final int medication_id;

  const Intake({
    required this.id,
    required this.date,
    required this.medication_id,
  });

  factory Intake.fromJson(Map<String, dynamic> data) => _$IntakeFromJson(data);

  Map<String, dynamic> toJson() => _$IntakeToJson(this);
}

class IntakeService {
  Future<void> uploadIntake(int id, int medicationId, String fecha) async {

    final url = Uri.parse('$source/patients/$id/medications/$medicationId/intakes');
    final newDatos = {
      "date": fecha,
      "medication_id": medicationId
    };

    try {
      final response = await http.post(
        url,
        headers: {
          HttpHeaders.contentTypeHeader: 'application/json',
        },
        body: jsonEncode(newDatos),
      ).timeout(
        Duration(seconds: 3),
        onTimeout: () => http.Response('Error', 408), 
      );

      if (response.statusCode != 201) {
        final errorDetail = jsonDecode(response.body)["detail"] ?? "Error desconocido";
        final eror = 'Error Modelo $errorDetail';
        throw Exception(eror);
      }
    } catch (e) {
      rethrow;
    }
  }
}

class testIntakeService extends IntakeService{
  @override
  Future<void> uploadIntake(int id, int medicationId, String fecha){
    return Future(() => {});
  }
}

class IntakeModel with ChangeNotifier {

  bool _loading = false;
  String _info = 'Haga click para subir la toma';

  String get info => _info;
  bool get loading => _loading;

  late IntakeService service;

  IntakeModel({service}){
    this.service = service ?? IntakeService();
  }

  Future<void> uploadIntake(int id, int medicationId, String fecha) async {

    _loading = true;
    notifyListeners();

    try {
      await service.uploadIntake(id, medicationId, fecha);
    } catch (e) {
      _info = 'Error al subir la toma';
      throw Exception(e);
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}
