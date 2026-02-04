import 'package:docs/models/intake.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';

import 'models/medicationIntake.dart';
import 'models/patient_model.dart';

const ID_PACIENTE = 4;

void main() {
   runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => MedIntakeModel()),
        ChangeNotifierProvider(create: (_) => IntakeModel()),
        Provider(create: (_) => IntakeService()),
      ],
      child: MyApp(),
    ),
  );
}

class _FormatoCodigo extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    String digitsOnly = newValue.text.replaceAll(RegExp(r'[^0-9]'), '');

    String formatted = '';
    for (int i = 0; i < digitsOnly.length; i++) {
      if (i == 3 || i == 5) {
        formatted += '-';
      }
      formatted += digitsOnly[i];
    }

    if (formatted.length > 11) {
      formatted = formatted.substring(0, 11);
    }

    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}


class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => PatientModel()),
        ChangeNotifierProvider(create: (_) => IntakeModel()),
      ],
      child: MaterialApp(
        title: 'Flutter Wear & Mobile Example',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: const MyHomePage(),
      ),
    );
  }
}

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key});
  @override
  Widget build(BuildContext context) {
    // Obtenemos el ancho de la pantalla para determinar si es móvil o smartwatch
    double screenWidth = MediaQuery.of(context).size.width;

    // Si el ancho de la pantalla es menor a 300px, es un smartwatch
    if (screenWidth < 300) {
      return const AuxClock();
    } else {
      return const LogScreen();
    }
  }
}

class AuxClock extends StatelessWidget {
  const AuxClock({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder<List<MedicationIntake>>(
        future: _fetchMedications(context), // Llamada asíncrona
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: CircularProgressIndicator()); // Cargando
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}')); // Error al obtener datos
          } else if (snapshot.hasData) {
            final List<MedicationIntake> lista = snapshot.data!;
            return Clock(lista: lista); // Llamamos a Clock y pasamos la lista
          } else {
            return Center(child: Text('No se encontraron medicamentos.')); // No hay datos
          }
        },
      ),
    );
  }

  Future<List<MedicationIntake>> _fetchMedications(BuildContext context) async {
    return await context.read<MedIntakeModel>().getMedIntakesById(ID_PACIENTE); // Llamada al método asíncrono
  }
}

class Clock extends StatelessWidget {
  final List<MedicationIntake> lista;

  const Clock({super.key, required this.lista});

  @override
  Widget build(BuildContext context) {
    final today = DateTime.now();

    final todayMedications = lista.where((medication) {
      final startDate = DateTime.parse(medication.start_date);
      final endDate = startDate.add(Duration(days: medication.treatment_duration));
      return today.isBefore(endDate) || today.isAtSameMomentAs(endDate);
    }).toList();

    return Center(
      child: SizedBox(
        width: 175, // Tamaño del círculo
        height: 175, // Para hacerlo circular
        child: ListView(
          children: todayMedications.map((medication) {
            final todayPosologies = medication.posologies_by_medication.where((posology) {
              final posologyTime = DateTime(today.year, today.month, today.day, posology.hour, posology.minute);
              return posologyTime.isAfter(DateTime(today.year, today.month, today.day, 0, 0)) &&
                     posologyTime.isBefore(DateTime(today.year, today.month, today.day, 23, 59));
            }).toList();

            return Column(
              children: todayPosologies.map((posology) {
                return ListTile(
                  title: Text(medication.name),
                  subtitle: Text(
                    DateFormat.jm().format(DateTime(today.year, today.month, today.day, posology.hour, posology.minute)),
                  ),
                );
              }).toList(),
            );
          }).toList(),
        ),
      ),
    );
  }
}

class LogScreen extends StatefulWidget {
  const LogScreen({super.key});

  @override
  _LogScreenState createState() => _LogScreenState();
}

