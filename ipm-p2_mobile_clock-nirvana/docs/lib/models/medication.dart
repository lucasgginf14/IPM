
import 'dart:ffi';

class Medication{
  final int id;
  final String name;
  final Float dosage;
  final String start_date;
  final int duracion_tratamiento;
  final int patient_id;

  const Medication({
    required this.id,
    required this.name,
    required this.dosage,
    required this.start_date,
    required this.duracion_tratamiento,
    required this.patient_id,
  });
}