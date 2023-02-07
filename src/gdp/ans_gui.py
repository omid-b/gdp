import os
import sys 
import re

from . import ans_config

from obspy import UTCDateTime

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from numpy import arange
from PyQt5.QtCore import (
    Qt,
    QRect,
    QPoint,
    QEasingCurve,
    QPropertyAnimation,
    pyqtProperty,
    QCoreApplication,
    QSize,
    QBuffer,
    QByteArray,
)
from PyQt5.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPalette,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QDialog,
    QFrame,
    QPushButton,
    QLabel,
    QLineEdit,
    QScrollArea,
    QStackedWidget,
    QCheckBox,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QDoubleSpinBox,
    QDateTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
)


pkg_dir, _ = os.path.split(__file__)
images_dir = os.path.join(pkg_dir,"data","images")


class QLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


class QComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


class QSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


class QDoubleSpinBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


class MyLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)

    def isfile(self): # is an existing file
        f = self.text()
        if os.path.isfile(f) or f == '':
            self.setStyleSheet("color: black")
            if os.path.isfile(f):
                return True
        else:
            self.setStyleSheet("color: red")
            return False

    def isdir(self): # is an existing directory
        d = self.text()
        if os.path.isdir(d) or d == '':
            self.setStyleSheet("color: black")
            if os.path.isdir(d):
                return True
        else:
            self.setStyleSheet("color: red")
            return False

    def isdate(self): # is a date value: 'YYYY-MM-DD'
        text = self.text()
        rexpr = re.compile("^[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]$")
        if rexpr.match(text) or text == '':
            self.setStyleSheet("color: black")
            if rexpr.match(text):
                return True
        else:
            self.setStyleSheet("color: red")
            return False

    def islat(self): # is a latitude value
        text = self.text()
        try:
            val = float(text)
            if val >= -90 and val <= 90:
                self.setStyleSheet("color: black")
                return True
            else:
                self.setStyleSheet("color: red")
                return False
        except ValueError:
            if len(text):
                self.setStyleSheet("color: red")
            else:
                self.setStyleSheet("color: black")
            return False

    def islon(self): # is a longitude value
        text = self.text()
        try:
            val = float(text)
            if val >= -180 and val <= 180:
                self.setStyleSheet("color: black")
                return True
            else:
                self.setStyleSheet("color: red")
                return False
        except ValueError:
            if len(text):
                self.setStyleSheet("color: red")
            else:
                self.setStyleSheet("color: black")
            return False

    def isposint(self): # is positive integer
        text = self.text()
        try:
            val = int(text)
            if val > 0:
                self.setStyleSheet("color: black")
                return True
            else:
                self.setStyleSheet("color: red")
                return False
        except ValueError:
            if len(text):
                self.setStyleSheet("color: red")
            else:
                self.setStyleSheet("color: black")
            return False

    def isfloat(self): # is a float
        text = self.text()
        try:
            val = float(text)
            self.setStyleSheet("color: black")
            return True
        except ValueError:
            if len(text):
                self.setStyleSheet("color: red")
            else:
                self.setStyleSheet("color: black")
            return False


class MyCheckBox(QCheckBox):
    def __init__(self):
        super().__init__()
        self.setFixedSize(30,18)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.bg_color = '#aaa'
        self.circle_color = '#fff'
        self.active_color = '#299408'
        # for animation
        self._circle_position = 2
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setDuration(100)
        self.stateChanged.connect(self.startTransition)

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = pyqtProperty(float, get_circle_position, set_circle_position)
    
    def startTransition(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - self.height() + 2)
        else:
            self.animation.setEndValue(2)
        self.animation.start()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # draw background rectangle
        rect = QRect(0, 0, self.width(), self.height())
        
        # draw circle
        if  self.isChecked():
            painter.setBrush(QColor(self.active_color))
            painter.drawRoundedRect(0, 0, rect.width(), rect.height(),
                                    rect.height() / 2, rect.height() / 2)
            painter.setBrush(QColor(self.circle_color))
            try:
                painter.drawEllipse(self._circle_position, 2,
                                    self.height() - 4, self.height() - 4)
            except:
                painter.drawEllipse(self.width() - self.height() + 2, 2,
                                    self.height() - 4, self.height() - 4)
        else:
            painter.setBrush(QColor(self.bg_color))
            painter.drawRoundedRect(0, 0, rect.width(), rect.height(),
                                    rect.height() / 2, rect.height() / 2)
            painter.setBrush(QColor(self.circle_color))
            try:
                painter.drawEllipse(self._circle_position, 2,
                                    self.height() - 4, self.height() - 4)
            except:
                painter.drawEllipse(self.width() - self.height() - 10, 2,
                                    self.height() - 4, self.height() - 4)
        painter.end()




class MyDialog(QPushButton):

    def __init__(self, text='...', type=0, filters='All Files (*)', lineEditObj=None):
        super().__init__()
        # size=[30,23]
        # self.setFixedSize(QSize(size[0], size[1]))
        self.filters = filters
        self.lineEditObj = lineEditObj
        self.setText(text)
        self.setCursor(Qt.PointingHandCursor)
        if type == 1:
            self.clicked.connect(self.select_file)
        elif type == 2:
            self.clicked.connect(self.select_files)
        elif type == 3:
            self.clicked.connect(self.select_directory)
        elif type == 4:
            self.clicked.connect(self.save_file)
        else:
            pass

    def select_file(self):
        ret = ""
        response, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select file",
            directory=os.getcwd(),
            filter=self.filters,
        )
        if self.lineEditObj != None and response != "":
            ret = os.path.abspath(response)
            self.lineEditObj.setText(ret)
        return ret


    def select_files(self):
        ret = []
        response, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Select files",
            directory=os.getcwd(),
            filter=self.filters,
        )
        if self.lineEditObj != None and response != []:
            for f in response:
                ret.append(os.path.abspath(f))
            ret = "; ".join(ret)
            self.lineEditObj.setText(ret)
        return ret


    def select_directory(self):
        ret = ""
        response = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select directory",
            directory=os.getcwd(),
        )
        if self.lineEditObj != None and response != "":
            ret = os.path.abspath(response)
            self.lineEditObj.setText(ret)
        return ret


    def save_file(self):
        ret = ""
        response, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save file name",
            directory=os.getcwd(),
            filter=self.filters,
        )
        if self.lineEditObj != None and response != "":
            ret = os.path.abspath(response)
            self.lineEditObj.setText(ret)
        return ret




class Setting(QWidget):
    def __init__(self):
        super().__init__()
        # project general setting (top section)
        # widgets
        lbl_proj = QLabel("Project general setting:")
        lbl_proj.setObjectName("lbl_proj")
        lbl_maindir = QLabel("Main dir:")
        lbl_maindir.setObjectName("lbl_maindir")
        self.le_maindir = MyLineEdit()
        self.le_maindir.setObjectName("le_maindir")
        self.le_maindir.setPlaceholderText("Full path to project main directory")
        self.le_maindir.textChanged.connect(self.le_maindir.isdir)
        browse_maindir = MyDialog(type=3, lineEditObj=self.le_maindir)
        lbl_startdate = QLabel("Start date:")
        lbl_startdate.setObjectName("lbl_startdate")
        self.le_startdate = MyLineEdit()
        self.le_startdate.setAlignment(Qt.AlignCenter)
        self.le_startdate.setObjectName("le_startdate")
        self.le_startdate.setPlaceholderText("YYYY-MM-DD")
        self.le_startdate.textChanged.connect(self.le_startdate.isdate)
        lbl_enddate = QLabel("End date:")
        lbl_enddate.setObjectName("lbl_enddate")
        self.le_enddate = MyLineEdit()
        self.le_enddate.setAlignment(Qt.AlignCenter)
        self.le_enddate.setObjectName("le_enddate")
        self.le_enddate.setPlaceholderText("YYYY-MM-DD")
        self.le_enddate.textChanged.connect(self.le_enddate.isdate)
        lbl_studyarea = QLabel("Study area boundaries")
        lbl_studyarea.setObjectName("lbl_studyarea")
        self.le_maxlat = MyLineEdit()
        self.le_maxlat.setObjectName("le_maxlat")
        self.le_maxlat.setAlignment(Qt.AlignCenter)
        self.le_maxlat.setPlaceholderText("Max Lat (deg)")
        self.le_maxlat.textChanged.connect(self.le_maxlat.islat)
        self.le_minlat = MyLineEdit()
        self.le_minlat.setObjectName("le_minlat")
        self.le_minlat.setAlignment(Qt.AlignCenter)
        self.le_minlat.setPlaceholderText("Min Lat (deg)")
        self.le_minlat.textChanged.connect(self.le_minlat.islat)
        self.le_minlon = MyLineEdit()
        self.le_minlon.setObjectName("le_minlon")
        self.le_minlon.setAlignment(Qt.AlignCenter)
        self.le_minlon.setPlaceholderText("Min Lon (deg)")
        self.le_minlon.textChanged.connect(self.le_minlon.islon)
        self.le_maxlon = MyLineEdit()
        self.le_maxlon.setObjectName("le_maxlon")
        self.le_maxlon.setAlignment(Qt.AlignCenter)
        self.le_maxlon.setPlaceholderText("Max Lon (deg)")
        self.le_maxlon.textChanged.connect(self.le_maxlon.islon)
        self.btn_showmap = QPushButton("Show map")
        self.btn_showmap.setObjectName("btn_showmap")
        self.btn_showmap.setEnabled(False)

        lbl_depend = QLabel("Program dependencies:")
        lbl_depend.setObjectName("lbl_depend")
        lbl_sac = QLabel("SAC:")
        lbl_sac.setObjectName("lbl_sac")
        self.le_sac = MyLineEdit()
        self.le_sac.setObjectName("le_sac")
        self.le_sac.setPlaceholderText("Full path to SAC executable")
        self.le_sac.textChanged.connect(self.le_sac.isfile)
        browse_sac = MyDialog(type=1, lineEditObj=self.le_sac)

        lbl_gmt = QLabel("GMT:")
        lbl_gmt.setObjectName("lbl_gmt")
        self.le_gmt = MyLineEdit()
        self.le_gmt.setObjectName("le_gmt")
        self.le_gmt.setPlaceholderText("Full path to GMT executable") 
        self.le_gmt.textChanged.connect(self.le_gmt.isfile)
        browse_gmt = MyDialog(type=1, lineEditObj=self.le_gmt)

        lbl_perl = QLabel("Perl:")
        lbl_perl.setObjectName("lbl_perl")
        self.le_perl = MyLineEdit()
        self.le_perl.setObjectName("le_perl")
        self.le_perl.setPlaceholderText("Full path to the Perl interpreter")
        self.le_perl.textChanged.connect(self.le_perl.isfile)
        browse_perl = MyDialog(type=1, lineEditObj=self.le_perl)

        # Design layouts

        ## Top Left/Right 
        lyo_tl = QGridLayout()
        lyo_tl.addWidget(lbl_maindir,0,0)
        lyo_tl.addWidget(self.le_maindir,0,1)
        lyo_tl.addWidget(browse_maindir,0,2)
        lyo_tl.addWidget(lbl_startdate,1,0)
        lyo_tl.addWidget(self.le_startdate,1,1)
        lyo_tl.addWidget(lbl_enddate,2,0)
        lyo_tl.addWidget(self.le_enddate,2,1)
        lyo_tl.setContentsMargins(0,0,0,0)
        lyo_tl.setVerticalSpacing(10)
        lyo_tl.setHorizontalSpacing(0)

        lyo_tr = QGridLayout()
        lyo_tr.addWidget(self.le_maxlat,0,1)
        lyo_tr.addWidget(self.le_minlon,1,0)
        lyo_tr.addWidget(self.le_maxlon,1,2)
        lyo_tr.addWidget(self.le_minlat,2,1)
        lyo_tr.addWidget(self.btn_showmap,3,1)
        lyo_tr.setContentsMargins(0,0,0,0)
        lyo_tr.setVerticalSpacing(10)
        lyo_tr.setHorizontalSpacing(0)

        lyo_top = QGridLayout()
        lyo_top.addWidget(lbl_proj, 0,0,1,3)
        lyo_top.addWidget(lbl_studyarea, 0,3,1,2)
        lyo_top.addLayout(lyo_tl,1,0,1,3)
        lyo_top.addLayout(lyo_tr,1,3,1,2)
        lyo_top.setVerticalSpacing(10)
        lyo_top.setHorizontalSpacing(30)
        lyo_top.setContentsMargins(0,0,0,0)

        ## bottom ##
        lyo_bottom = QGridLayout()
        lyo_bottom.addWidget(lbl_depend,0,0,1,3)
        lyo_bottom.addWidget(lbl_sac,1,0,1,1)
        lyo_bottom.addWidget(self.le_sac,1,1,1,1)
        lyo_bottom.addWidget(browse_sac,1,2,1,1)
        lyo_bottom.addWidget(lbl_gmt,2,0,1,1)
        lyo_bottom.addWidget(self.le_gmt,2,1,1,1)
        lyo_bottom.addWidget(browse_gmt,2,2,1,1)
        lyo_bottom.addWidget(lbl_perl,3,0,1,1)
        lyo_bottom.addWidget(self.le_perl,3,1,1,1)
        lyo_bottom.addWidget(browse_perl,3,2,1,1)
        lyo_bottom.setVerticalSpacing(10)
        lyo_bottom.setHorizontalSpacing(10)
        lyo_bottom.setContentsMargins(0,0,0,0)

        # put together top and bottom layouts
        self.layout = QVBoxLayout()
        self.layout.addLayout(lyo_top)
        self.layout.addLayout(lyo_bottom)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(60,60,60,60)
        self.setLayout(self.layout)

        self.le_minlat.textChanged.connect(lambda: self.showmap_button())
        self.le_maxlat.textChanged.connect(lambda: self.showmap_button())
        self.le_minlon.textChanged.connect(lambda: self.showmap_button())
        self.le_maxlon.textChanged.connect(lambda: self.showmap_button())
        
        map_window = OrthoMap()
        self.btn_showmap.clicked.connect(lambda: map_window.plot(float(self.le_minlat.text()),
                                                         float(self.le_maxlat.text()),
                                                         float(self.le_minlon.text()),
                                                         float(self.le_maxlon.text()) ))


    def get_parameters(self):
        setting = {}
        setting['le_maindir'] = self.le_maindir.text()
        if self.le_startdate.isdate() and self.le_enddate.isdate():
            if UTCDateTime(self.le_startdate.text()) <= UTCDateTime(self.le_enddate.text()):
                setting['le_startdate'] = self.le_startdate.text()
                setting['le_enddate'] = self.le_enddate.text()
            else:
                setting['le_startdate'] = ""
                setting['le_enddate'] = ""
        else:
            setting['le_startdate'] = ""
            setting['le_enddate'] = ""

        if self.le_minlat.islat() and self.le_maxlat.islat():
            if float(self.le_minlat.text()) < float(self.le_maxlat.text()):
                setting['le_minlat'] = self.le_minlat.text()
                setting['le_maxlat'] = self.le_maxlat.text()
            else:
                setting['le_minlat'] = ""
                setting['le_maxlat'] = ""
        else:
            setting['le_minlat'] = ""
            setting['le_maxlat'] = ""

        if self.le_minlon.islon() and self.le_maxlon.islon():
            if float(self.le_minlon.text()) < float(self.le_maxlon.text()):
                setting['le_minlon'] = self.le_minlon.text()
                setting['le_maxlon'] = self.le_maxlon.text()
            else:
                setting['le_minlon'] = ""
                setting['le_maxlon'] = ""
        else:
            setting['le_minlon'] = ""
            setting['le_maxlon'] = ""

        setting['le_sac'] = self.le_sac.text()
        setting['le_gmt'] = self.le_gmt.text()
        setting['le_perl'] = self.le_perl.text()
        return setting


    def showmap_button(self):
        all_filled_in = all([len(self.le_minlat.text()),
                             len(self.le_maxlat.text()),
                             len(self.le_minlon.text()),
                             len(self.le_maxlon.text())])
        correct_formats = all([self.le_minlat.islat(),
                               self.le_maxlat.islat(),
                               self.le_minlon.islon(),
                               self.le_maxlon.islon()])
        if all_filled_in and correct_formats:
            correct_values = all([float(self.le_minlat.text()) < float(self.le_maxlat.text()),
                                  float(self.le_minlon.text()) < float(self.le_maxlon.text())])
            if correct_values:
                self.btn_showmap.setEnabled(True)
                self.btn_showmap.setCursor(Qt.PointingHandCursor)
                return True
            else:
                self.btn_showmap.setEnabled(False)
                return False
        else:
            self.btn_showmap.setEnabled(False)
            return False




class OrthoMap(QMainWindow):
    def __init__(self):
        super().__init__()
        app_icon = QIcon()
        app_icon.addFile(os.path.join(images_dir,'icons','16x16.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','24x24.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','32x32.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','48x48.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','256x256.png'))
        self.setWindowIcon(app_icon)

    def plot(self, minlat, maxlat, minlon, maxlon):
        self.setWindowTitle(f'Show map:  longitude:[{minlon}, {maxlon}]; latitude:[{minlat}, {maxlat}]')
        plt.close()
        m = Basemap(llcrnrlon=minlon,llcrnrlat=minlat,urcrnrlon=maxlon,urcrnrlat=maxlat,
                    projection='cyl',resolution ='i',area_thresh=1000)
        m.drawcoastlines()
        m.drawcountries()
        m.drawmapboundary(fill_color='aqua')
        m.drawlsmask(ocean_color='white', land_color='white')
        m.fillcontinents(color='coral',lake_color='aqua')
        
        if (maxlat - minlat) > 40:
            dparallel = 20
        elif (maxlat - minlat) > 20:
            dparallel = 10
        elif (maxlat - minlat) > 10:
            dparallel = 5
        else:
            dparallel = 2

        if (maxlon - minlon) > 40:
            dmeridian = 30
        elif (maxlon - minlon) > 20:
            dmeridian = 10
        elif (maxlon - minlon) > 10:
            dmeridian = 5
        else:
            dmeridian = 2

        m.drawparallels(arange(-90,90+dparallel,dparallel), labels=[True, True, False, False])
        m.drawmeridians(arange(-180,180+dmeridian,dmeridian), labels=[False, False, True, True])
        img_bytes = QByteArray()
        img_buffer = QBuffer(img_bytes)
        img_buffer.open(QBuffer.WriteOnly)
        plt.tight_layout()
        plt.savefig(img_buffer, dpi=100, transparent=True)
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes)
        self.setFixedSize( QSize(pixmap.width(), pixmap.height()) )
        lbl = QLabel()
        lbl.setPixmap(pixmap)
        self.setCentralWidget(lbl)
        self.show()



