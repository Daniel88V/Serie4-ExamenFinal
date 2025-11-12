from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(237, 265)
        Dialog.setStyleSheet(u"")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(-20, 0, 261, 51))
        self.label.setStyleSheet(u"background-color: rgb(118, 106, 255);\n"
"font: 900 12pt \"Arial\";")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(-10, 50, 251, 8))
        self.label_2.setStyleSheet(u"background-color: qconicalgradient(cx:0.517, cy:0.489, angle:92.2, stop:0 rgba(181, 181, 181, 255), stop:0.0883978 rgba(158, 158, 158, 255), stop:0.21547 rgba(131, 131, 131, 255), stop:0.270718 rgba(156, 156, 156, 255), stop:0.441989 rgba(158, 158, 158, 255), stop:0.469613 rgba(99, 99, 99, 255), stop:0.585635 rgba(128, 128, 128, 255), stop:0.734807 rgba(142, 142, 142, 255), stop:0.828729 rgba(140, 140, 140, 255), stop:0.922652 rgba(156, 156, 156, 255), stop:1 rgba(184, 184, 184, 255));")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(-10, 60, 261, 211))
        self.label_3.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(99, 34, 165, 255), stop:0.633333 rgba(155, 151, 255, 255), stop:1 rgba(255, 255, 255, 255));")
        self.lbUsuario = QLineEdit(Dialog)
        self.lbUsuario.setObjectName(u"lbUsuario")
        self.lbUsuario.setGeometry(QRect(50, 80, 161, 22))
        self.lbContra = QLineEdit(Dialog)
        self.lbContra.setObjectName(u"lbContra")
        self.lbContra.setGeometry(QRect(50, 110, 161, 22))
        self.BtIngreso = QPushButton(Dialog)
        self.BtIngreso.setObjectName(u"BtIngreso")
        self.BtIngreso.setGeometry(QRect(80, 170, 81, 31))
        self.BtIngreso.setStyleSheet(u"font: 900 9pt \"Arial\";")
        self.lbAlerta = QLabel(Dialog)
        self.lbAlerta.setObjectName(u"lbAlerta")
        self.lbAlerta.setGeometry(QRect(50, 220, 141, 21))
        self.lbAlerta.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Inicio de Sesi\u00f3n", None))
        self.label_2.setText("")
        self.label_3.setText("")
        self.lbUsuario.setPlaceholderText(QCoreApplication.translate("Dialog", u"Ingresa tu usario", None))
        self.lbContra.setPlaceholderText(QCoreApplication.translate("Dialog", u"Ingresa tu contrase\u00f1a", None))
        self.BtIngreso.setText(QCoreApplication.translate("Dialog", u"Ingresar", None))
        self.lbAlerta.setText("")
    # retranslateUi

