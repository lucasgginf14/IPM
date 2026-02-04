// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'posology.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Posology _$PosologyFromJson(Map<String, dynamic> json) => Posology(
      id: (json['id'] as num).toInt(),
      hour: (json['hour'] as num).toInt(),
      minute: (json['minute'] as num).toInt(),
      medication_id: (json['medication_id'] as num).toInt(),
    );

Map<String, dynamic> _$PosologyToJson(Posology instance) => <String, dynamic>{
      'id': instance.id,
      'hour': instance.hour,
      'minute': instance.minute,
      'medication_id': instance.medication_id,
    };
