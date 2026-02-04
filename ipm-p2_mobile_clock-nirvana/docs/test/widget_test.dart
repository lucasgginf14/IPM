import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:docs/main.dart';
import 'package:docs/models/intake.dart';
import 'package:docs/models/patient_model.dart';
import 'package:docs/models/medicationIntake.dart';
import 'package:provider/provider.dart';

void main() {
  testWidgets('Test PatientViewer displays patient data correctly',
      (WidgetTester tester) async {

    final patientModel = PatientModel(service: TestPatientService());
    final medIntakeModel = MedIntakeModel(service : testMedIntakeService());
    final intakeService = IntakeService();
    final intakeModel = IntakeModel(service : testIntakeService());

    await tester.pumpWidget(
      MultiProvider(
        providers: [
        Provider(create: (_) => intakeService),
        ChangeNotifierProvider(create: (_) => patientModel),
        ChangeNotifierProvider(create: (_) => medIntakeModel),
        ChangeNotifierProvider(create: (_) => intakeModel),
      ],
        child: MaterialApp(
          home: const LogScreen(),
        ),
      ),
    );

    final textEntry = find.byType(TextField);

    expect(find.textContaining('Log-In'), findsOneWidget);
    expect(textEntry, findsOneWidget);

    await tester.enterText(textEntry, ' ');
    await tester.pump();

    final elevatedButt = find.byType(ElevatedButton);
    expect(elevatedButt, findsOneWidget);

    await tester.tap(elevatedButt);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final closeAlert = find.textContaining('Cerrar');
    await tester.tap(closeAlert);

    final textEntrada = find.byType(TextField);

    await tester.enterText(textEntrada, '123456789');
    await tester.pump();

    final buttAcceder = find.textContaining('Acceder');

    await tester.tap(buttAcceder);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final backButt = find.byType(BackButton);

    expect(find.textContaining('Welcome, Tester Testadez'), findsOneWidget);
    final historicButt = find.text('Historial');
    final medsButt = find.text('Medicaciones Hoy');
    
    await tester.tap(historicButt);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final hoy = DateTime.now();
    final inicioParacetamol = hoy.subtract(Duration(days: 14));
    final inicioIbuprofeno = hoy.subtract(Duration(days: 5));
    String formattedDateIbu = '${inicioIbuprofeno.year}-${inicioIbuprofeno.month.toString().padLeft(2, '0')}-${inicioIbuprofeno.day.toString().padLeft(2, '0')}';
    String formattedDatePara = '${inicioParacetamol.year}-${inicioParacetamol.month.toString().padLeft(2, '0')}-${inicioParacetamol.day.toString().padLeft(2, '0')}';

    expect(find.textContaining('Historial de Medicación'), findsOneWidget);
    final cards = tester.widgetList<Card>(find.byType(Card));
    expect(cards.length, 2);
    expect(find.text('Ibuprofen'), findsOneWidget);
    expect(find.text('Paracetamol'), findsOneWidget);
    expect(find.text('Dosis: 10.0'), findsOneWidget);
    expect(find.text('Dosis: 20.0'), findsOneWidget);
    expect(find.text('Fecha de inicio: $formattedDatePara'), findsOneWidget);
    expect(find.text('Fecha de inicio: $formattedDateIbu'), findsOneWidget);
    expect(find.text('Duración del tratamiento: 30 días'), findsOneWidget);
    expect(find.text('Duración del tratamiento: 35 días'), findsOneWidget);
    expect(find.textContaining('8:30'), findsOneWidget);
    expect(find.textContaining('20:00'), findsOneWidget);
    expect(find.textContaining('10:00'), findsOneWidget);
    expect(find.textContaining('22:00'), findsOneWidget);
    expect(find.textContaining('2023-11-20'), findsOneWidget);
    expect(find.textContaining('2023-11-21'), findsOneWidget);
    expect(find.textContaining('2023-11-22'), findsOneWidget);
    expect(find.textContaining('2023-11-23'), findsOneWidget);

    await tester.tap(backButt);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    expect(find.textContaining('Welcome, Tester Testadez'), findsOneWidget);

    await tester.tap(medsButt);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final cardsIntakes = tester.widgetList<Card>(find.byType(Card));

    expect(cardsIntakes.length, 2);
    expect(find.text('Ibuprofen'), findsExactly(2));
    expect(find.textContaining('Paracetamol'), findsExactly(0));
    expect(find.textContaining('Dosis: 10.0'), findsExactly(2));
    expect(find.textContaining('Fecha de inicio: $formattedDateIbu'), findsExactly(2));
    expect(find.textContaining('Duración del tratamiento: 30 días'), findsExactly(2));
    expect(find.textContaining('8:30'), findsOneWidget);
    expect(find.textContaining('20:00'), findsOneWidget);

    final cajas = find.byType(Checkbox);

    await tester.tap(cajas.at(0));
    await tester.pumpAndSettle(const Duration(seconds: 5));

    expect(find.textContaining('Confirmación'), findsOneWidget);
    final cancelar = find.text('Cancelar');

    await tester.tap(cancelar);
    await tester.pumpAndSettle(const Duration(seconds: 5));
    expect(find.textContaining('Confirmación'), findsNothing);

    await tester.tap(cajas.at(0));
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final aceptar = find.text('Aceptar');
    await tester.tap(aceptar);
    await tester.pumpAndSettle();

    /*
    final closeExitoButt = find.textContaining("Éxito");
    await tester.tap(closeExitoButt);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final firstCheckbox = tester.widget<Checkbox>(cajas.at(1));

    expect(firstCheckbox.value, isTrue); 
    */

    final closeErrButt = find.textContaining("Error");
    await tester.tap(closeErrButt);
    await tester.pumpAndSettle(const Duration(seconds: 5));

    final firstCheckbox = tester.widget<Checkbox>(cajas.at(1));

    expect(firstCheckbox.value, isFalse); 

      });
    }