class _LogScreenState extends State<LogScreen> {
  bool _isLoading = false; 
  TextEditingController textController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Log-In'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min, 
            children: [
              TextField(
                controller: textController,
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  _FormatoCodigo(),
                ],
                decoration: InputDecoration(
                  labelText: 'Código Paciente',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 20),
              if (_isLoading)
                CircularProgressIndicator(),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () async {
                  setState(() {
                    _isLoading = true;  
                  });

                  try {
                    Patient paciente = await context.read<PatientModel>().getPatientByCode(textController.text);

                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => UserScreen(paciente: paciente),
                      ),
                    );
                  } catch (e) {
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: Text('Alerta'),
                        content: Text(e.toString()),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: Text('Cerrar'),
                          ),
                        ],
                      ),
                    );
                  } finally {
                    setState(() {
                      _isLoading = false;
                    });
                  }
                },
                child: Text('Acceder'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class UserScreen extends StatefulWidget {
  final Patient paciente;

  const UserScreen({super.key, required this.paciente});

  @override
  _UserScreenState createState() => _UserScreenState();
}

class _UserScreenState extends State<UserScreen> {
  bool _isLoadingHistorial = false;  
  bool _isLoadingMedicaciones = false;  

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Text(
                'Welcome, ${widget.paciente.name} ${widget.paciente.surname}',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton(
                    onPressed: _isLoadingHistorial
                        ? null 
                        : () async {
                            setState(() {
                              _isLoadingHistorial = true; 
                            });

                            try {
                              List<MedicationIntake> medicationIntake = await context
                                  .read<MedIntakeModel>()
                                  .getMedIntakesById(widget.paciente.id);

                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => Historial(
                                    lista: medicationIntake,
                                  ),
                                ),
                              );
                            } catch (e) {
                              showDialog(
                                context: context,
                                builder: (context) => AlertDialog(
                                  title: Text('Alerta'),
                                  content: Text(e.toString()),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(context),
                                      child: Text('Cerrar'),
                                    ),
                                  ],
                                ),
                              );
                            } finally {
                              setState(() {
                                _isLoadingHistorial = false; 
                              });
                            }
                          },
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(120, 120), 
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8), 
                      ),
                    ),
                    child: _isLoadingHistorial
                        ? CircularProgressIndicator()
                        : Text('Historial'),
                  ),
                  
                  ElevatedButton(
                    onPressed: _isLoadingMedicaciones
                        ? null
                        : () async {
                            setState(() {
                              _isLoadingMedicaciones = true; 
                            });

                            try {
                              List<MedicationIntake> medicationIntake = await context
                                  .read<MedIntakeModel>()
                                  .getMedIntakesById(widget.paciente.id);

                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => IntakesByGranularity(
                                    lista: medicationIntake,
                                    patientId: widget.paciente.id,
                                  ),
                                ),
                              );
                            } catch (e) {
                              showDialog(
                                context: context,
                                builder: (context) => AlertDialog(
                                  title: Text('Alerta'),
                                  content: Text(e.toString()),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(context),
                                      child: Text('Cerrar'),
                                    ),
                                  ],
                                ),
                              );
                            } finally {
                              setState(() {
                                _isLoadingMedicaciones = false;
                              });
                            }
                          },
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(120, 120), 
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8), 
                      ),
                    ),
                    child: _isLoadingMedicaciones
                        ? CircularProgressIndicator()
                        : Text('Medicaciones Hoy'), 
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class Historial extends StatelessWidget{
  final List<MedicationIntake> lista;

  const Historial({super.key, required this.lista});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Historial de Medicación'),
      ),
      body: ListView.builder(
        itemCount: lista.length,
        itemBuilder: (context, index) {
          final medication = lista[index];

          return Card(
            margin: const EdgeInsets.all(8.0),
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    medication.name,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text("Dosis: ${medication.dosage}"),
                  Text("Fecha de inicio: ${medication.start_date}"),
                  Text("Duración del tratamiento: ${medication.treatment_duration} días"),
                  const SizedBox(height: 8),
                  Text(
                    "Posología:",
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  ...medication.posologies_by_medication.map((posology) {
                    final pos = posology;
                    return Text("- ${pos.hour}:${pos.minute.toString().padLeft(2, '0')}");
                  }),
                  const SizedBox(height: 8),
                  Text(
                    "Intakes:",
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  ...medication.intakes_by_medication.map((intake) {
                    final intk = intake;
                    return Text("- ${intk.date}");
                  }),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class IntakesByGranularity extends StatefulWidget {
  final List<MedicationIntake> lista;
  final int patientId;

  const IntakesByGranularity({
    super.key,
    required this.lista,
    required this.patientId,
  });

  @override
  _IntakesByGranularityState createState() => _IntakesByGranularityState();
}

class _IntakesByGranularityState extends State<IntakesByGranularity> {
  late String _currentTime;
  late Timer _timer;

  late List<List<bool>> _checkboxStates;
  
  late List<List<String?>> _frozenTimes;

  late List<List<String?>> _checkboxDates;

  @override
  void initState() {
    super.initState();

    _checkboxStates = List.generate(widget.lista.length, (medicationIndex) {
      return List.filled(
        widget.lista[medicationIndex].posologies_by_medication.length, false
      );
    });

    _frozenTimes = List.generate(widget.lista.length, (medicationIndex) {
      return List.filled(
        widget.lista[medicationIndex].posologies_by_medication.length, null
      );
    });

    _checkboxDates = List.generate(widget.lista.length, (medicationIndex) {
      return List.filled(
        widget.lista[medicationIndex].posologies_by_medication.length, null
      );
    });

    _updateTime();
    _startTimer();
    _loadCheckboxStates(); 
    _loadFrozenTimes();    
    _loadCheckboxDates();   
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  void _updateTime() {
    setState(() {
      _currentTime = DateFormat('HH:mm:ss').format(DateTime.now());
    });
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (Timer timer) {
      _updateTime();
    });
  }

  void _onCheckboxChanged(int medicationIndex, int posologyIndex, bool? value, int idPaciente, int idMedicacion) {
    if (value != null && value) {
      _showConfirmationDialog(medicationIndex, posologyIndex, idPaciente, idMedicacion);
    }
  }

void _showConfirmationDialog(int medicationIndex, int posologyIndex, int idPaciente, int idMedicacion) {
  final BuildContext parentContext = context; 

  showDialog(
    context: parentContext,
    builder: (BuildContext dialogContext) {
      return AlertDialog(
        title: const Text("Confirmación"),
        content: const Text("¿Estás seguro de marcar esta toma de medicación?"),
        actions: <Widget>[
          TextButton(
            onPressed: () {
              Navigator.of(dialogContext).pop(); 
            },
            child: const Text("Cancelar"),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(dialogContext).pop();

              showDialog(
                context: parentContext,
                barrierDismissible: false,
                builder: (BuildContext loadingContext) {
                  return const Center(
                    child: CircularProgressIndicator(),
                  );
                },
              );

              try {
                final intakeService = Provider.of<IntakeService>(parentContext, listen: false);
                await intakeService.uploadIntake(
                  idPaciente,
                  idMedicacion,
                  DateFormat("yyyy-MM-dd'T'HH:mm").format(DateTime.now()),
                );

                setState(() {
                  _checkboxStates[medicationIndex][posologyIndex] = true;
                  _frozenTimes[medicationIndex][posologyIndex] = _currentTime;
                  _checkboxDates[medicationIndex][posologyIndex] =
                      DateFormat('yyyy-MM-dd').format(DateTime.now());
                });

                await _saveCheckboxStates();
                await _saveFrozenTimes();
                await _saveCheckboxDates();

                Navigator.of(parentContext).pop();

                showDialog(
                  context: parentContext,
                  builder: (context) => AlertDialog(
                    title: const Text("Éxito"),
                    content: const Text("Toma añadida con éxito!"),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text("Cerrar"),
                      ),
                    ],
                  ),
                );
              } catch (e) {

                Navigator.of(parentContext).pop();

                showDialog(
                  context: parentContext,
                  builder: (context) => AlertDialog(
                    title: const Text('Error'),
                    content: Text(e.toString()),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('Cerrar'),
                      ),
                    ],
                  ),
                );
              }
            },
            child: const Text("Aceptar"),
          ),
        ],
      );
    },
  );
}

  Future<void> _saveCheckboxStates() async {
    final prefs = await SharedPreferences.getInstance();

    for (int medicationIndex = 0; medicationIndex < widget.lista.length; medicationIndex++) {
      for (int posologyIndex = 0; posologyIndex < widget.lista[medicationIndex].posologies_by_medication.length; posologyIndex++) {
        prefs.setBool('checkbox_${widget.patientId}_$medicationIndex$posologyIndex', _checkboxStates[medicationIndex][posologyIndex]);
      }
    }
  }

  Future<void> _saveFrozenTimes() async {
    final prefs = await SharedPreferences.getInstance();

    for (int medicationIndex = 0; medicationIndex < widget.lista.length; medicationIndex++) {
      for (int posologyIndex = 0; posologyIndex < widget.lista[medicationIndex].posologies_by_medication.length; posologyIndex++) {
        prefs.setString('frozen_time_${widget.patientId}_$medicationIndex$posologyIndex', _frozenTimes[medicationIndex][posologyIndex] ?? '');
      }
    }
  }

  Future<void> _saveCheckboxDates() async {
    final prefs = await SharedPreferences.getInstance();

    for (int medicationIndex = 0; medicationIndex < widget.lista.length; medicationIndex++) {
      for (int posologyIndex = 0; posologyIndex < widget.lista[medicationIndex].posologies_by_medication.length; posologyIndex++) {
        prefs.setString('checkbox_date_${widget.patientId}_$medicationIndex$posologyIndex', _checkboxDates[medicationIndex][posologyIndex] ?? '');
      }
    }
  }

  Future<void> _loadCheckboxStates() async {
    final prefs = await SharedPreferences.getInstance();

    _checkboxStates = List.generate(widget.lista.length, (medicationIndex) {
      return List.generate(
        widget.lista[medicationIndex].posologies_by_medication.length,
        (posologyIndex) {
          return prefs.getBool('checkbox_${widget.patientId}_$medicationIndex$posologyIndex') ?? false;
        },
      );
    });
  }

  Future<void> _loadFrozenTimes() async {
    final prefs = await SharedPreferences.getInstance();

    _frozenTimes = List.generate(widget.lista.length, (medicationIndex) {
      return List.generate(
        widget.lista[medicationIndex].posologies_by_medication.length,
        (posologyIndex) {
          return prefs.getString('frozen_time_${widget.patientId}_$medicationIndex$posologyIndex');
        },
      );
    });
  }

  Future<void> _loadCheckboxDates() async {
    final prefs = await SharedPreferences.getInstance();

    _checkboxDates = List.generate(widget.lista.length, (medicationIndex) {
      return List.generate(
        widget.lista[medicationIndex].posologies_by_medication.length,
        (posologyIndex) {
          return prefs.getString('checkbox_date_${widget.patientId}_$medicationIndex$posologyIndex');
        },
      );
    });
  }

  bool _isMedicationValid(MedicationIntake medication) {
    DateTime startDate = DateFormat('yyyy-MM-dd').parse(medication.start_date);
    DateTime endDate = startDate.add(Duration(days: medication.treatment_duration));

    DateTime currentDate = DateTime.now();

    return currentDate.isBefore(endDate);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tomas de Medicación'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Fecha Actual: ${DateFormat('dd/MM/yyyy').format(DateTime.now())}",
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: widget.lista.length,
                itemBuilder: (context, medicationIndex) {
                  final medication = widget.lista[medicationIndex];

                  if (!_isMedicationValid(medication)) {
                    return const SizedBox.shrink();
                  }

                  return Column(
                    children: medication.posologies_by_medication.asMap().entries.map((entry) {
                      int posologyIndex = entry.key;
                      var posology = entry.value;

                      bool isSameDay = _checkboxDates[medicationIndex][posologyIndex] == DateFormat('yyyy-MM-dd').format(DateTime.now());
                      if (!isSameDay) {
                        _checkboxStates[medicationIndex][posologyIndex] = false;
                        _frozenTimes[medicationIndex][posologyIndex] = null;
                      }

                      return Card(
                        margin: const EdgeInsets.symmetric(vertical: 8.0),
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                medication.name,
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text("Dosis: ${medication.dosage}"),
                              const SizedBox(height: 8),
                              Text("Fecha de inicio: ${medication.start_date}"),
                              Text("Duración del tratamiento: ${medication.treatment_duration} días"),
                              const SizedBox(height: 8),
                              Text(
                                "Hora de toma: ${posology.hour}:${posology.minute.toString().padLeft(2, '0')}",
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              
                              Text(
                                "Hora actual: ${_checkboxStates[medicationIndex][posologyIndex] ? _frozenTimes[medicationIndex][posologyIndex] : _currentTime}",
                                style: const TextStyle(color: Colors.blue),
                              ),
                              const SizedBox(height: 8),
                              
                              CheckboxListTile(
                                title: const Text("Añadir toma con hora actual"),
                                value: _checkboxStates[medicationIndex][posologyIndex],
                                onChanged: (bool? value) {
                                  _onCheckboxChanged(medicationIndex, posologyIndex, value, medication.patient_id, posology.medication_id);
                                },
                              ),
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
