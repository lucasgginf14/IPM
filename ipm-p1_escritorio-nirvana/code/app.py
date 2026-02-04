from model import ModeloPaciente, ModeloMedicamento, ModelPosologia, ModelIntakes, ServerStatus
from presenter import PacientePresenter
from view import View

import gettext
import locale
import os

if __name__ == "__main__":

    locale.setlocale(locale.LC_ALL, '')

    #os.environ['LANGUAGE'] = 'zh_CN'
    #cambiar a mano el locale

    LOCALE_DIR = "./locales"
    locale.bindtextdomain('Docs', LOCALE_DIR)
    gettext.bindtextdomain('Docs', LOCALE_DIR)
    gettext.textdomain('Docs')

    presenter = PacientePresenter(modelpac=ModeloPaciente(), modelin=ModelIntakes(), modelmed=ModeloMedicamento, modelpos=ModelPosologia, modelserver=ServerStatus(), viewpac=View())
    presenter.run(application_id="app.gestion.doctores")
