// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'medicationIntake.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MedicationIntake _$MedicationIntakeFromJson(Map<String, dynamic> json) =>
    MedicationIntake(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String,
      dosage: (json['dosage'] as num).toDouble(),
      start_date: json['start_date'] as String,
      treatment_duration: (json['treatment_duration'] as num).toInt(),
      patient_id: (json['patient_id'] as num).toInt(),
      posologies_by_medication:
          (json['posologies_by_medication'] as List<dynamic>)
              .map((e) => Posology.fromJson(e as Map<String, dynamic>))
              .toList(),
      intakes_by_medication: (json['intakes_by_medication'] as List<dynamic>)
          .map((e) => Intake.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$MedicationIntakeToJson(MedicationIntake instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'dosage': instance.dosage,
      'start_date': instance.start_date,
      'treatment_duration': instance.treatment_duration,
      'patient_id': instance.patient_id,
      'posologies_by_medication':
          instance.posologies_by_medication.map((e) => e.toJson()).toList(),
      'intakes_by_medication':
          instance.intakes_by_medication.map((e) => e.toJson()).toList(),
    };