class Download(QWidget):
    def __init__(self):
        super().__init__()
        lbl_datacenters = QLabel("Datacenters:")
        lbl_datacenters.setObjectName("lbl_datacenters")
        self.chb_dc_service_iris_edu = MyCheckBox()
        lbl_dc_service_iris_edu = QLabel("service.iris.edu")
        self.chb_dc_service_iris_edu.setObjectName("chb_dc_service_iris_edu")
        self.chb_dc_service_ncedc_org = MyCheckBox()
        lbl_dc_service_ncedc_org = QLabel("service.ncedc.org")
        self.chb_dc_service_ncedc_org.setObjectName("chb_dc_service_ncedc_org")
        self.chb_dc_service_scedc_caltech_edu = MyCheckBox()
        lbl_dc_service_scedc_caltech_edu = QLabel("service.scedc.caltech.edu")
        self.chb_dc_service_scedc_caltech_edu.setObjectName("chb_dc_service_scedc_caltech_edu")
        self.chb_dc_rtserve_beg_utexas_edu = MyCheckBox()
        lbl_dc_rtserve_beg_utexas_edu = QLabel("rtserve.beg.utexas.edu")
        self.chb_dc_rtserve_beg_utexas_edu.setObjectName("chb_dc_rtserve_beg_utexas_edu")
        self.chb_dc_eida_bgr_de = MyCheckBox()
        lbl_dc_eida_bgr_de = QLabel("eida.bgr.de")
        self.chb_dc_eida_bgr_de.setObjectName("chb_dc_eida_bgr_de")
        self.chb_dc_ws_resif_fr = MyCheckBox()
        lbl_dc_ws_resif_fr = QLabel("ws.resif.fr")
        self.chb_dc_ws_resif_fr.setObjectName("chb_dc_ws_resif_fr")
        self.chb_dc_seisrequest_iag_usp_br = MyCheckBox()
        lbl_dc_seisrequest_iag_usp_br = QLabel("seisrequest.iag.usp.br")
        self.chb_dc_seisrequest_iag_usp_br.setObjectName("chb_dc_seisrequest_iag_usp_br")
        self.chb_dc_eida_service_koeri_boun_edu_tr = MyCheckBox()
        lbl_dc_eida_service_koeri_boun_edu_tr = QLabel("eida-service.koeri.boun.edu.tr")
        self.chb_dc_eida_service_koeri_boun_edu_tr.setObjectName("chb_dc_eida_service_koeri_boun_edu_tr")
        self.chb_dc_eida_ethz_ch = MyCheckBox()
        lbl_dc_eida_ethz_ch = QLabel("eida.ethz.ch")
        self.chb_dc_eida_ethz_ch.setObjectName("chb_dc_eida_ethz_ch")
        self.chb_dc_geofon_gfz_potsdam_de = MyCheckBox()
        lbl_dc_geofon_gfz_potsdam_de = QLabel("geofon.gfz-potsdam.de")
        self.chb_dc_geofon_gfz_potsdam_de.setObjectName("chb_dc_geofon_gfz_potsdam_de")
        self.chb_dc_ws_icgc_cat = MyCheckBox()
        lbl_dc_ws_icgc_cat = QLabel("ws.icgc.cat")
        self.chb_dc_ws_icgc_cat.setObjectName("chb_dc_ws_icgc_cat")
        self.chb_dc_eida_ipgp_fr = MyCheckBox()
        lbl_dc_eida_ipgp_fr = QLabel("eida.ipgp.fr")
        self.chb_dc_eida_ipgp_fr.setObjectName("chb_dc_eida_ipgp_fr")
        self.chb_dc_fdsnws_raspberryshakedata_com = MyCheckBox()
        lbl_dc_fdsnws_raspberryshakedata_com = QLabel("fdsnws.raspberryshakedata.com")
        self.chb_dc_fdsnws_raspberryshakedata_com.setObjectName("chb_dc_fdsnws_raspberryshakedata_com")
        # column 3 widgets
        self.chb_dc_webservices_ingv_it = MyCheckBox()
        lbl_dc_webservices_ingv_it = QLabel("webservices.ingv.it")
        self.chb_dc_webservices_ingv_it.setObjectName("chb_dc_webservices_ingv_it")
        self.chb_dc_erde_geophysik_uni_muenchen_de = MyCheckBox()
        lbl_dc_erde_geophysik_uni_muenchen_de = QLabel("erde.geophysik.uni-muenchen.de")
        self.chb_dc_erde_geophysik_uni_muenchen_de.setObjectName("chb_dc_erde_geophysik_uni_muenchen_de")
        self.chb_dc_eida_sc3_infp_ro = MyCheckBox()
        lbl_dc_eida_sc3_infp_ro = QLabel("eida-sc3.infp.ro")
        self.chb_dc_eida_sc3_infp_ro.setObjectName("chb_dc_eida_sc3_infp_ro")
        self.chb_dc_eida_gein_noa_gr = MyCheckBox()
        lbl_dc_eida_gein_noa_gr = QLabel("eida.gein.noa.gr")
        self.chb_dc_eida_gein_noa_gr.setObjectName("chb_dc_eida_gein_noa_gr")
        self.chb_dc_www_orfeus_eu_org = MyCheckBox()
        lbl_dc_www_orfeus_eu_org = QLabel("www.orfeus-eu.org")
        self.chb_dc_www_orfeus_eu_org.setObjectName("chb_dc_www_orfeus_eu_org")
        self.chb_dc_auspass_edu_au = MyCheckBox()
        lbl_dc_auspass_edu_au = QLabel("auspass.edu.au")
        self.chb_dc_auspass_edu_au.setObjectName("chb_dc_auspass_edu_au")
        #### Download setting (bottom panel) ####
        # bottom left
        lbl_dlsetting = QLabel("Download setting:")
        lbl_dlsetting.setObjectName("lbl_dlsetting")
        lbl_stalist = QLabel("Station list file:")
        lbl_stalist.setObjectName("lbl_stalist")
        self.le_stalist = MyLineEdit()
        self.le_stalist.setObjectName("le_stalist")
        self.le_stalist.setPlaceholderText("Full path to station list file")
        # self.le_stalist.textChanged.connect(self.le_stalist.isfile)
        browse_stalist = MyDialog(type=1, lineEditObj=self.le_stalist)
        #
        lbl_stameta = QLabel("Station metadata dir:")
        lbl_stameta.setObjectName("lbl_stameta")
        self.le_stameta = MyLineEdit()
        self.le_stameta.setObjectName("le_stameta")
        self.le_stameta.setPlaceholderText("Full path to station metadata directory")
        # self.le_stameta.textChanged.connect(self.le_stameta.isdir)
        browse_stameta = MyDialog(type=3, lineEditObj=self.le_stameta)
        #
        lbl_mseeds = QLabel("MSEED dataset dir:")
        lbl_mseeds.setObjectName("lbl_mseeds")
        self.le_mseeds = MyLineEdit()
        self.le_mseeds.setObjectName("le_mseeds")
        self.le_mseeds.setPlaceholderText("Full path MSEED dataset directory")
        # self.le_mseeds.textChanged.connect(self.le_mseeds.isdir)
        browse_mseeds = MyDialog(type=3, lineEditObj=self.le_mseeds)
        #
        lbl_stalocs = QLabel("Station location codes:")
        lbl_stalocs.setObjectName("lbl_stalocs")
        self.le_stalocs = MyLineEdit()
        self.le_stalocs.setObjectName("le_stalocs")
        self.le_stalocs.setPlaceholderText("Station location codes separated by space")
        #
        lbl_stachns = QLabel("Station channels:")
        lbl_stachns.setObjectName("lbl_stachns")
        self.le_stachns = MyLineEdit()
        self.le_stachns.setObjectName("le_stachns")
        self.le_stachns.setPlaceholderText("Station channels separated by space")
        #
        lbl_timelen = QLabel("Timeseries length (s):")
        lbl_timelen.setObjectName("lbl_timelen")
        self.le_timelen = MyLineEdit()
        self.le_timelen.setObjectName("le_timelen")
        self.le_timelen.textChanged.connect(self.le_timelen.isposint)
        self.le_timelen.setPlaceholderText("Timeseries length in seconds")
        # bottom right
        lbl_dlscripts = QLabel("Download scripts:")
        lbl_dlscripts.setObjectName("lbl_dlscripts")
        lbl_obspy = QLabel("ObsPy script")
        lbl_fetch = QLabel("IRIS FetchData Perl script")
        self.chb_obspy = MyCheckBox()
        self.chb_obspy.setObjectName("chb_obspy")
        self.chb_fetch = MyCheckBox()
        self.chb_fetch.setObjectName("chb_fetch")

        # design layouts
        # top
        lyo_datacenters = QGridLayout()
        lyo_datacenters.addWidget(lbl_datacenters,0,0,1,6)
        lyo_datacenters.addWidget(self.chb_dc_service_iris_edu, 1,0)
        lyo_datacenters.addWidget(lbl_dc_service_iris_edu, 1,1)
        lyo_datacenters.addWidget(self.chb_dc_service_ncedc_org, 1,2)
        lyo_datacenters.addWidget(lbl_dc_service_ncedc_org, 1,3)
        lyo_datacenters.addWidget(self.chb_dc_service_scedc_caltech_edu, 1,4)
        lyo_datacenters.addWidget(lbl_dc_service_scedc_caltech_edu, 1,5)
        lyo_datacenters.addWidget(self.chb_dc_auspass_edu_au, 2,0)
        lyo_datacenters.addWidget(lbl_dc_auspass_edu_au, 2,1)
        lyo_datacenters.addWidget(self.chb_dc_eida_bgr_de, 2,2)
        lyo_datacenters.addWidget(lbl_dc_eida_bgr_de, 2,3)
        lyo_datacenters.addWidget(self.chb_dc_eida_ethz_ch, 2,4)
        lyo_datacenters.addWidget(lbl_dc_eida_ethz_ch, 2,5)
        lyo_datacenters.addWidget(self.chb_dc_eida_gein_noa_gr, 3,0)
        lyo_datacenters.addWidget(lbl_dc_eida_gein_noa_gr, 3,1)
        lyo_datacenters.addWidget(self.chb_dc_eida_ipgp_fr, 3,2)
        lyo_datacenters.addWidget(lbl_dc_eida_ipgp_fr, 3,3)
        lyo_datacenters.addWidget(self.chb_dc_eida_sc3_infp_ro, 3,4)
        lyo_datacenters.addWidget(lbl_dc_eida_sc3_infp_ro, 3,5)
        lyo_datacenters.addWidget(self.chb_dc_eida_service_koeri_boun_edu_tr, 4,0)
        lyo_datacenters.addWidget(lbl_dc_eida_service_koeri_boun_edu_tr, 4,1)
        lyo_datacenters.addWidget(self.chb_dc_erde_geophysik_uni_muenchen_de, 4,2)
        lyo_datacenters.addWidget(lbl_dc_erde_geophysik_uni_muenchen_de, 4,3)
        lyo_datacenters.addWidget(self.chb_dc_fdsnws_raspberryshakedata_com, 4,4)
        lyo_datacenters.addWidget(lbl_dc_fdsnws_raspberryshakedata_com, 4,5)
        lyo_datacenters.addWidget(self.chb_dc_geofon_gfz_potsdam_de, 5,0)
        lyo_datacenters.addWidget(lbl_dc_geofon_gfz_potsdam_de, 5,1)
        lyo_datacenters.addWidget(self.chb_dc_rtserve_beg_utexas_edu, 5,2)
        lyo_datacenters.addWidget(lbl_dc_rtserve_beg_utexas_edu, 5,3)
        lyo_datacenters.addWidget(self.chb_dc_seisrequest_iag_usp_br, 5,4)
        lyo_datacenters.addWidget(lbl_dc_seisrequest_iag_usp_br, 5,5)
        lyo_datacenters.addWidget(self.chb_dc_webservices_ingv_it, 6,0)
        lyo_datacenters.addWidget(lbl_dc_webservices_ingv_it, 6,1)
        lyo_datacenters.addWidget(self.chb_dc_ws_icgc_cat, 6,2)
        lyo_datacenters.addWidget(lbl_dc_ws_icgc_cat, 6,3)
        lyo_datacenters.addWidget(self.chb_dc_ws_resif_fr, 6,4)
        lyo_datacenters.addWidget(lbl_dc_ws_resif_fr, 6,5)
        lyo_datacenters.addWidget(self.chb_dc_www_orfeus_eu_org, 7,0,1,1)
        lyo_datacenters.addWidget(lbl_dc_www_orfeus_eu_org, 7,1,1,5)
        lyo_datacenters.setContentsMargins(30,15,50,0)
        lyo_datacenters.setSpacing(10)
        # bottom 
        lyo_bottom = QGridLayout()
        lyo_bottom.addWidget(lbl_dlsetting,0,0,1,3)
        lyo_bottom.addWidget(lbl_dlscripts,0,3,1,2)
        lyo_bottom.addWidget(lbl_stalist, 1,0,1,1)
        lyo_bottom.addWidget(self.le_stalist, 1,1,1,1)
        lyo_bottom.addWidget(browse_stalist, 1,2,1,1)
        lyo_bottom.addWidget(self.chb_fetch,1,3,1,1)
        lyo_bottom.addWidget(lbl_fetch,1,4,1,1)
        lyo_bottom.addWidget(self.chb_obspy,2,3,1,1)
        lyo_bottom.addWidget(lbl_obspy,2,4,1,1)
        lyo_bottom.addWidget(lbl_stameta, 2,0,1,1)
        lyo_bottom.addWidget(self.le_stameta, 2,1,1,1)
        lyo_bottom.addWidget(browse_stameta, 2,2,1,1)

        lyo_bottom.addWidget(lbl_mseeds, 3,0,1,1)
        lyo_bottom.addWidget(self.le_mseeds, 3,1,1,1)
        lyo_bottom.addWidget(browse_mseeds, 3,2,1,1)

        lyo_bottom.addWidget(lbl_stalocs, 4,0,1,1)
        lyo_bottom.addWidget(self.le_stalocs, 4,1,1,2)
        lyo_bottom.addWidget(lbl_stachns, 5,0,1,1)
        lyo_bottom.addWidget(self.le_stachns, 5,1,1,2)
        lyo_bottom.addWidget(lbl_timelen, 6,0,1,1)
        lyo_bottom.addWidget(self.le_timelen, 6,1,1,2)
        lyo_bottom.setSpacing(10)
        lyo_bottom.setContentsMargins(30,30,50,30)

        self.layout = QVBoxLayout()
        self.layout.addLayout(lyo_datacenters)
        self.layout.addLayout(lyo_bottom)
        self.setLayout(self.layout)

    def get_parameters(self):
        download = {}
        download['chb_dc_service_iris_edu'] = self.chb_dc_service_iris_edu.checkState()
        download['chb_dc_service_ncedc_org'] = self.chb_dc_service_ncedc_org.checkState()
        download['chb_dc_service_scedc_caltech_edu'] = self.chb_dc_service_scedc_caltech_edu.checkState()
        download['chb_dc_rtserve_beg_utexas_edu'] = self.chb_dc_rtserve_beg_utexas_edu.checkState()
        download['chb_dc_eida_bgr_de'] = self.chb_dc_eida_bgr_de.checkState()
        download['chb_dc_ws_resif_fr'] = self.chb_dc_ws_resif_fr.checkState()
        download['chb_dc_seisrequest_iag_usp_br'] = self.chb_dc_seisrequest_iag_usp_br.checkState()
        download['chb_dc_eida_service_koeri_boun_edu_tr'] = self.chb_dc_eida_service_koeri_boun_edu_tr.checkState()
        download['chb_dc_eida_ethz_ch'] = self.chb_dc_eida_ethz_ch.checkState()
        download['chb_dc_geofon_gfz_potsdam_de'] = self.chb_dc_geofon_gfz_potsdam_de.checkState()
        download['chb_dc_ws_icgc_cat'] = self.chb_dc_ws_icgc_cat.checkState()
        download['chb_dc_eida_ipgp_fr'] = self.chb_dc_eida_ipgp_fr.checkState()
        download['chb_dc_fdsnws_raspberryshakedata_com'] = self.chb_dc_fdsnws_raspberryshakedata_com.checkState()
        download['chb_dc_webservices_ingv_it'] = self.chb_dc_webservices_ingv_it.checkState()
        download['chb_dc_erde_geophysik_uni_muenchen_de'] = self.chb_dc_erde_geophysik_uni_muenchen_de.checkState()
        download['chb_dc_eida_sc3_infp_ro'] = self.chb_dc_eida_sc3_infp_ro.checkState()
        download['chb_dc_eida_gein_noa_gr'] = self.chb_dc_eida_gein_noa_gr.checkState()
        download['chb_dc_www_orfeus_eu_org'] = self.chb_dc_www_orfeus_eu_org.checkState()
        download['chb_dc_auspass_edu_au'] = self.chb_dc_auspass_edu_au.checkState()
        download['chb_obspy'] = self.chb_obspy.checkState()
        download['chb_fetch'] = self.chb_fetch.checkState()
        download['le_stalist'] = self.le_stalist.text()
        download['le_stameta'] = self.le_stameta.text()
        download['le_mseeds'] = self.le_mseeds.text()
        download['le_stalocs'] = self.le_stalocs.text()
        download['le_stachns'] = self.le_stachns.text()
        try:
            le_timelen = int(self.le_timelen.text())
        except Exception as e:
            le_timelen = ""
        download['le_timelen'] = le_timelen
        return download



