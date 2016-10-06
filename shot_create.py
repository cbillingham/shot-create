import sys
import os
import subprocess
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *


shot_create_main = "shot-create.ui"
shot_create_pref = "edit-pref.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(shot_create_main)
Ui_pref, QtBaseClass = uic.loadUiType(shot_create_pref)

class Pref(QtGui.QDialog, Ui_pref):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        Ui_pref.__init__(self)
        self.setupUi(self)

class ShotCreate(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.menuBar().setNativeMenuBar(False)
        self.cancel_btn.clicked.connect(QtGui.qApp.quit)
        self.actionQuit_shot_create.triggered.connect(QtGui.qApp.quit)
        self.actionPreferences.triggered.connect(self.changePref)
        self.actionOpen_project.triggered.connect(self.selectDir)
        self.new_shot = ""
        self.add_shot_btn.clicked.connect(self.addShot)
        self.add_seq_btn.clicked.connect(self.newSeq)
        self.build_btn.clicked.connect(self.buildFile)
        self.shot_assets = {}
        self.add_asset_btn.clicked.connect(self.addAsset)
        self.remove_asset_btn.clicked.connect(self.removeAsset)
        self.env_asset_dir_view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.env_asset_dir_view.header().setStretchLastSection(False)
        self.char_asset_dir_view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.char_asset_dir_view.header().setStretchLastSection(False)
        self.prop_asset_dir_view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.prop_asset_dir_view.header().setStretchLastSection(False)
        self.env_asset_dir_view.clicked.connect(self.updatePreview)
        self.char_asset_dir_view.clicked.connect(self.updatePreview)
        self.prop_asset_dir_view.clicked.connect(self.updatePreview)
        self.load.currentChanged.connect(self.updatePreview)

    def selectDir(self):
        pDir = str(QtGui.QFileDialog.getExistingDirectory(self, "Open Project Directory",os.path.expanduser("~/Documents/maya"), QtGui.QFileDialog.ShowDirsOnly))
        if pDir is "":
            if not hasattr(self, "current_dir"):
                sys.exit()
        else:
            self.current_dir = pDir
            self.new_shot = ""
            self.shot_lb.setText("")
            self.current_seq_dir = ""
        self.runMain()

    def runMain(self):
        project = os.path.basename(self.current_dir)
        self.project_lb.setText(project)
        self.setupDirs()
        self.setupSeqs()
        self.setupAssets()
        self.show()

    def setupDirs(self):
        self.seq_dirs = self.current_dir + "/scenes"
        self.char_asset_dir = self.current_dir + "/assets/chars"
        self.env_asset_dir = self.current_dir + "/assets/envs"
        self.prop_asset_dir = self.current_dir + "/assets/props"

    def changePref(self):
        QtGui.QMessageBox.information(self, 'Coming Soon...', "Changing preferences is a work in progress. It will be available in the next release.")

    def setupSeqs(self):
        self.scenes.clear()
        self.scenes.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        try:
            scene_dirs = os.walk(self.seq_dirs).next()[1]
            self.scenes.addItems(scene_dirs)
            self.scenes.currentItemChanged.connect(self.updateSceneDir)
            self.add_seq_btn.setEnabled(True)
            self.add_shot_btn.setEnabled(True)
        except Exception:
            warning = QListWidgetItem(self.seq_dirs + " does not exist")
            warning.setTextColor(QtGui.QColor(255,0,0))
            self.scenes.addItem(warning)
            self.scenes.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.add_seq_btn.setEnabled(False)
            self.add_shot_btn.setEnabled(False)      

    def updateSceneDir(self):
        self.current_seq_dir = str(self.seq_dirs + "/" + self.scenes.currentItem().text())
        self.updateShots()
        self.sqn_lb.setText(os.path.basename(self.current_seq_dir))

    def updateShots(self):
        self.shots.clear()
        self.current_shots = []
        for file in os.listdir(self.current_seq_dir):
            if file.endswith(".ma") or file.endswith(".mb"):
                self.current_shots.append(file)
        if self.current_shots == []:
            warning = QListWidgetItem("No shots currently in this sequence")
            warning.setTextColor(QtGui.QColor(255,0,0))
            self.shots.addItem(warning)
        else:
            self.shots.addItems(self.current_shots)

    def setupAssets(self):
        self.shot_assets = {};
        try:
            if not os.path.exists(self.char_asset_dir):
                raise Exception()
            charmodel = QtGui.QFileSystemModel()
            charmodel.setRootPath(self.char_asset_dir)
            charmodel.setNameFilters(["*.ma","*.mb"])
            charmodel.setNameFilterDisables(False)
            self.char_asset_dir_view.setModel(charmodel)
            self.char_asset_dir_view.setRootIndex(charmodel.index(self.char_asset_dir))
        except Exception as e:
            warning = QStandardItem(self.char_asset_dir + " does not exist")
            warningmodel = QStandardItemModel()
            warningmodel.appendRow(warning)
            self.char_asset_dir_view.setModel(warningmodel)
        try:
            if not os.path.exists(self.env_asset_dir):
                raise Exception()
            charmodel = QtGui.QFileSystemModel()
            charmodel.setRootPath(self.env_asset_dir)
            charmodel.setNameFilters(["*.ma","*.mb"])
            charmodel.setNameFilterDisables(False)
            self.env_asset_dir_view.setModel(charmodel)
            self.env_asset_dir_view.setRootIndex(charmodel.index(self.env_asset_dir))
        except Exception as e:
            warning = QStandardItem(self.env_asset_dir + " does not exist")
            warningmodel = QStandardItemModel()
            warningmodel.appendRow(warning)
            self.env_asset_dir_view.setModel(warningmodel)
        try:
            if not os.path.exists(self.prop_asset_dir):
                raise Exception()
            charmodel = QtGui.QFileSystemModel()
            charmodel.setRootPath(self.prop_asset_dir)
            charmodel.setNameFilters(["*.ma","*.mb"])
            charmodel.setNameFilterDisables(False)
            self.prop_asset_dir_view.setModel(charmodel)
            self.prop_asset_dir_view.setRootIndex(charmodel.index(self.prop_asset_dir))
        except Exception as e:
            warning = QStandardItem(self.prop_asset_dir + " does not exist")
            warningmodel = QStandardItemModel()
            warningmodel.appendRow(warning)
            self.prop_asset_dir_view.setModel(warningmodel)

    def buildFile(self):
        run = True
        if self.new_shot == "" or self.current_seq_dir is "":
            QtGui.QMessageBox.information(self, 'Error', "You have not named your shot. You must set a shot name before building your maya file.")
            run = False
        elif not self.shot_assets:
            reply = QtGui.QMessageBox.question(self, "Save empty file?", "You have not added any assets to your shot. Are you sure you want to build an empty file?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                run = False
        if (run):
            self.progress = QtGui.QProgressDialog("Building your file...","Please wait...",0,0,self) 
            self.progress.setWindowTitle('Please wait...')
            self.progress.setWindowModality(QtCore.Qt.WindowModal)
            self.progress.show()
            path = self.current_seq_dir + "/" + self.new_shot + ".ma"
            fstop = float(str(self.fstop.currentText()))
            lens = int(str(self.focal_length.currentText()))
            shutter = int(self.shutter_angle.value())
            buildcommands = "import maya.standalone; maya.standalone.initialize(); import maya.cmds as cmds; cmds.file(newFile=True, force=True); "
            for asset, asset_path in self.shot_assets.iteritems():
                asset_title, asset_ext = os.path.splitext(asset)
                ref = 'cmds.file(\"{0}\",r=True,uns=True,lrd=\"all\",mnc=False,ns=\"{1}\"); '.format(asset_path, asset_title)
                buildcommands += ref
            camera = 'cmds.camera(fs={0},fl={1},sa={2}); '.format(fstop, lens, shutter)
            buildcommands += camera
            save = 'cmds.file(rename=\"{0}\"); cmds.file(save=True,type=\"mayaAscii\", force=True); '.format(path)
            buildcommands += save
            mayapy = '/Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy -c \'{0}\''.format(buildcommands)
            try:
                subprocess.call(mayapy, shell=True)
                self.progress.close()
                self.complete(path)
            except OSError as e:
                self.progress.close()
                QtGui.QMessageBox.information(self, 'Error', "There was an issue when building your file. Could not access /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy")
            

    def complete(self, path):
        message = "Build Complete. Your shot was saved to {0}.\nWould you like to build another shot?".format(path)
        reply = QtGui.QMessageBox.question(self, "Build Complete", message, QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Cancel:
            sys.exit()
        else:
            self.selectDir()

    def addShot(self):
        title = str(self.shot_title.text())
        if title == "":
            QtGui.QMessageBox.information(self, 'Error', "Please enter a valid title for your shot")
        else:
            self.new_shot = title
            self.shot_lb.setText(title)
            self.selectWindow.setCurrentIndex(1);

    def newSeq(self):
        title = str(self.new_sqn_title.text())
        path = self.seq_dirs + "/" + title
        if os.path.exists(path):
            QtGui.QMessageBox.information(self, 'Error', "This sequence directory already exists.")
        else:
            os.makedirs(path)
            self.scenes.addItem(title)
            self.scenes.setCurrentRow(self.scenes.count()-1)
            self.updateSceneDir()
    
    def addAsset(self):
        try:
            assets = [self.char_asset_dir_view, self.env_asset_dir_view, self.prop_asset_dir_view]
            assetDir = assets[self.load.currentIndex()]
            index = assetDir.selectedIndexes()[0]
            asset = str(index.model().fileName(index))
            asset_path = str(index.model().filePath(index))
            if os.path.isdir(asset_path):
                raise Exception("Please select a Maya asset file to add your shot")
            if asset in self.shot_assets:
                raise Exception("You already added this asset")
            self.shot_assets[asset] = asset_path
            self.shot_assets_view.addItem(asset)
        except Exception as e:
            QtGui.QMessageBox.information(self, 'Error', e.message)

    def removeAsset(self):
        try:
            asset = str(self.shot_assets_view.takeItem(self.shot_assets_view.currentRow()).text())
            self.shot_assets.pop(asset)
        except Exception:
            #nothing left to remove. Do nothing
            return

    def updatePreview(self):
        self.preview.clear()
        self.preview_left_btn.setEnabled(False)
        self.preview_right_btn.setEnabled(False)
        assets = [self.char_asset_dir_view, self.env_asset_dir_view, self.prop_asset_dir_view]
        assetDir = assets[self.load.currentIndex()]
        try:
            index = assetDir.selectedIndexes()[0]
            asset = str(index.model().fileName(index))
            if not asset.endswith((".ma",".mb")):
                raise Exception("not an actual maya asset file")
            asset_path = str(index.model().filePath(index))
            asset_dir = os.path.dirname(asset_path)
            self.prevs = []
            self.prevs_index = 0
            for root, dirs, files in os.walk(asset_dir):
                for file in files:
                    if file.endswith((".jpg",".png",".tif")):
                        self.prevs.append(os.path.join(root, file))
        except Exception:
            self.prevs=[]
        if not self.prevs:
            self.preview.setText("No Preview")
        else:
            myPixmap = QtGui.QPixmap(self.prevs[self.prevs_index])
            self.preview.setPixmap(myPixmap.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio))
            self.preview_left_btn.clicked.connect(self.prevBack)
            self.preview_left_btn.setEnabled(True)
            self.preview_right_btn.clicked.connect(self.prevForward)
            self.preview_right_btn.setEnabled(True)

    def prevBack(self):
        self.prevs_index -= 1
        myPixmap = QtGui.QPixmap(self.prevs[self.prevs_index%len(self.prevs)])
        self.preview.setPixmap(myPixmap.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio))

    def prevForward(self):
        self.prevs_index += 1
        myPixmap = QtGui.QPixmap(self.prevs[self.prevs_index%len(self.prevs)])
        self.preview.setPixmap(myPixmap.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = ShotCreate()
    window.selectDir()
    sys.exit(app.exec_())
