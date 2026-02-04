```mermaid
sequenceDiagram
  participant View as View
  participant Presenter as Presenter
  participant Model as Model
  participant BBDD as BBDD
  

  View ->> Presenter: on_campo_modificado
  Presenter ->> View: actualize_list
  View ->> Presenter: list_by_query
  Presenter ->> Model: get_paciente_by_queary
  Model ->> BBDD: get_all_pacientes
  BBDD -->> Model: return list
  Model -->> Presenter: return list
  Presenter ->> View: set_pacientes
```