class MSEED2SAC(QWidget):
    def __init__(self):
        super().__init__()

        # buttons graphics files
        icon_add = os.path.join(images_dir,"add.svg")
        icon_add_hover = os.path.join(images_dir,"add_hover.svg")
        if sys.platform == "win32":
            icon_add = icon_add.replace('\\','/')
            icon_add_hover = icon_add_hover.replace('\\','/')
        icon_remove = os.path.join(images_dir,"remove.svg")
        icon_remove_hover = os.path.join(images_dir,"remove_hover.svg")
        if sys.platform == "win32":
            icon_remove = icon_remove.replace('\\','/')
            icon_remove_hover = icon_remove_hover.replace('\\','/')

        self.mseed2sac_proc_frames = []

        self.scroll = QScrollArea()
        self.scroll.setObjectName("scroll_mseed2sac")
        self.scroll.setFrameShape(QFrame.Box)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.lyo_mseed2sac_proc_frames = QVBoxLayout(self.scroll_widget)
        self.lyo_mseed2sac_proc_frames.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_widget)
        self.add_rem_btns_mseed2sac = QWidget()
        self.add_rem_btns_mseed2sac.setObjectName("add_rem_btns_mseed2sac")
        self.add_rem_btns_mseed2sac.setStyleSheet("QPushButton {min-width: 35px; max-width: 35px;\
                                                 min-height: 35px; max-height: 35px;\
                                                 margin-top: 0px; margin-bottom: 0px; }\
                                    QPushButton:pressed {border: 3px solid #EEE;}")
        # Add process button
        self.btn_mseed2sac_add = QPushButton()
        self.btn_mseed2sac_add.setCursor(Qt.PointingHandCursor)
        self.btn_mseed2sac_add.setObjectName("btn_mseed2sac_add")
        qss_code = '''
            #btn_mseed2sac_add {
                image: url(%s);
            }

            #btn_mseed2sac_add:hover {
                image: url(%s);
            }
        ''' %(icon_add, icon_add_hover)
        self.btn_mseed2sac_add.setStyleSheet(qss_code)
        # Remove process button
        self.btn_mseed2sac_remove = QPushButton()
        self.btn_mseed2sac_remove.setCursor(Qt.PointingHandCursor)
        self.btn_mseed2sac_remove.setObjectName("btn_mseed2sac_remove")
        qss_code = '''
            #btn_mseed2sac_remove {
                image: url(%s);
            }

            #btn_mseed2sac_remove:hover {
                image: url(%s);
            }
        ''' %(icon_remove, icon_remove_hover)
        self.btn_mseed2sac_remove.setStyleSheet(qss_code)

        self.lyo_buttons = QHBoxLayout()
        self.lyo_buttons.addWidget(self.btn_mseed2sac_remove)
        self.lyo_buttons.addWidget(self.btn_mseed2sac_add)
        self.lyo_buttons.setAlignment(Qt.AlignCenter)
        self.add_rem_btns_mseed2sac.setLayout(self.lyo_buttons)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.add_rem_btns_mseed2sac)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10,20,10,10)
        self.setLayout(self.layout)

        # button signals and slots
        self.btn_mseed2sac_add.clicked.connect(lambda: self.add_proc_frame(pid=[0,0], params={}))
        self.btn_mseed2sac_remove.clicked.connect(self.remove_proc_frame)

    def get_num_procs(self):
        return len(self.mseed2sac_proc_frames)

    def add_proc_frame(self, pid=[0,0], params={}):
        pframe_id = self.get_num_procs()
        new_proc_frame = self.new_proc_frame(pframe_id=pframe_id, pid=pid, params=params)
        self.mseed2sac_proc_frames.append(new_proc_frame)
        self.lyo_mseed2sac_proc_frames.addWidget(self.mseed2sac_proc_frames[-1])


    def remove_proc_frame(self):
        nprocs = self.get_num_procs()
        if nprocs:
            proc_frame_obj = self.lyo_mseed2sac_proc_frames.itemAt(nprocs - 1).widget()
            proc_frame_obj.deleteLater()
            self.mseed2sac_proc_frames.pop()


    def new_proc_frame(self, pframe_id, pid=[0,0], params={}):
        proc_frame = QFrame()
        proc_type = self.new_proc_type(pframe_id=pframe_id, ptype_index=pid[0])
        proc_method = self.new_proc_method(pid=pid)
        proc_param = self.new_proc_param(pframe_id=pframe_id, pid=pid, params=params)
        proc_frame.setObjectName("proc_frame")
        proc_type.setObjectName("proc_type")
        proc_method.setObjectName("proc_method")
        proc_param.setObjectName("proc_param")
        # setup main layout
        lyo_proc_frame = QGridLayout()
        lyo_proc_frame.addWidget(proc_type, 0, 0)
        lyo_proc_frame.addWidget(proc_method, 1, 0)
        lyo_proc_frame.addWidget(proc_param, 0, 1, 2, 1)
        lyo_proc_frame.setContentsMargins(5,5,15,5)
        lyo_proc_frame.setHorizontalSpacing(0)
        proc_frame.setLayout(lyo_proc_frame)
        # stylesheet
        proc_frame.setStyleSheet("#%s {max-height: 180px; min-height: 180px;border: 3px solid #DDD; border-radius: 15px; margin-bottom: 10px; margin-right: 10px;}" %("proc_frame"))
        proc_type.setStyleSheet("#%s {min-width:280px; max-width:280px;}" %("proc_type"))
        proc_method.setStyleSheet("#%s {min-width:280px; max-width:280px;}" %("proc_method"))
        proc_param.setStyleSheet("#%s {border-left: 2px solid #DDD;}" %("proc_param"))
        # Signals and Slots
        cmb_proc_type = proc_type.layout().itemAt(1).widget()
        cmb_proc_method = proc_method.layout().itemAt(1).widget()
        cmb_proc_type.currentIndexChanged.connect(lambda: self.replace_proc_frame(pframe_id))
        cmb_proc_method.currentIndexChanged.connect(lambda: self.replace_proc_frame(pframe_id))
        return proc_frame


    def replace_proc_frame(self, pframe_id):
        current_proc_frame = self.mseed2sac_proc_frames[pframe_id]
        proc_type = current_proc_frame.layout().itemAt(0).widget()
        proc_method = current_proc_frame.layout().itemAt(1).widget()
        proc_type_index = proc_type.layout().itemAt(1).widget().currentIndex()
        proc_method_index = proc_method.layout().itemAt(1).widget().currentIndex()
        more_than_one_method = [2] # proc_type_index which has more than 1 method available
        if proc_type_index not in more_than_one_method or proc_method_index in [0, -1]:
            proc_method_index = 1
            proc_method_index = 1
        new_proc_frame = self.new_proc_frame(pframe_id, pid=[proc_type_index, proc_method_index])
        self.mseed2sac_proc_frames[pframe_id] = new_proc_frame
        self.lyo_mseed2sac_proc_frames.replaceWidget(current_proc_frame, new_proc_frame)
        current_proc_frame.deleteLater()


    def update_proc_param_ui(self, pframe_id):
        current_proc_frame = self.mseed2sac_proc_frames[pframe_id]
        proc_type = current_proc_frame.layout().itemAt(0).widget()
        proc_method = current_proc_frame.layout().itemAt(1).widget()
        proc_param = current_proc_frame.layout().itemAt(2).widget()
        proc_param_lyo = proc_param.layout()
        proc_type_index = proc_type.layout().itemAt(1).widget().currentIndex()
        proc_method_index = proc_method.layout().itemAt(1).widget().currentIndex()
        pid = [proc_type_index, proc_method_index]
        if pid == [1,1]: # MSEED to SAC - Method 1
            chb_mseed2sac_detrend = proc_param.findChild(MyCheckBox, 'chb_mseed2sac_detrend')
            chb_mseed2sac_taper = proc_param.findChild(MyCheckBox, 'chb_mseed2sac_taper')
            lbl_mseed2sac_detrend_method = proc_param.findChild(QLabel, 'lbl_mseed2sac_detrend_method')
            cmb_mseed2sac_detrend_method = proc_param.findChild(QComboBox, 'cmb_mseed2sac_detrend_method')
            lbl_mseed2sac_detrend_order = proc_param.findChild(QLabel, 'lbl_mseed2sac_detrend_order')
            sb_mseed2sac_detrend_order = proc_param.findChild(QSpinBox, 'sb_mseed2sac_detrend_order')
            lbl_mseed2sac_dspline = proc_param.findChild(QLabel, 'lbl_mseed2sac_dspline')
            le_mseed2sac_dspline = proc_param.findChild(QLineEdit, 'le_mseed2sac_dspline')
            lbl_mseed2sac_taper_method = proc_param.findChild(QLabel, 'lbl_mseed2sac_taper_method')
            cmb_mseed2sac_taper_method = proc_param.findChild(QComboBox, 'cmb_mseed2sac_taper_method')
            lbl_mseed2sac_max_taper = proc_param.findChild(QLabel, 'lbl_mseed2sac_max_taper')
            dsb_mseed2sac_max_taper = proc_param.findChild(QDoubleSpinBox, 'dsb_mseed2sac_max_taper')
            # Detrend Parameters
            if  chb_mseed2sac_detrend.checkState():
                lbl_mseed2sac_detrend_method.setEnabled(True)
                cmb_mseed2sac_detrend_method.setEnabled(True)
                if cmb_mseed2sac_detrend_method.currentIndex() in [2,3]:
                    lbl_mseed2sac_detrend_order.setEnabled(True)
                    sb_mseed2sac_detrend_order.setEnabled(True)
                else:
                    lbl_mseed2sac_detrend_order.setEnabled(False)
                    sb_mseed2sac_detrend_order.setEnabled(False)

                if cmb_mseed2sac_detrend_method.currentIndex() == 3:
                    lbl_mseed2sac_dspline.setEnabled(True)
                    le_mseed2sac_dspline.setEnabled(True)
                else:
                    lbl_mseed2sac_dspline.setEnabled(False)
                    le_mseed2sac_dspline.setEnabled(False)
            else:
                lbl_mseed2sac_detrend_method.setEnabled(False)
                cmb_mseed2sac_detrend_method.setEnabled(False)
                lbl_mseed2sac_detrend_order.setEnabled(False)
                sb_mseed2sac_detrend_order.setEnabled(False)
                lbl_mseed2sac_dspline.setEnabled(False)
                le_mseed2sac_dspline.setEnabled(False)
            # Taper Parameters
            if chb_mseed2sac_taper.checkState():
                lbl_mseed2sac_taper_method.setEnabled(True)
                cmb_mseed2sac_taper_method.setEnabled(True)
                lbl_mseed2sac_max_taper.setEnabled(True)
                dsb_mseed2sac_max_taper.setEnabled(True)
            else:
                lbl_mseed2sac_taper_method.setEnabled(False)
                cmb_mseed2sac_taper_method.setEnabled(False)
                lbl_mseed2sac_max_taper.setEnabled(False)
                dsb_mseed2sac_max_taper.setEnabled(False)
        if pid == [6,1]: # MSEED to SAC - detrend
            lbl_mseed2sac_detrend_method = proc_param.findChild(QLabel, 'lbl_mseed2sac_detrend_method')
            cmb_mseed2sac_detrend_method = proc_param.findChild(QComboBox, 'cmb_mseed2sac_detrend_method')
            lbl_mseed2sac_detrend_order = proc_param.findChild(QLabel, 'lbl_mseed2sac_detrend_order')
            sb_mseed2sac_detrend_order = proc_param.findChild(QSpinBox, 'sb_mseed2sac_detrend_order')
            lbl_mseed2sac_dspline = proc_param.findChild(QLabel, 'lbl_mseed2sac_dspline')
            le_mseed2sac_dspline = proc_param.findChild(QLineEdit, 'le_mseed2sac_dspline')

            # Detrend Parameters
            if cmb_mseed2sac_detrend_method.currentIndex() in [2,3]:
                lbl_mseed2sac_detrend_order.setEnabled(True)
                sb_mseed2sac_detrend_order.setEnabled(True)
            else:
                lbl_mseed2sac_detrend_order.setEnabled(False)
                sb_mseed2sac_detrend_order.setEnabled(False)

            if cmb_mseed2sac_detrend_method.currentIndex() == 3:
                lbl_mseed2sac_dspline.setEnabled(True)
                le_mseed2sac_dspline.setEnabled(True)
            else:
                lbl_mseed2sac_dspline.setEnabled(False)
                le_mseed2sac_dspline.setEnabled(False)



    def new_proc_type(self, pframe_id, ptype_index=0):
        proc_type = QFrame()
        proc_type.setObjectName("proc_type")
        proc_type.setObjectName(f"proc_type")

        lbl_proc_type = QLabel(f"Process #{pframe_id + 1}:")
        lbl_proc_type.setObjectName("lbl_proc_type")
        lbl_proc_type.setStyleSheet("#%s {color: #999;}" %("lbl_proc_type"))
        cmb_proc_type = QComboBox()
        cmb_proc_type.setObjectName("cmb_proc_type")
        cmb_proc_type.setEditable(True)
        cmb_proc_type.lineEdit().setAlignment(Qt.AlignCenter)
        cmb_proc_type.addItem("---- Select ----")
        cmb_proc_type.addItem("  MSEED to SAC")
        cmb_proc_type.addItem("  Decimate")
        cmb_proc_type.addItem("  Remove response")
        cmb_proc_type.addItem("  Bandpass filter")
        cmb_proc_type.addItem("  Cut seismogram")
        cmb_proc_type.addItem("  Detrend")
        cmb_proc_type.addItem("  Write headers")
        cmb_proc_type.addItem("  Remove channel")
        lyo_proc_type = QHBoxLayout()
        lyo_proc_type.addWidget(lbl_proc_type)
        lyo_proc_type.addWidget(cmb_proc_type)
        lyo_proc_type.setAlignment(Qt.AlignVCenter)
        lyo_proc_type.setAlignment(Qt.AlignRight)
        lyo_proc_type.setContentsMargins(20,0,20,0)
        proc_type.setLayout(lyo_proc_type)
        cmb_proc_type.setCurrentIndex(ptype_index)
        proc_type.setStyleSheet("#%s {min-width:250px; max-width:250px;}" %("proc_type"))
        return proc_type


    def new_proc_method(self, pid=[0,0]):
        proc_method = QFrame()
        proc_method.setObjectName("proc_method")
        cmb_proc_method = QComboBox()
        cmb_proc_method.setObjectName("cmb_proc_method")
        cmb_proc_method.addItem("---- Select ----")
        lyo_proc_method = QHBoxLayout()
        ptype_index = pid[0]
        pmethod_index = pid[1]
        if ptype_index == 1: # mseed to sac
            lbl_mseed2sac_method = QLabel("Method:")
            lbl_mseed2sac_method.setObjectName(f"lbl_mseed2sac_method")
            lbl_mseed2sac_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_mseed2sac_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("Obspy + SAC") # Method 1
            lyo_proc_method.addWidget(lbl_mseed2sac_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 2: # decimate
            lbl_decimate_method = QLabel("Method:")
            lbl_decimate_method.setObjectName(f"lbl_decimate_method")
            lbl_decimate_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_decimate_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: decimate") # Method 1
            cmb_proc_method.addItem("ObsPy: resample") # Method 2
            lyo_proc_method.addWidget(lbl_decimate_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 3: # remove response
            lbl_remresp_method = QLabel("Method:")
            lbl_remresp_method.setObjectName(f"lbl_remresp_method")
            lbl_remresp_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_remresp_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("ObsPy: remove_response") # Method 1
            lyo_proc_method.addWidget(lbl_remresp_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 4: # bandpass filter
            lbl_bandpass_method = QLabel("Method:")
            lbl_bandpass_method.setObjectName(f"lbl_bandpass_method")
            lbl_bandpass_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_bandpass_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: bp") # Method 1
            lyo_proc_method.addWidget(lbl_bandpass_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 5: # cut seismogram
            lbl_cut_method = QLabel("Method:")
            lbl_cut_method.setObjectName(f"lbl_cut_method")
            lbl_cut_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_cut_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: cuterr fillz") # Method 1
            lyo_proc_method.addWidget(lbl_cut_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 6: # Detrend
            lbl_detrend_method = QLabel("Method:")
            lbl_detrend_method.setObjectName(f"lbl_detrend_method")
            lbl_detrend_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_detrend_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("Obspy: detrend") # Method 1
            lyo_proc_method.addWidget(lbl_detrend_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 7: # chnhdr
            lbl_chnhdr_method = QLabel("Method:")
            lbl_chnhdr_method.setObjectName(f"lbl_chnhdr_method")
            lbl_chnhdr_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_chnhdr_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: chnhdr") # Method 1
            lyo_proc_method.addWidget(lbl_chnhdr_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 8: # remove channel
            lbl_remchn_method = QLabel("Method:")
            lbl_remchn_method.setObjectName(f"lbl_remchn_method")
            lbl_remchn_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_remchn_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("Python script") # Method 1
            lyo_proc_method.addWidget(lbl_remchn_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        else:
            lbl_bandpass_method = QLabel("Method:")
            lbl_bandpass_method.setVisible(False)
            cmb_proc_method.setVisible(False)
            lyo_proc_method.addWidget(lbl_bandpass_method)
            lyo_proc_method.addWidget(cmb_proc_method)

        lyo_proc_method.setAlignment(Qt.AlignVCenter)
        lyo_proc_method.setAlignment(Qt.AlignRight)
        lyo_proc_method.setContentsMargins(20,0,20,0)
        proc_method.setLayout(lyo_proc_method)
        proc_method.setStyleSheet("#%s {min-width:250px; max-width:250px;}" %("proc_method"))
        cmb_proc_method.setCurrentIndex(pmethod_index)
        return proc_method


    def new_proc_param(self, pframe_id, pid=[0,0], params={}):
        proc_param = QWidget()
        proc_param.setObjectName(f"proc_param")
        lyo_proc_param = QGridLayout()
        if len(params) == 0:
            params = self.default_proc_params(pid)
        if pid == [1,1]: # MSEED to SAC - Method 1
            chb_mseed2sac_taper = MyCheckBox()
            chb_mseed2sac_taper.setObjectName("chb_mseed2sac_taper")
            lbl_mseed2sac_taper = QLabel("Taper")
            lbl_mseed2sac_taper.setObjectName("lbl_mseed2sac_taper")
            chb_mseed2sac_detrend = MyCheckBox()
            chb_mseed2sac_detrend.setObjectName("chb_mseed2sac_detrend")
            lbl_mseed2sac_detrend = QLabel("Detrend")
            lbl_mseed2sac_detrend.setObjectName("lbl_mseed2sac_detrend")
            lbl_mseed2sac_taper_method = QLabel("Taper method:")
            lbl_mseed2sac_taper_method.setObjectName("lbl_mseed2sac_taper_method")
            cmb_mseed2sac_taper_method = QComboBox()
            cmb_mseed2sac_taper_method.setObjectName("cmb_mseed2sac_taper_method")
            cmb_mseed2sac_taper_method.addItem("ObsPy: taper(type='hann')")
            lbl_mseed2sac_max_taper = QLabel("Taper max perc:")
            lbl_mseed2sac_max_taper.setObjectName("lbl_mseed2sac_max_taper")
            dsb_mseed2sac_max_taper = QDoubleSpinBox()
            dsb_mseed2sac_max_taper.setMinimum(0.0)
            dsb_mseed2sac_max_taper.setMaximum(0.5)
            dsb_mseed2sac_max_taper.setDecimals(3)
            dsb_mseed2sac_max_taper.setSingleStep(0.001)
            dsb_mseed2sac_max_taper.setObjectName("dsb_mseed2sac_max_taper")
            lbl_mseed2sac_detrend_method = QLabel("Detrend method:")
            lbl_mseed2sac_detrend_method.setObjectName("lbl_mseed2sac_detrend_method")
            cmb_mseed2sac_detrend_method = QComboBox()
            cmb_mseed2sac_detrend_method.setObjectName("cmb_mseed2sac_detrend_method")
            cmb_mseed2sac_detrend_method.addItem("Demean")
            cmb_mseed2sac_detrend_method.addItem("Linear")
            cmb_mseed2sac_detrend_method.addItem("Polynomial")
            cmb_mseed2sac_detrend_method.addItem("Spline")
            lbl_mseed2sac_detrend_order = QLabel("Detrend order:")
            lbl_mseed2sac_detrend_order.setObjectName("lbl_mseed2sac_detrend_order")
            sb_mseed2sac_detrend_order = QSpinBox()
            sb_mseed2sac_detrend_order.setObjectName("sb_mseed2sac_detrend_order")
            sb_mseed2sac_detrend_order.setMinimum(3)
            sb_mseed2sac_detrend_order.setMaximum(5)
            sb_mseed2sac_detrend_order.setSingleStep(1)
            lbl_mseed2sac_dspline = QLabel("dspline:")
            lbl_mseed2sac_dspline.setObjectName("lbl_mseed2sac_dspline")
            le_mseed2sac_dspline = MyLineEdit()
            le_mseed2sac_dspline.setObjectName("le_mseed2sac_dspline")
            le_mseed2sac_dspline.setPlaceholderText("Number of samples between nodes (spline method)")
            # set parameters
            chb_mseed2sac_detrend.setCheckState(params['chb_mseed2sac_detrend'])
            chb_mseed2sac_taper.setCheckState(params['chb_mseed2sac_taper'])
            cmb_mseed2sac_taper_method.setCurrentIndex(params["cmb_mseed2sac_taper_method"])
            dsb_mseed2sac_max_taper.setValue(params["dsb_mseed2sac_max_taper"])
            cmb_mseed2sac_detrend_method.setCurrentIndex(params["cmb_mseed2sac_detrend_method"])
            sb_mseed2sac_detrend_order.setValue(params["sb_mseed2sac_detrend_order"])
            le_mseed2sac_dspline.setText(f"{params['le_mseed2sac_dspline']}")
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_detrend, 0,1,1,1)
            lyo_proc_param.addWidget(chb_mseed2sac_detrend, 0,0,1,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_detrend_method, 1,0,1,2)
            lyo_proc_param.addWidget(cmb_mseed2sac_detrend_method, 1,2)
            lyo_proc_param.addWidget(lbl_mseed2sac_detrend_order, 2,0,1,2)
            lyo_proc_param.addWidget(sb_mseed2sac_detrend_order, 2,2)
            lyo_proc_param.addWidget(lbl_mseed2sac_dspline, 3,0,1,2)
            lyo_proc_param.addWidget(le_mseed2sac_dspline, 3,2)
            lyo_proc_param.addWidget(lbl_mseed2sac_taper, 0,4,1,1)
            lyo_proc_param.addWidget(chb_mseed2sac_taper, 0,3,1,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_taper_method, 1,3,1,2)
            lyo_proc_param.addWidget(cmb_mseed2sac_taper_method, 1,5)
            lyo_proc_param.addWidget(lbl_mseed2sac_max_taper, 2,3,1,2)
            lyo_proc_param.addWidget(dsb_mseed2sac_max_taper, 2,5)
            lyo_proc_param.setHorizontalSpacing(20)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(50,0,50,0)
            # UPDATE UI BASED ON INPUT PARAMETERS
            # 1) Detrend Parameters
            if  chb_mseed2sac_detrend.checkState():
                lbl_mseed2sac_detrend_method.setEnabled(True)
                cmb_mseed2sac_detrend_method.setEnabled(True)
                if cmb_mseed2sac_detrend_method.currentIndex() in [2,3]:
                    lbl_mseed2sac_detrend_order.setEnabled(True)
                    sb_mseed2sac_detrend_order.setEnabled(True)
                else:
                    lbl_mseed2sac_detrend_order.setEnabled(False)
                    sb_mseed2sac_detrend_order.setEnabled(False)
                    
                if cmb_mseed2sac_detrend_method.currentIndex() == 3:
                    lbl_mseed2sac_dspline.setEnabled(True)
                    le_mseed2sac_dspline.setEnabled(True)
                else:
                    lbl_mseed2sac_dspline.setEnabled(False)
                    le_mseed2sac_dspline.setEnabled(False)
            else:
                lbl_mseed2sac_detrend_method.setEnabled(False)
                cmb_mseed2sac_detrend_method.setEnabled(False)
                lbl_mseed2sac_detrend_order.setEnabled(False)
                sb_mseed2sac_detrend_order.setEnabled(False)
                lbl_mseed2sac_dspline.setEnabled(False)
                le_mseed2sac_dspline.setEnabled(False)
            # 2) Taper Parameters
            if chb_mseed2sac_taper.checkState():
                lbl_mseed2sac_taper_method.setEnabled(True)
                cmb_mseed2sac_taper_method.setEnabled(True)
                lbl_mseed2sac_max_taper.setEnabled(True)
                dsb_mseed2sac_max_taper.setEnabled(True)
            else:
                lbl_mseed2sac_taper_method.setEnabled(False)
                cmb_mseed2sac_taper_method.setEnabled(False)
                lbl_mseed2sac_max_taper.setEnabled(False)
                dsb_mseed2sac_max_taper.setEnabled(False)
            # signals and slots
            chb_mseed2sac_detrend.stateChanged.connect(lambda: self.update_proc_param_ui(pframe_id))
            chb_mseed2sac_taper.stateChanged.connect(lambda: self.update_proc_param_ui(pframe_id))
            cmb_mseed2sac_detrend_method.currentIndexChanged.connect(lambda: self.update_proc_param_ui(pframe_id))
            chb_mseed2sac_taper.setTristate(False)
            chb_mseed2sac_detrend.setTristate(False)
            le_mseed2sac_dspline.textChanged.connect(le_mseed2sac_dspline.isfloat)
        elif pid == [2,1] or pid == [2,2]: # Decimate - Method 1 & 2
            lbl_mseed2sac_finalSF = QLabel("Final sampling frequency:")
            cmb_mseed2sac_final_sf = QComboBox()
            cmb_mseed2sac_final_sf.addItem("1 Hz")
            cmb_mseed2sac_final_sf.addItem("2 Hz")
            cmb_mseed2sac_final_sf.addItem("5 Hz")
            cmb_mseed2sac_final_sf.addItem("10 Hz")
            cmb_mseed2sac_final_sf.addItem("20 Hz")
            cmb_mseed2sac_final_sf.setObjectName('cmb_mseed2sac_final_sf')
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_finalSF,0,0)
            lyo_proc_param.addWidget(cmb_mseed2sac_final_sf,0,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            cmb_mseed2sac_final_sf.setCurrentIndex(params['cmb_mseed2sac_final_sf'])
        elif pid == [3,1]: # Remove response - Method 1
            lbl_mseed2sac_stametadir = QLabel("Station metadata dir:")
            le_mseed2sac_stametadir = MyLineEdit()
            le_mseed2sac_stametadir.setObjectName("le_mseed2sac_stametadir")
            le_mseed2sac_stametadir.setPlaceholderText("Full path to station metadata directory")
            le_mseed2sac_stametadir.isdir()
            le_mseed2sac_stametadir.textChanged.connect(le_mseed2sac_stametadir.isdir)
            browse_mseed2sac_stametadir = MyDialog(type=3, lineEditObj=le_mseed2sac_stametadir)
            lbl_mseed2sac_resp_output = QLabel("Output unit:")
            cmb_mseed2sac_resp_output = QComboBox()
            cmb_mseed2sac_resp_output.setObjectName('cmb_mseed2sac_resp_output')
            cmb_mseed2sac_resp_output.setEditable(True)
            cmb_mseed2sac_resp_output.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_mseed2sac_resp_output.addItem("Displacement (m)")
            cmb_mseed2sac_resp_output.addItem("Velocity (m/s)")
            cmb_mseed2sac_resp_output.addItem("Acceleration (m/s**2)")
            lbl_mseed2sac_resp_prefilter = QLabel("Deconvolution pre-filter:")
            cmb_mseed2sac_resp_prefilter = QComboBox()
            cmb_mseed2sac_resp_prefilter.setObjectName('cmb_mseed2sac_resp_prefilter')
            cmb_mseed2sac_resp_prefilter.setEditable(True)
            cmb_mseed2sac_resp_prefilter.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_mseed2sac_resp_prefilter.addItem("None")
            cmb_mseed2sac_resp_prefilter.addItem("(0.005, 0.006, 30.0, 35.0)")
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_stametadir, 0,0)
            lyo_proc_param.addWidget(le_mseed2sac_stametadir, 0,1)
            lyo_proc_param.addWidget(browse_mseed2sac_stametadir, 0,2)
            lyo_proc_param.addWidget(lbl_mseed2sac_resp_output, 1,0)
            lyo_proc_param.addWidget(cmb_mseed2sac_resp_output, 1,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_resp_prefilter, 2,0)
            lyo_proc_param.addWidget(cmb_mseed2sac_resp_prefilter, 2,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_mseed2sac_stametadir.setText(f"{params['le_mseed2sac_stametadir']}")
            cmb_mseed2sac_resp_output.setCurrentIndex(params['cmb_mseed2sac_resp_output'])
            cmb_mseed2sac_resp_prefilter.setCurrentIndex(params['cmb_mseed2sac_resp_prefilter'])
        elif pid == [4,1]: # bandpass filter - Method 1
            lbl_mseed2sac_bp_cp1 = QLabel("Left corner period (s):")
            le_mseed2sac_bp_cp1 = MyLineEdit()
            le_mseed2sac_bp_cp1.setObjectName('le_mseed2sac_bp_cp1')
            le_mseed2sac_bp_cp1.setAlignment(Qt.AlignCenter)
            le_mseed2sac_bp_cp1.setPlaceholderText("Bandpass left corner period (s)")
            le_mseed2sac_bp_cp1.textChanged.connect(le_mseed2sac_bp_cp1.isfloat)
            lbl_mseed2sac_bp_cp2 = QLabel("Right corner period (s):")
            le_mseed2sac_bp_cp2 = MyLineEdit()
            le_mseed2sac_bp_cp2.setObjectName('le_mseed2sac_bp_cp2')
            le_mseed2sac_bp_cp2.setAlignment(Qt.AlignCenter)
            le_mseed2sac_bp_cp2.setPlaceholderText("Bandpass right corner period (s)")
            le_mseed2sac_bp_cp2.textChanged.connect(le_mseed2sac_bp_cp2.isfloat)
            lbl_mseed2sac_bp_poles = QLabel("Number of poles (n):")
            sb_mseed2sac_bp_poles = QSpinBox()
            sb_mseed2sac_bp_poles.setObjectName('sb_mseed2sac_bp_poles')
            sb_mseed2sac_bp_poles.setMinimum(1)
            sb_mseed2sac_bp_poles.setMaximum(10)
            sb_mseed2sac_bp_poles.setSingleStep(1)
            lbl_mseed2sac_bp_passes = QLabel("Number of passes (p):")
            sb_mseed2sac_bp_passes = QSpinBox()
            sb_mseed2sac_bp_passes.setObjectName('sb_mseed2sac_bp_passes')
            sb_mseed2sac_bp_passes.setMinimum(1)
            sb_mseed2sac_bp_passes.setMaximum(2)
            sb_mseed2sac_bp_passes.setSingleStep(1)
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_bp_cp1, 0,0)
            lyo_proc_param.addWidget(le_mseed2sac_bp_cp1, 0,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_bp_cp2, 1,0)
            lyo_proc_param.addWidget(le_mseed2sac_bp_cp2, 1,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_bp_poles, 0,2)
            lyo_proc_param.addWidget(sb_mseed2sac_bp_poles, 0,3)
            lyo_proc_param.addWidget(lbl_mseed2sac_bp_passes, 1,2)
            lyo_proc_param.addWidget(sb_mseed2sac_bp_passes, 1,3)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setVerticalSpacing(15)
            lyo_proc_param.setContentsMargins(50,0,50,0)
            # set parameters
            le_mseed2sac_bp_cp1.setText(f"{params['le_mseed2sac_bp_cp1']}")
            le_mseed2sac_bp_cp2.setText(f"{params['le_mseed2sac_bp_cp2']}")
            sb_mseed2sac_bp_poles.setValue(params['sb_mseed2sac_bp_poles'])
            sb_mseed2sac_bp_passes.setValue(params['sb_mseed2sac_bp_passes'])
        elif pid == [5,1]: # Cut seismogram - Method 1
            lbl_mseed2sac_cut_begin = QLabel("Cut begin (s):")
            le_mseed2sac_cut_begin = MyLineEdit()
            le_mseed2sac_cut_begin.setObjectName("le_mseed2sac_cut_begin")
            lbl_mseed2sac_cut_end = QLabel("Cut end (s):")
            le_mseed2sac_cut_end = MyLineEdit()
            le_mseed2sac_cut_end.setObjectName("le_mseed2sac_cut_end")
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_cut_begin, 0,0)
            lyo_proc_param.addWidget(le_mseed2sac_cut_begin, 0,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_cut_end, 1,0)
            lyo_proc_param.addWidget(le_mseed2sac_cut_end, 1,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_mseed2sac_cut_begin.setText(f"{params['le_mseed2sac_cut_begin']}")
            le_mseed2sac_cut_end.setText(f"{params['le_mseed2sac_cut_end']}")
        elif pid == [6,1]: # Detrend - Method 1
            lbl_mseed2sac_detrend_method = QLabel("Detrend method:")
            lbl_mseed2sac_detrend_method.setObjectName("lbl_mseed2sac_detrend_method")
            cmb_mseed2sac_detrend_method = QComboBox()
            cmb_mseed2sac_detrend_method.setObjectName("cmb_mseed2sac_detrend_method")
            cmb_mseed2sac_detrend_method.addItem("Demean")
            cmb_mseed2sac_detrend_method.addItem("Linear")
            cmb_mseed2sac_detrend_method.addItem("Polynomial")
            cmb_mseed2sac_detrend_method.addItem("Spline")
            lbl_mseed2sac_detrend_order = QLabel("Detrend order:")
            lbl_mseed2sac_detrend_order.setObjectName("lbl_mseed2sac_detrend_order")
            sb_mseed2sac_detrend_order = QSpinBox()
            sb_mseed2sac_detrend_order.setObjectName("sb_mseed2sac_detrend_order")
            sb_mseed2sac_detrend_order.setMinimum(3)
            sb_mseed2sac_detrend_order.setMaximum(5)
            sb_mseed2sac_detrend_order.setSingleStep(1)
            lbl_mseed2sac_dspline = QLabel("dspline:")
            lbl_mseed2sac_dspline.setObjectName("lbl_mseed2sac_dspline")
            le_mseed2sac_dspline = MyLineEdit()
            le_mseed2sac_dspline.setObjectName("le_mseed2sac_dspline")
            le_mseed2sac_dspline.setPlaceholderText("Number of samples between nodes (spline method)")
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_detrend_method, 1,0,1,2)
            lyo_proc_param.addWidget(cmb_mseed2sac_detrend_method, 1,2)
            lyo_proc_param.addWidget(lbl_mseed2sac_detrend_order, 2,0,1,2)
            lyo_proc_param.addWidget(sb_mseed2sac_detrend_order, 2,2)
            lyo_proc_param.addWidget(lbl_mseed2sac_dspline, 3,0,1,2)
            lyo_proc_param.addWidget(le_mseed2sac_dspline, 3,2)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(85,0,75,0)
            # set UI parameters
            cmb_mseed2sac_detrend_method.setCurrentIndex(params["cmb_mseed2sac_detrend_method"])
            sb_mseed2sac_detrend_order.setValue(params["sb_mseed2sac_detrend_order"])
            le_mseed2sac_dspline.setText(f"{params['le_mseed2sac_dspline']}")
            # signals ans slots
            cmb_mseed2sac_detrend_method.currentIndexChanged.connect(lambda: self.update_proc_param_ui(pframe_id))
            le_mseed2sac_dspline.textChanged.connect(le_mseed2sac_dspline.isfloat)

            # update UI
            if cmb_mseed2sac_detrend_method.currentIndex() in [2,3]:
                lbl_mseed2sac_detrend_order.setEnabled(True)
                sb_mseed2sac_detrend_order.setEnabled(True)
            else:
                lbl_mseed2sac_detrend_order.setEnabled(False)
                sb_mseed2sac_detrend_order.setEnabled(False)
                
            if cmb_mseed2sac_detrend_method.currentIndex() == 3:
                lbl_mseed2sac_dspline.setEnabled(True)
                le_mseed2sac_dspline.setEnabled(True)
            else:
                lbl_mseed2sac_dspline.setEnabled(False)
                le_mseed2sac_dspline.setEnabled(False)
        elif pid == [7,1]: # Write headers - Method 1
            lbl_mseed2sac_stametadir = QLabel("Station metadata dir:")
            le_mseed2sac_stametadir = MyLineEdit()
            le_mseed2sac_stametadir.setObjectName("le_mseed2sac_stametadir")
            le_mseed2sac_stametadir.setPlaceholderText("Full path to station metadata directory")
            le_mseed2sac_stametadir.isdir()
            le_mseed2sac_stametadir.textChanged.connect(le_mseed2sac_stametadir.isdir)
            browse_mseed2sac_stametadir = MyDialog(type=3, lineEditObj=le_mseed2sac_stametadir)
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_stametadir, 0,0)
            lyo_proc_param.addWidget(le_mseed2sac_stametadir, 0,1)
            lyo_proc_param.addWidget(browse_mseed2sac_stametadir, 0,2)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_mseed2sac_stametadir.setText(f"{params['le_mseed2sac_stametadir']}")
        elif pid == [8,1]: # Remove channel - Method 1
            lbl_mseed2sac_similar_channels = QLabel("If all these channels were available:")
            le_mseed2sac_similar_channels = QLineEdit()
            le_mseed2sac_similar_channels.setObjectName("le_mseed2sac_similar_channels")
            lbl_mseed2sac_channels2keep = QLabel("Only keep these channels:")
            le_mseed2sac_channels2keep = QLineEdit()
            le_mseed2sac_channels2keep.setObjectName("le_mseed2sac_channels2keep")
            # setup layout
            lyo_proc_param.addWidget(lbl_mseed2sac_similar_channels, 0,0)
            lyo_proc_param.addWidget(le_mseed2sac_similar_channels, 0,1)
            lyo_proc_param.addWidget(lbl_mseed2sac_channels2keep, 1,0)
            lyo_proc_param.addWidget(le_mseed2sac_channels2keep, 1,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_mseed2sac_similar_channels.setText(f"{params['le_mseed2sac_similar_channels']}")
            le_mseed2sac_channels2keep.setText(f"{params['le_mseed2sac_channels2keep']}")

        proc_param.setLayout(lyo_proc_param)
        proc_param.setStyleSheet("#%s {border-left: 2px solid #DDD;}" %("proc_param"))
        return proc_param


    def default_proc_params(self, pid):
        mseed2sac_proc_params = {"pid": [0,0]}
        if pid == [1,1]: # MSEED to SAC - Method 1
            mseed2sac_proc_params["pid"] = [1,1]
            mseed2sac_proc_params["chb_mseed2sac_taper"] = 2
            mseed2sac_proc_params["chb_mseed2sac_detrend"] = 2
            mseed2sac_proc_params["cmb_mseed2sac_taper_method"] = 0
            mseed2sac_proc_params["dsb_mseed2sac_max_taper"] = 0.005
            mseed2sac_proc_params["cmb_mseed2sac_detrend_method"] = 3
            mseed2sac_proc_params["sb_mseed2sac_detrend_order"] = 4
            mseed2sac_proc_params["le_mseed2sac_dspline"] = 864000
        elif pid == [2,1]: # Decimate - Method 1
            mseed2sac_proc_params["pid"] = [2,1]
            mseed2sac_proc_params["cmb_mseed2sac_final_sf"] = 0
        elif pid == [2,2]: # Decimate - Method 2
            mseed2sac_proc_params["pid"] = [2,2]
            mseed2sac_proc_params["cmb_mseed2sac_final_sf"] = 0
        elif pid == [3,1]: # Remove response - Method 1
            mseed2sac_proc_params["pid"] = [3,1]
            mseed2sac_proc_params["le_mseed2sac_stametadir"] = os.path.abspath("./metadata")
            mseed2sac_proc_params["cmb_mseed2sac_resp_output"] = 1
            mseed2sac_proc_params["cmb_mseed2sac_resp_prefilter"] = 1
        elif pid == [4,1]: # Bandpass filter - Method 1
            mseed2sac_proc_params["pid"] = [4,1]
            mseed2sac_proc_params["le_mseed2sac_bp_cp1"] = "4"
            mseed2sac_proc_params["le_mseed2sac_bp_cp2"] = "500"
            mseed2sac_proc_params["sb_mseed2sac_bp_poles"] = 3
            mseed2sac_proc_params["sb_mseed2sac_bp_passes"] = 2
        elif pid == [5,1]: # Cut seismogram - Method 1
            mseed2sac_proc_params["pid"] = [5,1]
            mseed2sac_proc_params["le_mseed2sac_cut_begin"] = ""
            mseed2sac_proc_params["le_mseed2sac_cut_end"] = ""
        elif pid == [6,1]: # Detrend - Method 1
            mseed2sac_proc_params["cmb_mseed2sac_detrend_method"] = 3
            mseed2sac_proc_params["sb_mseed2sac_detrend_order"] = 4
            mseed2sac_proc_params["le_mseed2sac_dspline"] = 864000
        elif pid == [7,1]: # Write headers - Method 1
            mseed2sac_proc_params["le_mseed2sac_stametadir"] = os.path.abspath("./metadata")
        elif pid == [8,1]: # Remove extra channel - Method 1
            mseed2sac_proc_params["pid"] = [8,1]
            mseed2sac_proc_params["le_mseed2sac_similar_channels"] = "BHZ HHZ"
            mseed2sac_proc_params["le_mseed2sac_channels2keep"] = "BHZ"
        return mseed2sac_proc_params


    def get_parameters(self):
        mseed2sac = {}
        mseed2sac['mseed2sac_procs'] = []
        nprocs = self.get_num_procs()
        for i in range(nprocs):
            proc_frame = self.mseed2sac_proc_frames[i]
            proc_type = proc_frame.layout().itemAt(0).widget()
            proc_method = proc_frame.layout().itemAt(1).widget()
            proc_param = proc_frame.layout().itemAt(2).widget()
            proc_type_index = proc_type.layout().itemAt(1).widget().currentIndex()
            proc_method_index = proc_method.layout().itemAt(1).widget().currentIndex()
            if proc_type_index > 0 and proc_method_index > 0:
                proc = {}
                pid = [proc_type_index, proc_method_index]
                proc['pid'] = pid
                if pid == [1,1]: # MSEED to SAC - Method 1
                    chb_mseed2sac_detrend = proc_param.findChild(MyCheckBox, 'chb_mseed2sac_detrend').checkState()
                    chb_mseed2sac_taper = proc_param.findChild(MyCheckBox, 'chb_mseed2sac_taper').checkState()
                    cmb_mseed2sac_detrend_method = proc_param.findChild(QComboBox, 'cmb_mseed2sac_detrend_method').currentIndex()
                    sb_mseed2sac_detrend_order = proc_param.findChild(QSpinBox, 'sb_mseed2sac_detrend_order').value()
                    le_mseed2sac_dspline = proc_param.findChild(MyLineEdit, 'le_mseed2sac_dspline').text()
                    cmb_mseed2sac_taper_method = proc_param.findChild(QComboBox, 'cmb_mseed2sac_taper_method').currentIndex()
                    dsb_mseed2sac_max_taper = proc_param.findChild(QDoubleSpinBox, 'dsb_mseed2sac_max_taper').value()
                    proc['chb_mseed2sac_detrend'] = chb_mseed2sac_detrend
                    proc['chb_mseed2sac_taper'] = chb_mseed2sac_taper
                    proc['cmb_mseed2sac_detrend_method'] = cmb_mseed2sac_detrend_method
                    proc['sb_mseed2sac_detrend_order'] = sb_mseed2sac_detrend_order
                    proc['le_mseed2sac_dspline'] = le_mseed2sac_dspline
                    proc['cmb_mseed2sac_taper_method'] = cmb_mseed2sac_taper_method
                    proc['dsb_mseed2sac_max_taper'] = dsb_mseed2sac_max_taper
                elif pid == [2,1] or pid == [2,2]: # Decimate - Method 1 & 2
                    cmb_mseed2sac_final_sf = proc_param.findChild(QComboBox, 'cmb_mseed2sac_final_sf').currentIndex()
                    proc['cmb_mseed2sac_final_sf'] = cmb_mseed2sac_final_sf
                elif pid == [3,1]: # Remove response - Method 1
                    le_mseed2sac_stametadir = proc_param.findChild(MyLineEdit, 'le_mseed2sac_stametadir').text()
                    cmb_mseed2sac_resp_output = proc_param.findChild(QComboBox, 'cmb_mseed2sac_resp_output').currentIndex()
                    cmb_mseed2sac_resp_prefilter = proc_param.findChild(QComboBox, 'cmb_mseed2sac_resp_prefilter').currentIndex()
                    proc['le_mseed2sac_stametadir'] = le_mseed2sac_stametadir
                    proc['cmb_mseed2sac_resp_output'] = cmb_mseed2sac_resp_output
                    proc['cmb_mseed2sac_resp_prefilter'] = cmb_mseed2sac_resp_prefilter
                elif pid == [4,1]: # bandpass filter - Method 1
                    le_mseed2sac_bp_cp1 = proc_param.findChild(QLineEdit, 'le_mseed2sac_bp_cp1').text()
                    le_mseed2sac_bp_cp2 = proc_param.findChild(QLineEdit, 'le_mseed2sac_bp_cp2').text()
                    sb_mseed2sac_bp_poles = proc_param.findChild(QSpinBox, 'sb_mseed2sac_bp_poles').value()
                    sb_mseed2sac_bp_passes = proc_param.findChild(QSpinBox, 'sb_mseed2sac_bp_passes').value()
                    proc['le_mseed2sac_bp_cp1'] = le_mseed2sac_bp_cp1
                    proc['le_mseed2sac_bp_cp2'] = le_mseed2sac_bp_cp2
                    proc['sb_mseed2sac_bp_poles'] = sb_mseed2sac_bp_poles
                    proc['sb_mseed2sac_bp_passes'] = sb_mseed2sac_bp_passes
                elif pid == [5,1]: # Cut seismogram - Method 1
                    le_mseed2sac_cut_begin = proc_param.findChild(MyLineEdit, 'le_mseed2sac_cut_begin').text()
                    le_mseed2sac_cut_end = proc_param.findChild(MyLineEdit, 'le_mseed2sac_cut_end').text()
                    proc['le_mseed2sac_cut_begin'] = le_mseed2sac_cut_begin
                    proc['le_mseed2sac_cut_end'] = le_mseed2sac_cut_end
                elif pid == [6,1]: # Detrend - Method 1
                    cmb_mseed2sac_detrend_method = proc_param.findChild(QComboBox, 'cmb_mseed2sac_detrend_method').currentIndex()
                    sb_mseed2sac_detrend_order = proc_param.findChild(QSpinBox, 'sb_mseed2sac_detrend_order').value()
                    le_mseed2sac_dspline = proc_param.findChild(MyLineEdit, 'le_mseed2sac_dspline').text()
                    proc["cmb_mseed2sac_detrend_method"] = cmb_mseed2sac_detrend_method
                    proc["sb_mseed2sac_detrend_order"] = sb_mseed2sac_detrend_order
                    proc["le_mseed2sac_dspline"] = le_mseed2sac_dspline
                elif pid == [7,1]: # Write headers - Method 1
                    le_mseed2sac_stametadir = proc_param.findChild(MyLineEdit, 'le_mseed2sac_stametadir').text()
                    proc['le_mseed2sac_stametadir'] = le_mseed2sac_stametadir
                elif pid == [8,1]: # Remove channel - Method 1
                    le_mseed2sac_similar_channels = proc_param.findChild(QLineEdit, 'le_mseed2sac_similar_channels').text()
                    le_mseed2sac_channels2keep = proc_param.findChild(QLineEdit, 'le_mseed2sac_channels2keep').text()
                    proc['le_mseed2sac_similar_channels'] = le_mseed2sac_similar_channels
                    proc['le_mseed2sac_channels2keep'] = le_mseed2sac_channels2keep
                mseed2sac['mseed2sac_procs'].append(proc)
        return mseed2sac
                    





class SAC2NCF(QWidget):
    def __init__(self):
        super().__init__()

        # buttons graphics files
        icon_add = os.path.join(images_dir,"add.svg")
        icon_add_hover = os.path.join(images_dir,"add_hover.svg")
        if sys.platform == "win32":
            icon_add = icon_add.replace('\\','/')
            icon_add_hover = icon_add_hover.replace('\\','/')
        icon_remove = os.path.join(images_dir,"remove.svg")
        icon_remove_hover = os.path.join(images_dir,"remove_hover.svg")
        if sys.platform == "win32":
            icon_remove = icon_remove.replace('\\','/')
            icon_remove_hover = icon_remove_hover.replace('\\','/')

        self.sac2ncf_proc_frames = []

        self.scroll = QScrollArea()
        self.scroll.setObjectName("scroll_sac2ncf")
        self.scroll.setFrameShape(QFrame.Box)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scroll_widget")
        self.lyo_sac2ncf_proc_frames = QVBoxLayout(self.scroll_widget)
        self.lyo_sac2ncf_proc_frames.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_widget)
        self.add_rem_btns_sac2ncf = QWidget()
        self.add_rem_btns_sac2ncf.setObjectName("add_rem_btns_sac2ncf")
        self.add_rem_btns_sac2ncf.setStyleSheet("QPushButton {min-width: 35px; max-width: 35px;\
                                                 min-height: 35px; max-height: 35px;\
                                                 margin-top: 0px; margin-bottom: 0px; }\
                                    QPushButton:pressed {border: 3px solid #EEE;}")

        # Add process button
        self.btn_sac2ncf_add = QPushButton()
        self.btn_sac2ncf_add.setCursor(Qt.PointingHandCursor)
        self.btn_sac2ncf_add.setObjectName("btn_sac2ncf_add")
        qss_code = '''
            #btn_sac2ncf_add {
                image: url(%s);
            }

            #btn_sac2ncf_add:hover {
                image: url(%s);
            }
        ''' %(icon_add, icon_add_hover)
        self.btn_sac2ncf_add.setStyleSheet(qss_code)
        # Remove process button
        self.btn_sac2ncf_remove = QPushButton()
        self.btn_sac2ncf_remove.setCursor(Qt.PointingHandCursor)
        self.btn_sac2ncf_remove.setObjectName("btn_sac2ncf_remove")
        qss_code = '''
            #btn_sac2ncf_remove {
                image: url(%s);
            }

            #btn_sac2ncf_remove:hover {
                image: url(%s);
            }
        ''' %(icon_remove, icon_remove_hover)
        self.btn_sac2ncf_remove.setStyleSheet(qss_code)

        self.lyo_buttons = QHBoxLayout()
        self.lyo_buttons.addWidget(self.btn_sac2ncf_remove)
        self.lyo_buttons.addWidget(self.btn_sac2ncf_add)
        self.lyo_buttons.setAlignment(Qt.AlignCenter)
        self.add_rem_btns_sac2ncf.setLayout(self.lyo_buttons)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.add_rem_btns_sac2ncf)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10,20,10,10)
        self.setLayout(self.layout)

        # button signals and slots
        self.btn_sac2ncf_add.clicked.connect(lambda: self.add_proc_frame(pid=[0,0], params={}))
        self.btn_sac2ncf_remove.clicked.connect(self.remove_proc_frame)


    def get_num_procs(self):
        return len(self.sac2ncf_proc_frames)


    def add_proc_frame(self, pid=[0,0], params={}):
        add = True
        if self.get_num_procs() > 0:
            last_proc_type = self.sac2ncf_proc_frames[-1].layout().itemAt(0).widget()
            last_proc_type_index = last_proc_type.layout().itemAt(1).widget().currentIndex()
            if last_proc_type_index == 10: # if cross-correlate is the last process 
                add = False
        if add:
            pframe_id = self.get_num_procs()
            new_proc_frame = self.new_proc_frame(pframe_id=pframe_id, pid=pid, params=params)
            self.sac2ncf_proc_frames.append(new_proc_frame)
            self.lyo_sac2ncf_proc_frames.addWidget(self.sac2ncf_proc_frames[-1])


    def remove_proc_frame(self):
        nprocs = self.get_num_procs()
        if nprocs:
            proc_frame_obj = self.lyo_sac2ncf_proc_frames.itemAt(nprocs - 1).widget()
            proc_frame_obj.deleteLater()
            self.sac2ncf_proc_frames.pop()


    def new_proc_frame(self, pframe_id, pid=[0,0], params={}):
        proc_frame = QFrame()
        proc_type = self.new_proc_type(pframe_id=pframe_id, ptype_index=pid[0])
        proc_method = self.new_proc_method(pid=pid)
        proc_param = self.new_proc_param(pframe_id=pframe_id, pid=pid, params=params)
        proc_frame.setObjectName("proc_frame")
        proc_type.setObjectName("proc_type")
        proc_method.setObjectName("proc_method")
        proc_param.setObjectName("proc_param")
        # setup main layout
        lyo_proc_frame = QGridLayout()
        lyo_proc_frame.addWidget(proc_type, 0, 0)
        lyo_proc_frame.addWidget(proc_method, 1, 0)
        lyo_proc_frame.addWidget(proc_param, 0, 1, 2, 1)
        lyo_proc_frame.setContentsMargins(5,5,15,5)
        lyo_proc_frame.setHorizontalSpacing(0)
        proc_frame.setLayout(lyo_proc_frame)
        # stylesheet
        proc_frame.setStyleSheet("#%s {max-height: 180px; min-height: 180px;border: 3px solid #DDD; border-radius: 15px; margin-bottom: 10px; margin-right: 10px;}" %("proc_frame"))
        proc_type.setStyleSheet("#%s {min-width:280px; max-width:280px;}" %("proc_type"))
        proc_method.setStyleSheet("#%s {min-width:280px; max-width:280px;}" %("proc_method"))
        proc_param.setStyleSheet("#%s {border-left: 2px solid #DDD;}" %("proc_param"))
        # Signals and Slots
        cmb_proc_type = proc_type.layout().itemAt(1).widget()
        cmb_proc_method = proc_method.layout().itemAt(1).widget()
        cmb_proc_type.currentIndexChanged.connect(lambda: self.replace_proc_frame(pframe_id))
        cmb_proc_method.currentIndexChanged.connect(lambda: self.replace_proc_frame(pframe_id))
        return proc_frame


    def replace_proc_frame(self, pframe_id):
        current_proc_frame = self.sac2ncf_proc_frames[pframe_id]
        proc_type = current_proc_frame.layout().itemAt(0).widget()
        proc_method = current_proc_frame.layout().itemAt(1).widget()
        proc_type_index = proc_type.layout().itemAt(1).widget().currentIndex()
        proc_method_index = proc_method.layout().itemAt(1).widget().currentIndex()
        more_than_one_method = [1] # proc_type_index which has more than 1 method available
        if proc_type_index not in more_than_one_method or proc_method_index in [0, -1]:
            proc_method_index = 1
        new_proc_frame = self.new_proc_frame(pframe_id, pid=[proc_type_index, proc_method_index])
        self.sac2ncf_proc_frames[pframe_id] = new_proc_frame
        self.lyo_sac2ncf_proc_frames.replaceWidget(current_proc_frame, new_proc_frame)
        current_proc_frame.deleteLater()


    def update_proc_param_ui(self, pframe_id):
        current_proc_frame = self.sac2ncf_proc_frames[pframe_id]
        proc_type = current_proc_frame.layout().itemAt(0).widget()
        proc_method = current_proc_frame.layout().itemAt(1).widget()
        proc_param = current_proc_frame.layout().itemAt(2).widget()
        proc_param_lyo = proc_param.layout()
        proc_type_index = proc_type.layout().itemAt(1).widget().currentIndex()
        proc_method_index = proc_method.layout().itemAt(1).widget().currentIndex()
        pid = [proc_type_index, proc_method_index]
        if pid == [5,1]: # MSEED to SAC - detrend
            lbl_sac2ncf_detrend_method = proc_param.findChild(QLabel, 'lbl_sac2ncf_detrend_method')
            cmb_sac2ncf_detrend_method = proc_param.findChild(QComboBox, 'cmb_sac2ncf_detrend_method')
            lbl_sac2ncf_detrend_order = proc_param.findChild(QLabel, 'lbl_sac2ncf_detrend_order')
            sb_sac2ncf_detrend_order = proc_param.findChild(QSpinBox, 'sb_sac2ncf_detrend_order')
            lbl_sac2ncf_dspline = proc_param.findChild(QLabel, 'lbl_sac2ncf_dspline')
            le_sac2ncf_dspline = proc_param.findChild(QLineEdit, 'le_sac2ncf_dspline')

            # Detrend Parameters
            if cmb_sac2ncf_detrend_method.currentIndex() in [2,3]:
                lbl_sac2ncf_detrend_order.setEnabled(True)
                sb_sac2ncf_detrend_order.setEnabled(True)
            else:
                lbl_sac2ncf_detrend_order.setEnabled(False)
                sb_sac2ncf_detrend_order.setEnabled(False)

            if cmb_sac2ncf_detrend_method.currentIndex() == 3:
                lbl_sac2ncf_dspline.setEnabled(True)
                le_sac2ncf_dspline.setEnabled(True)
            else:
                lbl_sac2ncf_dspline.setEnabled(False)
                le_sac2ncf_dspline.setEnabled(False)


    def new_proc_type(self, pframe_id, ptype_index=0):
        proc_type = QFrame()
        proc_type.setObjectName("proc_type")
        proc_type.setObjectName(f"proc_type")
        lbl_proc_type = QLabel(f"Process #{pframe_id + 1}:")
        lbl_proc_type.setObjectName("lbl_proc_type")
        lbl_proc_type.setStyleSheet("#%s {color: #999;}" %("lbl_proc_type"))
        cmb_proc_type = QComboBox()
        cmb_proc_type.setObjectName("cmb_proc_type")
        cmb_proc_type.setEditable(True)
        cmb_proc_type.lineEdit().setAlignment(Qt.AlignCenter)
        cmb_proc_type.addItem("---- Select ----")
        cmb_proc_type.addItem("  Decimate")
        cmb_proc_type.addItem("  Remove response")
        cmb_proc_type.addItem("  Bandpass filter")
        cmb_proc_type.addItem("  Cut seismogram")
        cmb_proc_type.addItem("  Detrend")
        cmb_proc_type.addItem("  Write headers")
        cmb_proc_type.addItem("  Remove channel")
        cmb_proc_type.addItem("  Temporal normalize")
        cmb_proc_type.addItem("  Spectral whitening")
        cmb_proc_type.addItem("  Cross-correlation")
        lyo_proc_type = QHBoxLayout()
        lyo_proc_type.addWidget(lbl_proc_type)
        lyo_proc_type.addWidget(cmb_proc_type)
        lyo_proc_type.setAlignment(Qt.AlignVCenter)
        lyo_proc_type.setAlignment(Qt.AlignRight)
        lyo_proc_type.setContentsMargins(20,0,20,0)
        proc_type.setLayout(lyo_proc_type)
        cmb_proc_type.setCurrentIndex(ptype_index)
        proc_type.setStyleSheet("#%s {min-width:250px; max-width:250px;}" %("proc_type"))
        return proc_type


    def new_proc_method(self, pid=[0,0]):
        proc_method = QFrame()
        proc_method.setObjectName("proc_method")
        cmb_proc_method = QComboBox()
        cmb_proc_method.setObjectName("cmb_proc_method")
        cmb_proc_method.addItem("---- Select ----")
        lyo_proc_method = QHBoxLayout()
        ptype_index = pid[0]
        pmethod_index = pid[1]
        if ptype_index == 1: # decimate
            lbl_decimate_method = QLabel("Method:")
            lbl_decimate_method.setObjectName(f"lbl_decimate_method")
            lbl_decimate_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_decimate_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: decimate") # Method 1
            cmb_proc_method.addItem("ObsPy: resample") # Method 2
            lyo_proc_method.addWidget(lbl_decimate_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 2: # remove response
            lbl_remresp_method = QLabel("Method:")
            lbl_remresp_method.setObjectName(f"lbl_remresp_method")
            lbl_remresp_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_remresp_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("ObsPy: remove_response") # Method 1
            lyo_proc_method.addWidget(lbl_remresp_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 3: # bandpass filter
            lbl_bandpass_method = QLabel("Method:")
            lbl_bandpass_method.setObjectName(f"lbl_bandpass_method")
            lbl_bandpass_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_bandpass_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: bp") # Method 1
            lyo_proc_method.addWidget(lbl_bandpass_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 4: # cut seismogram
            lbl_cut_method = QLabel("Method:")
            lbl_cut_method.setObjectName(f"lbl_cut_method")
            lbl_cut_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_cut_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: cuterr fillz") # Method 1
            lyo_proc_method.addWidget(lbl_cut_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 5: # Detrend
            lbl_detrend_method = QLabel("Method:")
            lbl_detrend_method.setObjectName(f"lbl_detrend_method")
            lbl_detrend_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_detrend_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("Obspy: detrend") # Method 1
            lyo_proc_method.addWidget(lbl_detrend_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 6: # chnhdr
            lbl_chnhdr_method = QLabel("Method:")
            lbl_chnhdr_method.setObjectName(f"lbl_chnhdr_method")
            lbl_chnhdr_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_chnhdr_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: chnhdr") # Method 1
            lyo_proc_method.addWidget(lbl_chnhdr_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 7: # remove channel
            lbl_remchn_method = QLabel("Method:")
            lbl_remchn_method.setObjectName(f"lbl_remchn_method")
            lbl_remchn_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_remchn_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("Python script") # Method 1
            lyo_proc_method.addWidget(lbl_remchn_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 8: # temporal normalization
            lbl_tempnorm_method = QLabel("Method:")
            lbl_tempnorm_method.setObjectName("lbl_tempnorm_method")
            lbl_tempnorm_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_tempnorm_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("One-bit normalization") # Method 1
            lyo_proc_method.addWidget(lbl_tempnorm_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 9: # spectral whitening
            lbl_whiten_method = QLabel("Method:")
            lbl_whiten_method.setObjectName("lbl_whiten_method")
            lbl_whiten_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_whiten_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: whiten") # Method 1
            lyo_proc_method.addWidget(lbl_whiten_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        elif ptype_index == 10: # cross correlation
            lbl_xcorr_method = QLabel("Method:")
            lbl_xcorr_method.setObjectName("lbl_xcorr_method")
            lbl_xcorr_method.setStyleSheet("#%s {color:#999;}" %(f"lbl_xcorr_method"))
            cmb_proc_method.setEditable(True)
            cmb_proc_method.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_proc_method.addItem("SAC: correlate") # Method 1
            lyo_proc_method.addWidget(lbl_xcorr_method)
            lyo_proc_method.addWidget(cmb_proc_method)
        else:
            lbl_bandpass_method = QLabel("Method:")
            lbl_bandpass_method.setVisible(False)
            cmb_proc_method.setVisible(False)
            lyo_proc_method.addWidget(lbl_bandpass_method)
            lyo_proc_method.addWidget(cmb_proc_method)

        lyo_proc_method.setAlignment(Qt.AlignVCenter)
        lyo_proc_method.setAlignment(Qt.AlignRight)
        lyo_proc_method.setContentsMargins(20,0,20,0)
        proc_method.setLayout(lyo_proc_method)
        proc_method.setStyleSheet("#%s {min-width:250px; max-width:250px;}" %("proc_method"))
        cmb_proc_method.setCurrentIndex(pmethod_index)
        return proc_method


    def new_proc_param(self, pframe_id, pid=[0,0], params={}):
        proc_param = QWidget()
        proc_param.setObjectName(f"proc_param")
        lyo_proc_param = QGridLayout()
        if len(params) == 0:
            params = self.default_proc_params(pid)
        if pid == [1,1] or pid == [1,2]: # Decimate - Method 1 & 2
            lbl_sac2ncf_finalSF = QLabel("Final sampling frequency:")
            cmb_sac2ncf_final_sf = QComboBox()
            cmb_sac2ncf_final_sf.addItem("1 Hz")
            cmb_sac2ncf_final_sf.addItem("2 Hz")
            cmb_sac2ncf_final_sf.addItem("5 Hz")
            cmb_sac2ncf_final_sf.addItem("10 Hz")
            cmb_sac2ncf_final_sf.addItem("20 Hz")
            cmb_sac2ncf_final_sf.setObjectName('cmb_sac2ncf_final_sf')
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_finalSF,0,0)
            lyo_proc_param.addWidget(cmb_sac2ncf_final_sf,0,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            cmb_sac2ncf_final_sf.setCurrentIndex(params['cmb_sac2ncf_final_sf'])
        elif pid == [2,1]: # Remove response - Method 1
            lbl_sac2ncf_stametadir = QLabel("Station metadata dir:")
            le_sac2ncf_stametadir = MyLineEdit()
            le_sac2ncf_stametadir.setObjectName("le_sac2ncf_stametadir")
            le_sac2ncf_stametadir.setPlaceholderText("Full path to station metadata directory")
            le_sac2ncf_stametadir.isdir()
            le_sac2ncf_stametadir.textChanged.connect(le_sac2ncf_stametadir.isdir)
            browse_sac2ncf_stametadir = MyDialog(type=3, lineEditObj=le_sac2ncf_stametadir)
            lbl_sac2ncf_resp_output = QLabel("Output unit:")
            cmb_sac2ncf_resp_output = QComboBox()
            cmb_sac2ncf_resp_output.setObjectName('cmb_sac2ncf_resp_output')
            cmb_sac2ncf_resp_output.setEditable(True)
            cmb_sac2ncf_resp_output.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_sac2ncf_resp_output.addItem("Displacement (m)")
            cmb_sac2ncf_resp_output.addItem("Velocity (m/s)")
            cmb_sac2ncf_resp_output.addItem("Acceleration (m/s**2)")
            lbl_sac2ncf_resp_prefilter = QLabel("Deconvolution pre-filter:")
            cmb_sac2ncf_resp_prefilter = QComboBox()
            cmb_sac2ncf_resp_prefilter.setObjectName('cmb_sac2ncf_resp_prefilter')
            cmb_sac2ncf_resp_prefilter.setEditable(True)
            cmb_sac2ncf_resp_prefilter.lineEdit().setAlignment(Qt.AlignCenter)
            cmb_sac2ncf_resp_prefilter.addItem("None")
            cmb_sac2ncf_resp_prefilter.addItem("[0.001, 0.005, 45, 50]")
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_stametadir, 0,0)
            lyo_proc_param.addWidget(le_sac2ncf_stametadir, 0,1)
            lyo_proc_param.addWidget(browse_sac2ncf_stametadir, 0,2)
            lyo_proc_param.addWidget(lbl_sac2ncf_resp_output, 1,0)
            lyo_proc_param.addWidget(cmb_sac2ncf_resp_output, 1,1)
            lyo_proc_param.addWidget(lbl_sac2ncf_resp_prefilter, 2,0)
            lyo_proc_param.addWidget(cmb_sac2ncf_resp_prefilter, 2,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_sac2ncf_stametadir.setText(f"{params['le_sac2ncf_stametadir']}")
            cmb_sac2ncf_resp_output.setCurrentIndex(params['cmb_sac2ncf_resp_output'])
            cmb_sac2ncf_resp_prefilter.setCurrentIndex(params['cmb_sac2ncf_resp_prefilter'])
        elif pid == [3,1]: # bandpass filter - Method 1
            lbl_sac2ncf_bp_cp1 = QLabel("Left corner period (s):")
            le_sac2ncf_bp_cp1 = MyLineEdit()
            le_sac2ncf_bp_cp1.setObjectName('le_sac2ncf_bp_cp1')
            le_sac2ncf_bp_cp1.setAlignment(Qt.AlignCenter)
            le_sac2ncf_bp_cp1.setPlaceholderText("Bandpass left corner period (s)")
            le_sac2ncf_bp_cp1.textChanged.connect(le_sac2ncf_bp_cp1.isfloat)
            lbl_sac2ncf_bp_cp2 = QLabel("Right corner period (s):")
            le_sac2ncf_bp_cp2 = MyLineEdit()
            le_sac2ncf_bp_cp2.setObjectName('le_sac2ncf_bp_cp2')
            le_sac2ncf_bp_cp2.setAlignment(Qt.AlignCenter)
            le_sac2ncf_bp_cp2.setPlaceholderText("Bandpass right corner period (s)")
            le_sac2ncf_bp_cp2.textChanged.connect(le_sac2ncf_bp_cp2.isfloat)
            lbl_sac2ncf_bp_poles = QLabel("Number of poles (n):")
            sb_sac2ncf_bp_poles = QSpinBox()
            sb_sac2ncf_bp_poles.setObjectName('sb_sac2ncf_bp_poles')
            sb_sac2ncf_bp_poles.setMinimum(1)
            sb_sac2ncf_bp_poles.setMaximum(10)
            sb_sac2ncf_bp_poles.setSingleStep(1)
            lbl_sac2ncf_bp_passes = QLabel("Number of passes (p):")
            sb_sac2ncf_bp_passes = QSpinBox()
            sb_sac2ncf_bp_passes.setObjectName('sb_sac2ncf_bp_passes')
            sb_sac2ncf_bp_passes.setMinimum(1)
            sb_sac2ncf_bp_passes.setMaximum(2)
            sb_sac2ncf_bp_passes.setSingleStep(1)
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_bp_cp1, 0,0)
            lyo_proc_param.addWidget(le_sac2ncf_bp_cp1, 0,1)
            lyo_proc_param.addWidget(lbl_sac2ncf_bp_cp2, 1,0)
            lyo_proc_param.addWidget(le_sac2ncf_bp_cp2, 1,1)
            lyo_proc_param.addWidget(lbl_sac2ncf_bp_poles, 0,2)
            lyo_proc_param.addWidget(sb_sac2ncf_bp_poles, 0,3)
            lyo_proc_param.addWidget(lbl_sac2ncf_bp_passes, 1,2)
            lyo_proc_param.addWidget(sb_sac2ncf_bp_passes, 1,3)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setVerticalSpacing(15)
            lyo_proc_param.setContentsMargins(50,0,50,0)
            # set parameters
            le_sac2ncf_bp_cp1.setText(f"{params['le_sac2ncf_bp_cp1']}")
            le_sac2ncf_bp_cp2.setText(f"{params['le_sac2ncf_bp_cp2']}")
            sb_sac2ncf_bp_poles.setValue(params['sb_sac2ncf_bp_poles'])
            sb_sac2ncf_bp_passes.setValue(params['sb_sac2ncf_bp_passes'])
        elif pid == [4,1]: # Cut seismogram - Method 1
            lbl_sac2ncf_cut_begin = QLabel("Cut begin (s):")
            le_sac2ncf_cut_begin = MyLineEdit()
            le_sac2ncf_cut_begin.setObjectName("le_sac2ncf_cut_begin")
            lbl_sac2ncf_cut_end = QLabel("Cut end (s):")
            le_sac2ncf_cut_end = MyLineEdit()
            le_sac2ncf_cut_end.setObjectName("le_sac2ncf_cut_end")
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_cut_begin, 0,0)
            lyo_proc_param.addWidget(le_sac2ncf_cut_begin, 0,1)
            lyo_proc_param.addWidget(lbl_sac2ncf_cut_end, 1,0)
            lyo_proc_param.addWidget(le_sac2ncf_cut_end, 1,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_sac2ncf_cut_begin.setText(f"{params['le_sac2ncf_cut_begin']}")
            le_sac2ncf_cut_end.setText(f"{params['le_sac2ncf_cut_end']}")
        elif pid == [5,1]: # Detrend - Method 1
            lbl_sac2ncf_detrend_method = QLabel("Detrend method:")
            lbl_sac2ncf_detrend_method.setObjectName("lbl_sac2ncf_detrend_method")
            cmb_sac2ncf_detrend_method = QComboBox()
            cmb_sac2ncf_detrend_method.setObjectName("cmb_sac2ncf_detrend_method")
            cmb_sac2ncf_detrend_method.addItem("Demean")
            cmb_sac2ncf_detrend_method.addItem("Linear")
            cmb_sac2ncf_detrend_method.addItem("Polynomial")
            cmb_sac2ncf_detrend_method.addItem("Spline")
            lbl_sac2ncf_detrend_order = QLabel("Detrend order:")
            lbl_sac2ncf_detrend_order.setObjectName("lbl_sac2ncf_detrend_order")
            sb_sac2ncf_detrend_order = QSpinBox()
            sb_sac2ncf_detrend_order.setObjectName("sb_sac2ncf_detrend_order")
            sb_sac2ncf_detrend_order.setMinimum(3)
            sb_sac2ncf_detrend_order.setMaximum(5)
            sb_sac2ncf_detrend_order.setSingleStep(1)
            lbl_sac2ncf_dspline = QLabel("dspline:")
            lbl_sac2ncf_dspline.setObjectName("lbl_sac2ncf_dspline")
            le_sac2ncf_dspline = MyLineEdit()
            le_sac2ncf_dspline.setObjectName("le_sac2ncf_dspline")
            le_sac2ncf_dspline.setPlaceholderText("Number of samples between nodes (spline method)")
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_detrend_method, 1,0,1,2)
            lyo_proc_param.addWidget(cmb_sac2ncf_detrend_method, 1,2)
            lyo_proc_param.addWidget(lbl_sac2ncf_detrend_order, 2,0,1,2)
            lyo_proc_param.addWidget(sb_sac2ncf_detrend_order, 2,2)
            lyo_proc_param.addWidget(lbl_sac2ncf_dspline, 3,0,1,2)
            lyo_proc_param.addWidget(le_sac2ncf_dspline, 3,2)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(85,0,75,0)
            # set UI parameters
            cmb_sac2ncf_detrend_method.setCurrentIndex(params["cmb_sac2ncf_detrend_method"])
            sb_sac2ncf_detrend_order.setValue(params["sb_sac2ncf_detrend_order"])
            le_sac2ncf_dspline.setText(f"{params['le_sac2ncf_dspline']}")
            # signals ans slots
            cmb_sac2ncf_detrend_method.currentIndexChanged.connect(lambda: self.update_proc_param_ui(pframe_id))
            le_sac2ncf_dspline.textChanged.connect(le_sac2ncf_dspline.isfloat)

            # update UI
            if cmb_sac2ncf_detrend_method.currentIndex() in [2,3]:
                lbl_sac2ncf_detrend_order.setEnabled(True)
                sb_sac2ncf_detrend_order.setEnabled(True)
            else:
                lbl_sac2ncf_detrend_order.setEnabled(False)
                sb_sac2ncf_detrend_order.setEnabled(False)
                
            if cmb_sac2ncf_detrend_method.currentIndex() == 3:
                lbl_sac2ncf_dspline.setEnabled(True)
                le_sac2ncf_dspline.setEnabled(True)
            else:
                lbl_sac2ncf_dspline.setEnabled(False)
                le_sac2ncf_dspline.setEnabled(False)
        elif pid == [6,1]: # Write headers - Method 1
            lbl_sac2ncf_stametadir = QLabel("Station metadata dir:")
            le_sac2ncf_stametadir = MyLineEdit()
            le_sac2ncf_stametadir.setObjectName("le_sac2ncf_stametadir")
            le_sac2ncf_stametadir.setPlaceholderText("Full path to station metadata directory")
            le_sac2ncf_stametadir.isdir()
            le_sac2ncf_stametadir.textChanged.connect(le_sac2ncf_stametadir.isdir)
            browse_sac2ncf_stametadir = MyDialog(type=3, lineEditObj=le_sac2ncf_stametadir)
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_stametadir, 0,0)
            lyo_proc_param.addWidget(le_sac2ncf_stametadir, 0,1)
            lyo_proc_param.addWidget(browse_sac2ncf_stametadir, 0,2)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_sac2ncf_stametadir.setText(f"{params['le_sac2ncf_stametadir']}")
        elif pid == [7,1]: # Remove channel - Method 1
            lbl_sac2ncf_similar_channels = QLabel("If all these channels were available:")
            le_sac2ncf_similar_channels = QLineEdit()
            le_sac2ncf_similar_channels.setObjectName("le_sac2ncf_similar_channels")
            lbl_sac2ncf_channels2keep = QLabel("Only keep these channels:")
            le_sac2ncf_channels2keep = QLineEdit()
            le_sac2ncf_channels2keep.setObjectName("le_sac2ncf_channels2keep")
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_similar_channels, 0,0)
            lyo_proc_param.addWidget(le_sac2ncf_similar_channels, 0,1)
            lyo_proc_param.addWidget(lbl_sac2ncf_channels2keep, 1,0)
            lyo_proc_param.addWidget(le_sac2ncf_channels2keep, 1,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            le_sac2ncf_similar_channels.setText(f"{params['le_sac2ncf_similar_channels']}")
            le_sac2ncf_channels2keep.setText(f"{params['le_sac2ncf_channels2keep']}")
        elif pid == [9,1]: # Spectral whitening - Method 1: SAC: whiten
            lbl_sac2ncf_whiten_order = QLabel("Whitening order:")
            sb_sac2ncf_whiten_order = QSpinBox()
            sb_sac2ncf_whiten_order.setObjectName('sb_sac2ncf_whiten_order')
            sb_sac2ncf_whiten_order.setMinimum(1)
            sb_sac2ncf_whiten_order.setMaximum(9999)
            sb_sac2ncf_whiten_order.setSingleStep(1)
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_whiten_order, 0,0)
            lyo_proc_param.addWidget(sb_sac2ncf_whiten_order, 0,1)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)
            # set parameters
            sb_sac2ncf_whiten_order.setValue(params['sb_sac2ncf_whiten_order'])
        elif pid == [8,1] or pid == [10,1]: # Temporal normalization - Method 1 OR Cross-correlate - Method 1
            lbl_sac2ncf_nothing_adjustable = QLabel("No parameter needs to be adjusted for this process")
            lbl_sac2ncf_nothing_adjustable.setObjectName("lbl_sac2ncf_nothing_adjustable")
            lbl_sac2ncf_nothing_adjustable.setStyleSheet("#lbl_sac2ncf_nothing_adjustable{ color: gray;}")
            lbl_sac2ncf_last_process = QLabel("Note: This must be the last listed process for ncf2sac")
            lbl_sac2ncf_last_process.setObjectName("lbl_sac2ncf_last_process")
            lbl_sac2ncf_last_process.setStyleSheet("#lbl_sac2ncf_last_process{ color: gray;}")
            # setup layout
            lyo_proc_param.addWidget(lbl_sac2ncf_nothing_adjustable, 0,0)
            if pid == [10,1]:
                lyo_proc_param.addWidget(lbl_sac2ncf_last_process, 1,0)
            lyo_proc_param.setAlignment(Qt.AlignVCenter)
            lyo_proc_param.setAlignment(Qt.AlignHCenter)
            lyo_proc_param.setContentsMargins(65,0,55,0)

        # remove next process frames if process type "cross-correlation" is selected
        if pid == [10,1]:
            num_procs = self.get_num_procs()
            for  i in range(pframe_id, num_procs-1):
                self.remove_proc_frame()


        proc_param.setLayout(lyo_proc_param)
        proc_param.setStyleSheet("#%s {border-left: 2px solid #DDD;}" %("proc_param"))
        return proc_param


    def default_proc_params(self, pid):
        sac2ncf_proc_params = {"pid": [0,0]}
        if pid == [1,1]: # Decimate - Method 1
            sac2ncf_proc_params["pid"] = [1,1]
            sac2ncf_proc_params["cmb_sac2ncf_final_sf"] = 0
        elif pid == [1,2]: # Decimate - Method 2
            sac2ncf_proc_params["pid"] = [1,2]
            sac2ncf_proc_params["cmb_sac2ncf_final_sf"] = 0
        elif pid == [2,1]: # Remove response - Method 1
            sac2ncf_proc_params["pid"] = [2,1]
            sac2ncf_proc_params["le_sac2ncf_stametadir"] = os.path.abspath("./metadata")
            sac2ncf_proc_params["cmb_sac2ncf_resp_output"] = 1
            sac2ncf_proc_params["cmb_sac2ncf_resp_prefilter"] = 1
        elif pid == [3,1]: # Bandpass filter - Method 1
            sac2ncf_proc_params["pid"] = [3,1]
            sac2ncf_proc_params["le_sac2ncf_bp_cp1"] = "4"
            sac2ncf_proc_params["le_sac2ncf_bp_cp2"] = "500"
            sac2ncf_proc_params["sb_sac2ncf_bp_poles"] = 3
            sac2ncf_proc_params["sb_sac2ncf_bp_passes"] = 2
        elif pid == [4,1]: # Cut seismogram - Method 1
            sac2ncf_proc_params["pid"] = [4,1]
            sac2ncf_proc_params["le_sac2ncf_cut_begin"] = ""
            sac2ncf_proc_params["le_sac2ncf_cut_end"] = ""
        elif pid == [5,1]: # Detrend - Method 1
            sac2ncf_proc_params["cmb_sac2ncf_detrend_method"] = 3
            sac2ncf_proc_params["sb_sac2ncf_detrend_order"] = 4
            sac2ncf_proc_params["le_sac2ncf_dspline"] = 864000
        elif pid == [6,1]: # Write headers - Method 1
            sac2ncf_proc_params["le_sac2ncf_stametadir"] = os.path.abspath("./metadata")
        elif pid == [7,1]: # Remove extra channel - Method 1
            sac2ncf_proc_params["pid"] = [7,1]
            sac2ncf_proc_params["le_sac2ncf_similar_channels"] = "BHZ HHZ"
            sac2ncf_proc_params["le_sac2ncf_channels2keep"] = "BHZ"
        elif pid == [8,1]: # Temporal normalize - Method 1: one-bit
            sac2ncf_proc_params["pid"] = [8,1]
        elif pid == [9,1]: # Spectral whitening - Method 1
            sac2ncf_proc_params["pid"] = [9,1]
            sac2ncf_proc_params['sb_sac2ncf_whiten_order'] = 6
        elif pid == [10,1]: # Cross-correlation - Method 1: sac correlate
            sac2ncf_proc_params["pid"] = [10,1]
        return sac2ncf_proc_params


    def get_parameters(self):
        sac2ncf = {}
        sac2ncf['sac2ncf_procs'] = []
        nprocs = self.get_num_procs()
        for i in range(nprocs):
            proc_frame = self.sac2ncf_proc_frames[i]
            proc_type = proc_frame.layout().itemAt(0).widget()
            proc_method = proc_frame.layout().itemAt(1).widget()
            proc_param = proc_frame.layout().itemAt(2).widget()
            proc_type_index = proc_type.layout().itemAt(1).widget().currentIndex()
            proc_method_index = proc_method.layout().itemAt(1).widget().currentIndex()
            if proc_type_index > 0 and proc_method_index > 0:
                proc = {}
                pid = [proc_type_index, proc_method_index]
                proc['pid'] = pid
                if pid == [1,1] or pid == [1,2]: # Decimate - Method 1 & 2
                    cmb_sac2ncf_final_sf = proc_param.findChild(QComboBox, 'cmb_sac2ncf_final_sf').currentIndex()
                    proc['cmb_sac2ncf_final_sf'] = cmb_sac2ncf_final_sf
                elif pid == [2,1]: # Remove response - Method 1
                    le_sac2ncf_stametadir = proc_param.findChild(MyLineEdit, 'le_sac2ncf_stametadir').text()
                    cmb_sac2ncf_resp_output = proc_param.findChild(QComboBox, 'cmb_sac2ncf_resp_output').currentIndex()
                    cmb_sac2ncf_resp_prefilter = proc_param.findChild(QComboBox, 'cmb_sac2ncf_resp_prefilter').currentIndex()
                    proc['le_sac2ncf_stametadir'] = le_sac2ncf_stametadir
                    proc['cmb_sac2ncf_resp_output'] = cmb_sac2ncf_resp_output
                    proc['cmb_sac2ncf_resp_prefilter'] = cmb_sac2ncf_resp_prefilter
                elif pid == [3,1]: # bandpass filter - Method 1
                    le_sac2ncf_bp_cp1 = proc_param.findChild(QLineEdit, 'le_sac2ncf_bp_cp1').text()
                    le_sac2ncf_bp_cp2 = proc_param.findChild(QLineEdit, 'le_sac2ncf_bp_cp2').text()
                    sb_sac2ncf_bp_poles = proc_param.findChild(QSpinBox, 'sb_sac2ncf_bp_poles').value()
                    sb_sac2ncf_bp_passes = proc_param.findChild(QSpinBox, 'sb_sac2ncf_bp_passes').value()
                    proc['le_sac2ncf_bp_cp1'] = le_sac2ncf_bp_cp1
                    proc['le_sac2ncf_bp_cp2'] = le_sac2ncf_bp_cp2
                    proc['sb_sac2ncf_bp_poles'] = sb_sac2ncf_bp_poles
                    proc['sb_sac2ncf_bp_passes'] = sb_sac2ncf_bp_passes
                elif pid == [4,1]: # Cut seismogram - Method 1
                    le_sac2ncf_cut_begin = proc_param.findChild(MyLineEdit, 'le_sac2ncf_cut_begin').text()
                    le_sac2ncf_cut_end = proc_param.findChild(MyLineEdit, 'le_sac2ncf_cut_end').text()
                    proc['le_sac2ncf_cut_begin'] = le_sac2ncf_cut_begin
                    proc['le_sac2ncf_cut_end'] = le_sac2ncf_cut_end
                elif pid == [5,1]: # Detrend - Method 1
                    cmb_sac2ncf_detrend_method = proc_param.findChild(QComboBox, 'cmb_sac2ncf_detrend_method').currentIndex()
                    sb_sac2ncf_detrend_order = proc_param.findChild(QSpinBox, 'sb_sac2ncf_detrend_order').value()
                    le_sac2ncf_dspline = proc_param.findChild(MyLineEdit, 'le_sac2ncf_dspline').text()
                    proc["cmb_sac2ncf_detrend_method"] = cmb_sac2ncf_detrend_method
                    proc["sb_sac2ncf_detrend_order"] = sb_sac2ncf_detrend_order
                    proc["le_sac2ncf_dspline"] = le_sac2ncf_dspline
                elif pid == [6,1]: # Write headers - Method 1
                    le_sac2ncf_stametadir = proc_param.findChild(MyLineEdit, 'le_sac2ncf_stametadir').text()
                    proc['le_sac2ncf_stametadir'] = le_sac2ncf_stametadir
                elif pid == [7,1]: # Remove channel - Method 1
                    le_sac2ncf_similar_channels = proc_param.findChild(QLineEdit, 'le_sac2ncf_similar_channels').text()
                    le_sac2ncf_channels2keep = proc_param.findChild(QLineEdit, 'le_sac2ncf_channels2keep').text()
                    proc['le_sac2ncf_similar_channels'] = le_sac2ncf_similar_channels
                    proc['le_sac2ncf_channels2keep'] = le_sac2ncf_channels2keep
                elif pid == [9,1]: # Spectral whitening
                    sb_sac2ncf_whiten_order = proc_param.findChild(QSpinBox, 'sb_sac2ncf_whiten_order').value()
                    proc['sb_sac2ncf_whiten_order'] = sb_sac2ncf_whiten_order
                sac2ncf['sac2ncf_procs'].append(proc)
        return sac2ncf






class NCF2EGF(QWidget):
    def __init__(self):
        super().__init__()

        lbl_empty = QLabel()

        self.chb_ncf2egf_symmetrize = MyCheckBox()
        lbl_ncf2egf_symmetrize = QLabel("Symmetrize EGFs")
        # layout symmetrize
        lyo_sym = QGridLayout()
        lyo_sym.addWidget(self.chb_ncf2egf_symmetrize, 0,0,1,1)
        lyo_sym.addWidget(lbl_ncf2egf_symmetrize, 0,1,1,2)
        lyo_sym.addWidget(lbl_empty, 1,0,1,3)
        lyo_sym.addWidget(lbl_empty, 2,0,1,3)
        lyo_sym.setVerticalSpacing(15)
        lyo_sym.setHorizontalSpacing(15)

        
        self.chb_ncf2egf_cut = MyCheckBox()
        lbl_ncf2egf_cut = QLabel("Cut EGFs")
        lbl_ncf2egf_cut_begin = QLabel("Cut begin (s):")
        lbl_ncf2egf_cut_end = QLabel("Cut end (s):")
        self.le_ncf2egf_cut_begin = MyLineEdit()
        self.le_ncf2egf_cut_end = MyLineEdit()
        self.le_ncf2egf_cut_begin.setObjectName("le_ncf2egf_cut_begin")
        self.le_ncf2egf_cut_end.setObjectName("le_ncf2egf_cut_end")
        self.le_ncf2egf_cut_begin.setStyleSheet("#le_ncf2egf_cut_begin {max-width: 200px;}")
        self.le_ncf2egf_cut_end.setStyleSheet("#le_ncf2egf_cut_end {max-width: 200px;}")
        self.le_ncf2egf_cut_begin.setAlignment(Qt.AlignCenter)
        self.le_ncf2egf_cut_end.setAlignment(Qt.AlignCenter)
        # layout cut
        lyo_cut = QGridLayout()
        lyo_cut.addWidget(self.chb_ncf2egf_cut, 0,0,1,1)
        lyo_cut.addWidget(lbl_ncf2egf_cut, 0,1,1,1)
        lyo_cut.addWidget(lbl_ncf2egf_cut_begin, 1,1,1,1)
        lyo_cut.addWidget(lbl_ncf2egf_cut_end, 2,1,1,1)
        lyo_cut.addWidget(self.le_ncf2egf_cut_begin, 1,2,1,1)
        lyo_cut.addWidget(self.le_ncf2egf_cut_end, 2,2,1,1)
        lyo_cut.addWidget(lbl_empty, 1,3)
        lyo_cut.addWidget(lbl_empty, 1,3)
        lyo_cut.setAlignment(Qt.AlignVCenter)
        lyo_cut.setVerticalSpacing(15)
        lyo_cut.setHorizontalSpacing(15)


        self.chb_ncf2egf_bp = MyCheckBox()
        lbl_ncf2egf_bp = QLabel("Apply bandpass filter to EGFs")
        lbl_ncf2egf_bp_cp1 = QLabel("Left corner period (s):")
        self.le_ncf2egf_bp_cp1 = MyLineEdit()
        self.le_ncf2egf_bp_cp1.setObjectName('le_ncf2egf_bp_cp1')
        self.le_ncf2egf_bp_cp1.setAlignment(Qt.AlignCenter)
        self.le_ncf2egf_bp_cp1.setPlaceholderText("Bandpass left corner period (s)")
        self.le_ncf2egf_bp_cp1.textChanged.connect(self.le_ncf2egf_bp_cp1.isfloat)
        lbl_ncf2egf_bp_cp2 = QLabel("Right corner period (s):")
        self.le_ncf2egf_bp_cp2 = MyLineEdit()
        self.le_ncf2egf_bp_cp2.setObjectName('le_ncf2egf_bp_cp2')
        self.le_ncf2egf_bp_cp2.setAlignment(Qt.AlignCenter)
        self.le_ncf2egf_bp_cp2.setPlaceholderText("Bandpass right corner period (s)")
        self.le_ncf2egf_bp_cp2.textChanged.connect(self.le_ncf2egf_bp_cp2.isfloat)
        lbl_ncf2egf_bp_poles = QLabel("Number of poles (n):")
        self.sb_ncf2egf_bp_poles = QSpinBox()
        self.sb_ncf2egf_bp_poles.setObjectName('sb_ncf2egf_bp_poles')
        self.sb_ncf2egf_bp_poles.setMinimum(1)
        self.sb_ncf2egf_bp_poles.setMaximum(10)
        self.sb_ncf2egf_bp_poles.setSingleStep(1)
        lbl_ncf2egf_bp_passes = QLabel("Number of passes (p):")
        self.sb_ncf2egf_bp_passes = QSpinBox()
        self.sb_ncf2egf_bp_passes.setObjectName('sb_ncf2egf_bp_passes')
        self.sb_ncf2egf_bp_passes.setMinimum(1)
        self.sb_ncf2egf_bp_passes.setMaximum(2)
        self.sb_ncf2egf_bp_passes.setSingleStep(1)
        # layout bandpass
        lyo_bp = QGridLayout()
        lyo_bp.addWidget(self.chb_ncf2egf_bp, 0,0,1,1)
        lyo_bp.addWidget(lbl_ncf2egf_bp, 0,1,1,1)
        lyo_bp.addWidget(lbl_ncf2egf_bp_cp1, 1,1,1,1)
        lyo_bp.addWidget(self.le_ncf2egf_bp_cp1, 1,2,1,1)
        lyo_bp.addWidget(lbl_ncf2egf_bp_cp2, 2,1,1,1)
        lyo_bp.addWidget(self.le_ncf2egf_bp_cp2, 2,2,1,1)
        lyo_bp.addWidget(lbl_ncf2egf_bp_poles, 1,3,1,1)
        lyo_bp.addWidget(self.sb_ncf2egf_bp_poles, 1,4,1,1)
        lyo_bp.addWidget(lbl_ncf2egf_bp_passes, 2,3,1,1)
        lyo_bp.addWidget(self.sb_ncf2egf_bp_passes, 2,4,1,1)
        lyo_bp.setAlignment(Qt.AlignVCenter)
        lyo_bp.setAlignment(Qt.AlignHCenter)
        lyo_bp.setVerticalSpacing(15)
        lyo_bp.setHorizontalSpacing(15)


        # put together all layouts 
        layout = QGridLayout()
        layout.addLayout(lyo_sym, 0,0,1,3)
        layout.addLayout(lyo_cut, 1,0,1,2)
        layout.addLayout(lyo_bp, 1,2,1,1)
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(50)
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(30,0,30,0)
        self.setLayout(layout)

        # update ui
        self.chb_ncf2egf_cut.stateChanged.connect(self.update_ncf2egf_ui)
        self.chb_ncf2egf_bp.stateChanged.connect(self.update_ncf2egf_ui)
        self.update_ncf2egf_ui()



    def update_ncf2egf_ui(self):

        if self.chb_ncf2egf_cut.isChecked():
            self.le_ncf2egf_cut_begin.setEnabled(True)
            self.le_ncf2egf_cut_end.setEnabled(True)
            self.le_ncf2egf_cut_begin.setStyleSheet('#le_ncf2egf_cut_begin{color: #000;}')
            self.le_ncf2egf_cut_end.setStyleSheet('#le_ncf2egf_cut_end{color: #000;}')
        else:
            self.le_ncf2egf_cut_begin.setEnabled(False)
            self.le_ncf2egf_cut_end.setEnabled(False)
            self.le_ncf2egf_cut_begin.setStyleSheet('#le_ncf2egf_cut_begin{color: #aaa;}')
            self.le_ncf2egf_cut_end.setStyleSheet('#le_ncf2egf_cut_end{color: #aaa;}')

        if self.chb_ncf2egf_bp.isChecked():
            self.le_ncf2egf_bp_cp1.setEnabled(True)
            self.le_ncf2egf_bp_cp2.setEnabled(True)
            self.sb_ncf2egf_bp_poles.setEnabled(True)
            self.sb_ncf2egf_bp_passes.setEnabled(True)
            self.le_ncf2egf_bp_cp1.setStyleSheet('#le_ncf2egf_bp_cp1{color: #000;}')
            self.le_ncf2egf_bp_cp2.setStyleSheet('#le_ncf2egf_bp_cp2{color: #000;}')
            self.sb_ncf2egf_bp_poles.setStyleSheet('#sb_ncf2egf_bp_poles{color: #000;}')
            self.sb_ncf2egf_bp_passes.setStyleSheet('#sb_ncf2egf_bp_passes{color: #000;}')
        else:
            self.le_ncf2egf_bp_cp1.setEnabled(False)
            self.le_ncf2egf_bp_cp2.setEnabled(False)
            self.sb_ncf2egf_bp_poles.setEnabled(False)
            self.sb_ncf2egf_bp_passes.setEnabled(False)
            self.le_ncf2egf_bp_cp1.setStyleSheet('#le_ncf2egf_bp_cp1{color: #aaa;}')
            self.le_ncf2egf_bp_cp2.setStyleSheet('#le_ncf2egf_bp_cp2{color: #aaa;}')
            self.sb_ncf2egf_bp_poles.setStyleSheet('#sb_ncf2egf_bp_poles{color: #aaa;}')
            self.sb_ncf2egf_bp_passes.setStyleSheet('#sb_ncf2egf_bp_passes{color: #aaa;}')



    def get_parameters(self):
        ncf2egf = {}
        ncf2egf['chb_ncf2egf_symmetrize'] = self.chb_ncf2egf_symmetrize.checkState()
        ncf2egf['chb_ncf2egf_cut'] = self.chb_ncf2egf_cut.checkState()
        ncf2egf['le_ncf2egf_cut_begin'] = self.le_ncf2egf_cut_begin.text()
        ncf2egf['le_ncf2egf_cut_end'] = self.le_ncf2egf_cut_end.text()
        ncf2egf['chb_ncf2egf_bp'] = self.chb_ncf2egf_bp.checkState()
        ncf2egf['le_ncf2egf_bp_cp1'] = self.le_ncf2egf_bp_cp1.text()
        ncf2egf['le_ncf2egf_bp_cp2'] = self.le_ncf2egf_bp_cp2.text()
        ncf2egf['sb_ncf2egf_bp_poles'] = self.sb_ncf2egf_bp_poles.value()
        ncf2egf['sb_ncf2egf_bp_passes'] = self.sb_ncf2egf_bp_passes.value()
        return ncf2egf


    def set_parameters(self, parameters):
        self.chb_ncf2egf_symmetrize.setCheckState(parameters['chb_ncf2egf_symmetrize'])
        self.chb_ncf2egf_cut.setCheckState(int(parameters['chb_ncf2egf_cut']))
        self.le_ncf2egf_cut_begin.setText(f"{parameters['le_ncf2egf_cut_begin']}")
        self.le_ncf2egf_cut_end.setText(f"{parameters['le_ncf2egf_cut_end']}")
        self.chb_ncf2egf_bp.setCheckState(int(parameters['chb_ncf2egf_bp']))
        self.sb_ncf2egf_bp_poles.setValue(int(parameters['sb_ncf2egf_bp_poles']))
        self.sb_ncf2egf_bp_passes.setValue(int(parameters['sb_ncf2egf_bp_passes']))
        self.le_ncf2egf_bp_cp1.setText(f"{parameters['le_ncf2egf_bp_cp1']}")
        self.le_ncf2egf_bp_cp2.setText(f"{parameters['le_ncf2egf_bp_cp2']}")
        self.update_ncf2egf_ui()

        

class ABOUT(QWidget):
    def __init__(self):
        super().__init__()
        about_html = open(os.path.join(pkg_dir, 'ans_about.html'), 'r').read()
        about_te = QTextEdit(self,
            html=about_html,
            readOnly=True,
            )
        about_te.setViewportMargins(10, 0, 30, 30)
        about_te.setObjectName('about_te')
        about_te.setStyleSheet("#%s {border: none; margin-right:20px; color: black}" %('about_te'))

        layout = QGridLayout()
        layout.addWidget(about_te, 0, 0)
        layout.setAlignment(Qt.AlignVCenter)
        layout.setAlignment(Qt.AlignHCenter)
        layout.setContentsMargins(50,50,50,50)
        self.setLayout(layout)



class MainWindow(QMainWindow):
    def __init__(self, maindir):
        super().__init__()
        self.maindir = os.path.abspath(maindir)
        self.setMinimumSize(1000, 600)
        app_icon = QIcon()
        app_icon.addFile(os.path.join(images_dir,'icons','16x16.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','24x24.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','32x32.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','48x48.png'))
        app_icon.addFile(os.path.join(images_dir,'icons','256x256.png'))
        self.setWindowIcon(app_icon)
        self.setWindowTitle("ANS")

        # load external stylesheet file
        with open(os.path.join(pkg_dir,'ans_gui.qss')) as qss:
            qss = qss.read()
            if sys.platform == 'darwin':
                qss = "\nQFrame { font-family: 'Tahoma';\n font-size: 13pt;}\n" + qss
            else:
                qss = "\nQFrame { font-family: 'Tahoma';\n font-size: 11pt;}\n" + qss
        self.setStyleSheet(qss)

        #### HEADER ####
        # header: left
        self.header_left = QFrame()
        self.header_left.setObjectName("header_left")
        lyo_header_left = QHBoxLayout()
        self.btn_menu = QPushButton()
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        lyo_header_left.addWidget(self.btn_menu)
        lyo_header_left.setAlignment(Qt.AlignLeft)
        lyo_header_left.setSpacing(10)
        lyo_header_left.setContentsMargins(10,10,0,10)
        self.header_left.setLayout(lyo_header_left)

        #header: right
        self.header_right = QFrame()
        self.header_right.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,\
                                            QSizePolicy.Expanding))
        self.header_right.setObjectName("header_right")
        lyo_header_right = QHBoxLayout()
        self.btn_logo = QPushButton()
        self.btn_logo.setEnabled(False)
        self.btn_logo.setObjectName("btn_logo")
        lbl_title = QLabel("Ambient Noise Seismology (ANS)")
        lbl_title.setObjectName("lbl_title")
        lyo_header_right.addWidget(self.btn_logo)
        lyo_header_right.addWidget(lbl_title)
        lyo_header_right.setAlignment(Qt.AlignCenter)
        lyo_header_right.setSpacing(5)
        lyo_header_right.setContentsMargins(10,10,0,10)
        self.header_right.setLayout(lyo_header_right)


        # HEADER: LAYOUT
        header = QFrame()
        header.setObjectName("header")
        lyo_header = QHBoxLayout()
        lyo_header.addWidget(self.header_left)
        lyo_header.addWidget(self.header_right)
        lyo_header.setSpacing(0)
        lyo_header.setContentsMargins(0,0,0,0)
        header.setLayout(lyo_header)

        #### BODY ####
        # body: menu
        self.body_menu = QFrame()
        self.body_menu.setObjectName("body_menu")
        menu_top = QFrame()
        menu_top.setObjectName("menu_top")
        self.btn_setting = QPushButton()
        self.btn_setting.setObjectName("btn_setting")
        self.btn_setting.setCursor(Qt.PointingHandCursor)
        self.btn_download = QPushButton()
        self.btn_download.setObjectName("btn_download")
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_mseed2sac = QPushButton()
        self.btn_mseed2sac.setObjectName("btn_mseed2sac")
        self.btn_mseed2sac.setCursor(Qt.PointingHandCursor)
        self.btn_sac2ncf = QPushButton()
        self.btn_sac2ncf.setObjectName("btn_sac2ncf")
        self.btn_sac2ncf.setCursor(Qt.PointingHandCursor)
        self.btn_ncf2egf = QPushButton()
        self.btn_ncf2egf.setObjectName("btn_ncf2egf")
        self.btn_ncf2egf.setCursor(Qt.PointingHandCursor)

        menu_bottom = QFrame()
        menu_bottom.setObjectName("menu_bottom")
        self.btn_terminal = QPushButton()
        self.btn_terminal.setObjectName("btn_terminal")
        self.btn_terminal.setCursor(Qt.PointingHandCursor)
        self.btn_about = QPushButton()
        self.btn_about.setObjectName("btn_about")
        self.btn_about.setCursor(Qt.PointingHandCursor)
        lyo_menu_top = QVBoxLayout()
        lyo_menu_top.addWidget(self.btn_setting)
        lyo_menu_top.addWidget(self.btn_download)
        lyo_menu_top.addWidget(self.btn_mseed2sac)
        lyo_menu_top.addWidget(self.btn_sac2ncf)
        lyo_menu_top.addWidget(self.btn_ncf2egf)
        lyo_menu_top.setAlignment(Qt.AlignTop)
        lyo_menu_top.setSpacing(10)
        lyo_menu_top.setContentsMargins(10,10,10,0)
        lyo_menu_bottom = QVBoxLayout()
        lyo_menu_bottom.addWidget(self.btn_terminal)
        lyo_menu_bottom.addWidget(self.btn_about)
        lyo_menu_bottom.setAlignment(Qt.AlignBottom)
        lyo_menu_bottom.setSpacing(10)
        lyo_menu_bottom.setContentsMargins(10,10,0,10)
        lyo_menu_top.addStretch(1)
        menu_top.setLayout(lyo_menu_top)
        menu_bottom.setLayout(lyo_menu_bottom)
        lyo_body_menu = QVBoxLayout()
        lyo_body_menu.addWidget(menu_top)
        lyo_body_menu.addWidget(menu_bottom)
        lyo_body_menu.setSpacing(0)
        lyo_body_menu.setContentsMargins(0,0,0,0)
        self.body_menu.setLayout(lyo_body_menu)

        # body: main
        self.body_main = QStackedWidget()
        self.body_main.setObjectName("body_main")
        self.body_main.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,\
                                            QSizePolicy.MinimumExpanding))


        # MAIN WIDGET CLASSES
        self.setting = Setting()
        self.download = Download()
        self.mseed2sac = MSEED2SAC()
        self.sac2ncf = SAC2NCF()
        self.ncf2egf = NCF2EGF()
        self.about = ABOUT()

        self.body_main.addWidget(self.setting)
        self.body_main.addWidget(self.download)
        self.body_main.addWidget(self.mseed2sac)
        self.body_main.addWidget(self.sac2ncf)
        self.body_main.addWidget(self.ncf2egf)
        self.body_main.addWidget(self.about)

        # BODY: LAYOUT
        body = QFrame()
        body.setObjectName("body")
        lyo_body = QHBoxLayout()
        lyo_body.addWidget(self.body_menu)
        lyo_body.addWidget(self.body_main)
        lyo_body.setSpacing(0)
        lyo_body.setContentsMargins(0,0,0,0)
        body.setLayout(lyo_body)

        #### FOOTER ####
        footer = QFrame()
        footer.setObjectName("footer")
        footer_left = QFrame()
        footer_left.setObjectName("footer_left")
        footer_right = QFrame()
        footer_right.setObjectName("footer_right")
        lyo_footer = QHBoxLayout()

        # footer_left
        lyo_footer_left = QHBoxLayout()
        lbl_status = QLabel('Ready...')
        lbl_status.setObjectName("lbl_status")
        lyo_footer_left.addWidget(lbl_status)
        lyo_footer_left.setAlignment(Qt.AlignLeft)
        footer_left.setLayout(lyo_footer_left)

        # footer_right
        lyo_footer_right = QHBoxLayout()
        self.btn_save = QPushButton()
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_discard = QPushButton()
        self.btn_discard.setObjectName("btn_discard")
        self.btn_discard.setCursor(Qt.PointingHandCursor)
        self.btn_revert = QPushButton()
        self.btn_revert.setObjectName("btn_revert")
        self.btn_revert.setCursor(Qt.PointingHandCursor)
        lyo_footer_right.addWidget(self.btn_revert)
        lyo_footer_right.addWidget(self.btn_discard)
        lyo_footer_right.addWidget(self.btn_save)
        lyo_footer_right.setAlignment(Qt.AlignRight)
        footer_right.setLayout(lyo_footer_right)
        lyo_footer.addWidget(footer_left)
        lyo_footer.addWidget(footer_right)
        lyo_footer.setSpacing(0)
        lyo_footer.setContentsMargins(0,0,0,0)
        footer.setLayout(lyo_footer)

        #### MAIN ####
        lyo_main = QVBoxLayout()
        lyo_main.addWidget(header)
        lyo_main.addWidget(body)
        lyo_main.addWidget(footer)
        lyo_main.setSpacing(0)
        lyo_main.setContentsMargins(0,0,0,0)
        main = QFrame()
        main.setLayout(lyo_main)
        self.setCentralWidget(main)

        #### APPLY BUTTON STYLES ###

        # PATH to BUTTON ICONS
        # logo
        icon_logo = os.path.join(images_dir,"ans_logo.svg")
        if sys.platform == "win32":
            icon_logo = icon_logo.replace('\\','/')
        # menu
        icon_menu = os.path.join(images_dir,"menu.svg")
        icon_menu_hover = os.path.join(images_dir,"menu_hover.svg")
        if sys.platform == "win32":
            icon_menu = icon_menu.replace('\\','/')
            icon_menu_hover = icon_menu_hover.replace('\\','/')
        # setting
        self.icon_setting = os.path.join(images_dir,"setting.svg")
        self.icon_setting_hover = os.path.join(images_dir,"setting_hover.svg")
        self.icon_setting_selected = os.path.join(images_dir,"setting_selected.svg")
        if sys.platform == "win32":
            self.icon_setting = self.icon_setting.replace('\\','/')
            self.icon_setting_hover = self.icon_setting_hover.replace('\\','/')
            self.icon_setting_selected = self.icon_setting_selected.replace('\\','/')
        # download            
        self.icon_download = os.path.join(images_dir,"download.svg")
        self.icon_download_hover = os.path.join(images_dir,"download_hover.svg")
        self.icon_download_selected = os.path.join(images_dir,"download_selected.svg")
        if sys.platform == "win32":
            self.icon_download = self.icon_download.replace('\\','/')
            self.icon_download_hover = self.icon_download_hover.replace('\\','/')
            self.icon_download_selected = self.icon_download_selected.replace('\\','/')
        # mseed2sac
        self.icon_mseed2sac = os.path.join(images_dir,"mseed2sac.svg")
        self.icon_mseed2sac_hover = os.path.join(images_dir,"mseed2sac_hover.svg")
        self.icon_mseed2sac_selected = os.path.join(images_dir,"mseed2sac_selected.svg")
        if sys.platform == "win32":
            self.icon_mseed2sac = self.icon_mseed2sac.replace('\\','/')
            self.icon_mseed2sac_hover = self.icon_mseed2sac_hover.replace('\\','/')
            self.icon_mseed2sac_selected = self.icon_mseed2sac_selected.replace('\\','/')
        # sac2ncf
        self.icon_sac2ncf = os.path.join(images_dir,"sac2ncf.svg")
        self.icon_sac2ncf_hover = os.path.join(images_dir,"sac2ncf_hover.svg")
        self.icon_sac2ncf_selected = os.path.join(images_dir,"sac2ncf_selected.svg")
        if sys.platform == "win32":
            self.icon_sac2ncf = self.icon_sac2ncf.replace('\\','/')
            self.icon_sac2ncf_hover = self.icon_sac2ncf_hover.replace('\\','/')
            self.icon_sac2ncf_selected = self.icon_sac2ncf_selected.replace('\\','/')
        # ncf2egf
        self.icon_ncf2egf = os.path.join(images_dir,"ncf2egf.svg")
        self.icon_ncf2egf_hover = os.path.join(images_dir,"ncf2egf_hover.svg")
        self.icon_ncf2egf_selected = os.path.join(images_dir,"ncf2egf_selected.svg")
        if sys.platform == "win32":
            self.icon_ncf2egf = self.icon_ncf2egf.replace('\\','/')
            self.icon_ncf2egf_hover = self.icon_ncf2egf_hover.replace('\\','/')
            self.icon_ncf2egf_selected = self.icon_ncf2egf_selected.replace('\\','/')
        # terminal
        icon_terminal = os.path.join(images_dir,"terminal.svg")
        icon_terminal_hover = os.path.join(images_dir,"terminal_hover.svg")
        if sys.platform == "win32":
            icon_terminal = icon_terminal.replace('\\','/')
            icon_terminal_hover = icon_terminal_hover.replace('\\','/')
        # about
        self.icon_about = os.path.join(images_dir,"about.svg")
        self.icon_about_hover = os.path.join(images_dir,"about_hover.svg")
        self.icon_about_selected = os.path.join(images_dir,"about_selected.svg")
        if sys.platform == "win32":
            self.icon_about = self.icon_about.replace('\\','/')
            self.icon_about_hover = self.icon_about_hover.replace('\\','/')
            self.icon_about_selected = self.icon_about_selected.replace('\\','/')
        # save
        icon_save = os.path.join(images_dir,"save.svg")
        icon_save_hover = os.path.join(images_dir,"save_hover.svg")
        if sys.platform == "win32":
            icon_save = icon_save.replace('\\','/')
            icon_save_hover = icon_save_hover.replace('\\','/')
        # discard
        icon_discard = os.path.join(images_dir,"discard.svg")
        icon_discard_hover = os.path.join(images_dir,"discard_hover.svg")
        if sys.platform == "win32":
            icon_discard = icon_discard.replace('\\','/')
            icon_discard_hover = icon_discard_hover.replace('\\','/')
        # revert
        icon_revert = os.path.join(images_dir,"revert.svg")
        icon_revert_hover = os.path.join(images_dir,"revert_hover.svg")
        if sys.platform == "win32":
            icon_revert = icon_revert.replace('\\','/')
            icon_revert_hover = icon_revert_hover.replace('\\','/')
        
        # APPLY BUTTON QSS
        self.set_btn_qss(self.btn_logo, "btn_logo", (50, 50), icon_logo, icon_logo, 3,'#DDDDF9')
        self.set_btn_qss(self.btn_menu, "btn_menu", (176,40), icon_menu, icon_menu_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting, self.icon_setting_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download, self.icon_download_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac, self.icon_mseed2sac_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf, self.icon_sac2ncf_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf, self.icon_ncf2egf_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_terminal, "btn_terminal", (176,40), icon_terminal, icon_terminal_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about, self.icon_about_hover, 1,'#DDDDF9')
        self.set_btn_qss(self.btn_revert, "btn_revert", (167,35), icon_revert, icon_revert_hover,2,'#DDDDF9')
        self.set_btn_qss(self.btn_discard, "btn_discard", (167,35), icon_discard, icon_discard_hover,2,'#DDDDF9')
        self.set_btn_qss(self.btn_save, "btn_save", (167,35), icon_save, icon_save_hover,2,'#DDDDF9')

        # SIGNALS ans SLOTS
        self.btn_setting.clicked.connect(lambda: self.body_main.setCurrentIndex(0))
        self.btn_download.clicked.connect(lambda: self.body_main.setCurrentIndex(1))
        self.btn_mseed2sac.clicked.connect(lambda: self.body_main.setCurrentIndex(2))
        self.btn_sac2ncf.clicked.connect(lambda: self.body_main.setCurrentIndex(3))
        self.btn_ncf2egf.clicked.connect(lambda: self.body_main.setCurrentIndex(4))
        self.btn_about.clicked.connect(lambda: self.body_main.setCurrentIndex(5))
        self.btn_setting.clicked.connect(lambda: self.selected_widget_tab(0))
        self.btn_download.clicked.connect(lambda: self.selected_widget_tab(1))
        self.btn_mseed2sac.clicked.connect(lambda: self.selected_widget_tab(2))
        self.btn_sac2ncf.clicked.connect(lambda: self.selected_widget_tab(3))
        self.btn_ncf2egf.clicked.connect(lambda: self.selected_widget_tab(4))
        self.btn_about.clicked.connect(lambda: self.selected_widget_tab(5))
        self.btn_menu.clicked.connect(self.toggle_menu)
        self.btn_save.clicked.connect(self.save_button)
        self.btn_discard.clicked.connect(self.discard_button)
        self.btn_revert.clicked.connect(self.revert_button)

        #### EXTRA STEPS BEFORE RUNNIG THE APP ####
        input_config = os.path.join(self.maindir,'ans.config')
        if os.path.isfile(input_config):
            parameters = ans_config.read_config(self.maindir)
            self.set_UI_parameters(parameters)
        else:
            print(f"\nError! Could not find 'ans.config' in project directory.\n")
            sys.exit(0)
        
        # hide terminal button (for the first versions)
        self.btn_terminal.setVisible(False)

        # fix failing to update self on Mac!
        QCoreApplication.processEvents()
        self.header_left.setStyleSheet("max-width: 160px")
        self.body_menu.setStyleSheet("max-width: 160px")
        self.toggle_menu()

        # select widget 0
        self.selected_widget_tab(0)
        self.body_main.setCurrentIndex(0)


    def save_button(self):
        parameters = {}
        parameters['setting'] = self.setting.get_parameters()
        parameters['download'] = self.download.get_parameters()
        parameters['mseed2sac'] = self.mseed2sac.get_parameters()
        parameters['sac2ncf'] = self.sac2ncf.get_parameters()
        parameters['ncf2egf'] = self.ncf2egf.get_parameters()
        ans_config.write_config(parameters['setting']['le_maindir'], parameters)
        if not os.path.isdir(os.path.join(parameters['setting']['le_maindir'], '.ans')):
            os.mkdir(os.path.join(parameters['setting']['le_maindir'], '.ans'))
        sys.exit(0)


    def discard_button(self):
        sys.exit(0)


    def revert_button(self):
        current_parameters = {}
        current_parameters['setting'] = self.setting.get_parameters() 
        current_parameters['download'] = self.download.get_parameters()
        current_parameters['mseed2sac'] = self.mseed2sac.get_parameters()
        current_parameters['sac2ncf'] = self.sac2ncf.get_parameters()
        current_parameters['ncf2egf'] = self.ncf2egf.get_parameters()
        defaults = ans_config.Defaults(self.maindir)
        current_index = self.body_main.currentIndex()

        if current_index == 0:
            current_parameters['setting'] = defaults.setting()
        elif current_index == 1:
            current_parameters['download'] = defaults.download()
        elif current_index == 2:
            current_parameters['mseed2sac'] = defaults.mseed2sac()
        elif current_index == 3:
            current_parameters['sac2ncf'] = defaults.sac2ncf()
        elif current_index == 4:
            current_parameters['ncf2egf'] = defaults.ncf2egf()

        self.set_UI_parameters(current_parameters)


    def set_UI_parameters(self, parameters):
        # setting
        self.setting.findChild(MyLineEdit, 'le_maindir').setText(f"{parameters['setting']['le_maindir']}")
        self.setting.findChild(MyLineEdit, 'le_startdate').setText(f"{parameters['setting']['le_startdate']}")
        self.setting.findChild(MyLineEdit, 'le_enddate').setText(f"{parameters['setting']['le_enddate']}")
        self.setting.findChild(MyLineEdit, 'le_maxlat').setText(f"{parameters['setting']['le_maxlat']}")
        self.setting.findChild(MyLineEdit, 'le_minlon').setText(f"{parameters['setting']['le_minlon']}")
        self.setting.findChild(MyLineEdit, 'le_maxlon').setText(f"{parameters['setting']['le_maxlon']}")
        self.setting.findChild(MyLineEdit, 'le_minlat').setText(f"{parameters['setting']['le_minlat']}")
        self.setting.findChild(MyLineEdit, 'le_sac').setText(parameters['setting']['le_sac'])
        self.setting.findChild(MyLineEdit, 'le_gmt').setText(parameters['setting']['le_gmt'])
        self.setting.findChild(MyLineEdit, 'le_perl').setText(parameters['setting']['le_perl'])
        # download
        self.download.findChild(MyCheckBox, 'chb_dc_service_iris_edu').setCheckState(parameters['download']['chb_dc_service_iris_edu'])
        self.download.findChild(MyCheckBox, 'chb_dc_service_ncedc_org').setCheckState(parameters['download']['chb_dc_service_ncedc_org'])
        self.download.findChild(MyCheckBox, 'chb_dc_service_scedc_caltech_edu').setCheckState(parameters['download']['chb_dc_service_scedc_caltech_edu'])
        self.download.findChild(MyCheckBox, 'chb_dc_rtserve_beg_utexas_edu').setCheckState(parameters['download']['chb_dc_rtserve_beg_utexas_edu'])
        self.download.findChild(MyCheckBox, 'chb_dc_eida_bgr_de').setCheckState(parameters['download']['chb_dc_eida_bgr_de'])
        self.download.findChild(MyCheckBox, 'chb_dc_ws_resif_fr').setCheckState(parameters['download']['chb_dc_ws_resif_fr'])
        self.download.findChild(MyCheckBox, 'chb_dc_seisrequest_iag_usp_br').setCheckState(parameters['download']['chb_dc_seisrequest_iag_usp_br'])
        self.download.findChild(MyCheckBox, 'chb_dc_eida_service_koeri_boun_edu_tr').setCheckState(parameters['download']['chb_dc_eida_service_koeri_boun_edu_tr'])
        self.download.findChild(MyCheckBox, 'chb_dc_eida_ethz_ch').setCheckState(parameters['download']['chb_dc_eida_ethz_ch'])
        self.download.findChild(MyCheckBox, 'chb_dc_geofon_gfz_potsdam_de').setCheckState(parameters['download']['chb_dc_geofon_gfz_potsdam_de'])
        self.download.findChild(MyCheckBox, 'chb_dc_ws_icgc_cat').setCheckState(parameters['download']['chb_dc_ws_icgc_cat'])
        self.download.findChild(MyCheckBox, 'chb_dc_eida_ipgp_fr').setCheckState(parameters['download']['chb_dc_eida_ipgp_fr'])
        self.download.findChild(MyCheckBox, 'chb_dc_fdsnws_raspberryshakedata_com').setCheckState(parameters['download']['chb_dc_fdsnws_raspberryshakedata_com'])
        self.download.findChild(MyCheckBox, 'chb_dc_webservices_ingv_it').setCheckState(parameters['download']['chb_dc_webservices_ingv_it'])
        self.download.findChild(MyCheckBox, 'chb_dc_erde_geophysik_uni_muenchen_de').setCheckState(parameters['download']['chb_dc_erde_geophysik_uni_muenchen_de'])
        self.download.findChild(MyCheckBox, 'chb_dc_eida_sc3_infp_ro').setCheckState(parameters['download']['chb_dc_eida_sc3_infp_ro'])
        self.download.findChild(MyCheckBox, 'chb_dc_eida_gein_noa_gr').setCheckState(parameters['download']['chb_dc_eida_gein_noa_gr'])
        self.download.findChild(MyCheckBox, 'chb_dc_www_orfeus_eu_org').setCheckState(parameters['download']['chb_dc_www_orfeus_eu_org'])
        self.download.findChild(MyCheckBox, 'chb_dc_auspass_edu_au').setCheckState(parameters['download']['chb_dc_auspass_edu_au'])
        self.download.findChild(MyCheckBox, 'chb_obspy').setCheckState(parameters['download']['chb_obspy'])
        self.download.findChild(MyCheckBox, 'chb_fetch').setCheckState(parameters['download']['chb_fetch'])
        self.download.findChild(MyLineEdit, 'le_stalist').setText(parameters['download']['le_stalist'])
        self.download.findChild(MyLineEdit, 'le_stameta').setText(parameters['download']['le_stameta'])
        self.download.findChild(MyLineEdit, 'le_mseeds').setText(parameters['download']['le_mseeds'])
        self.download.findChild(MyLineEdit, 'le_stalocs').setText(parameters['download']['le_stalocs'])
        self.download.findChild(MyLineEdit, 'le_stachns').setText(parameters['download']['le_stachns'])
        self.download.findChild(MyLineEdit, 'le_timelen').setText(f"{parameters['download']['le_timelen']}")
        
        # mseed2sac
        # mseed2sac: remove old processes
        old_mseed2sac_nprocs = self.mseed2sac.get_num_procs()
        for i in range(old_mseed2sac_nprocs):
            self.mseed2sac.remove_proc_frame()
        # mseed2sac: add new processes
        nprocs = len(parameters['mseed2sac']['mseed2sac_procs'])
        for i in range(nprocs):
            self.mseed2sac.add_proc_frame(pid=parameters['mseed2sac']['mseed2sac_procs'][i]['pid'] ,
                                          params=parameters['mseed2sac']['mseed2sac_procs'][i])

        # sac2ncf
        # sac2ncf: remove old processes
        old_sac2ncf_nprocs = self.sac2ncf.get_num_procs()
        for i in range(old_sac2ncf_nprocs):
            self.sac2ncf.remove_proc_frame()
        # sac2ncf: add new processes
        nprocs = len(parameters['sac2ncf']['sac2ncf_procs'])
        for i in range(nprocs):
            self.sac2ncf.add_proc_frame(pid=parameters['sac2ncf']['sac2ncf_procs'][i]['pid'] ,
                                          params=parameters['sac2ncf']['sac2ncf_procs'][i])

        # ncf2egf
        self.ncf2egf.set_parameters(parameters['ncf2egf'])




    def selected_widget_tab(self, widget_index): # apply proper qss to the selected widget button
        if widget_index == 0:
            self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting_selected, self.icon_setting_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download, self.icon_download_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac, self.icon_mseed2sac_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf, self.icon_sac2ncf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf, self.icon_ncf2egf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about, self.icon_about_hover, 1,'#DDDDF9')
        elif widget_index == 1:
            self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting, self.icon_setting_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download_selected, self.icon_download_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac, self.icon_mseed2sac_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf, self.icon_sac2ncf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf, self.icon_ncf2egf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about, self.icon_about_hover, 1,'#DDDDF9')
        elif widget_index == 2:
            self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting, self.icon_setting_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download, self.icon_download_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac_selected, self.icon_mseed2sac_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf, self.icon_sac2ncf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf, self.icon_ncf2egf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about, self.icon_about_hover, 1,'#DDDDF9')
        elif widget_index == 3:
            self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting, self.icon_setting_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download, self.icon_download_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac, self.icon_mseed2sac_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf_selected, self.icon_sac2ncf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf, self.icon_ncf2egf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about, self.icon_about_hover, 1,'#DDDDF9')
        elif widget_index == 4:
            self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting, self.icon_setting_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download, self.icon_download_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac, self.icon_mseed2sac_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf, self.icon_sac2ncf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf_selected, self.icon_ncf2egf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about, self.icon_about_hover, 1,'#DDDDF9')
        elif widget_index == 5:
            self.set_btn_qss(self.btn_setting, "btn_setting", (176,40), self.icon_setting, self.icon_setting_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_download, "btn_download", (176,40), self.icon_download, self.icon_download_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_mseed2sac, "btn_mseed2sac", (176,40), self.icon_mseed2sac, self.icon_mseed2sac_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_sac2ncf, "btn_sac2ncf", (176,40), self.icon_sac2ncf, self.icon_sac2ncf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_ncf2egf, "btn_ncf2egf", (176,40), self.icon_ncf2egf, self.icon_ncf2egf_hover, 1,'#DDDDF9')
            self.set_btn_qss(self.btn_about, "btn_about", (176,40), self.icon_about_selected, self.icon_about_hover, 1,'#DDDDF9')



    def set_btn_qss(self, btn_obj, btn_obj_name,\
                    btn_size, icon_file, icon_hover_file,\
                    icon_clicked_border_size, icon_clicked_border_color):
        qss_code = '''
            #%s {
                min-width: %dpx;
                max-width: %dpx;
                min-height: %dpx;
                max-height: %dpx;
                border: none;
                image: url(%s);
            }

            #%s:hover {
                image: url(%s);
            }

            #%s:pressed {
                border-top: %dpx solid %s;
                border-right: %dpx solid %s;
            }
        ''' %(btn_obj_name, btn_size[0], btn_size[0], btn_size[1], btn_size[1],\
              icon_file, btn_obj_name, icon_hover_file, btn_obj_name,\
              icon_clicked_border_size, icon_clicked_border_color,\
              icon_clicked_border_size, icon_clicked_border_color)
        btn_obj.setStyleSheet(qss_code)

    
    def toggle_menu(self):
        self.anim_body_main = QPropertyAnimation(self.body_main, b'minimumWidth')
        self.anim_body_menu = QPropertyAnimation(self.body_menu, b'maximumWidth')
        self.anim_header_right = QPropertyAnimation(self.header_right, b'minimumWidth')
        self.anim_header_left = QPropertyAnimation(self.header_left, b'maximumWidth')
        self.anim_body_main.setDuration(170)
        self.anim_body_menu.setDuration(170)
        self.anim_header_left.setDuration(170)
        self.anim_header_right.setDuration(170)
        maxWidth = self.width() - 60
        minWidth = self.width() - 190
        if self.body_menu.width() != 60:
            self.anim_body_main.setEndValue(self.width() - 60)
            self.anim_body_menu.setEndValue(60)
            self.anim_header_right.setEndValue(self.width() - 60)
            self.anim_header_left.setEndValue(60)
        else:
            self.anim_body_main.setEndValue(self.width() - 190)
            self.anim_body_menu.setEndValue(190)
            self.anim_header_right.setEndValue(self.width() - 190)
            self.anim_header_left.setEndValue(190)
        self.anim_body_menu.start()
        self.anim_body_main.start()
        self.anim_header_left.start()
        self.anim_header_right.start()

    
