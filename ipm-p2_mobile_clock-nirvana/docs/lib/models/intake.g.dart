// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'intake.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Intake _$IntakeFromJson(Map<String, dynamic> json) => Intake(
      id: (json['id'] as num).toInt(),
      date: json['date'] as String,
      medication_id: (json['medication_id'] as num).toInt(),
    );

Map<String, dynamic> _$IntakeToJson(Intake instance) => <String, dynamic>{
      'id': instance.id,
      'date': instance.date,
      'medication_id': instance.medication_id,
    };
