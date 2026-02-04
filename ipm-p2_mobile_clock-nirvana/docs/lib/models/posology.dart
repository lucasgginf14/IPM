import 'package:json_annotation/json_annotation.dart';

part 'posology.g.dart';

@JsonSerializable()
class Posology{
  final int id;
  final int hour;
  final int minute;
  final int medication_id;

  const Posology({
    required this.id,
    required this.hour,
    required this.minute,
    required this.medication_id,
  });

  factory Posology.fromJson(Map<String, dynamic> data) => _$PosologyFromJson(data);

  Map<String, dynamic> toJson() => _$PosologyToJson(this);
}
