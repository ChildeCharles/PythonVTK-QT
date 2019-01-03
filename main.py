from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.browse_button.pressed.connect(self.choose_input_file)
        self.delete_button.pressed.connect(self.delete_selected)

        self.list_model = QStandardItemModel()
        self.list_view.setModel(self.list_model)

        self.list_model.itemChanged.connect(self.update_preview)

        self.vtk_widget = QVTKRenderWindowInteractor(self.vtk_display)
        self.vtk_widget.resize(self.vtk_display.size())
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(interactor_style)

        self.actors = {}

        self.interactor.Initialize()

    def choose_input_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        filename, _ = dialog.getOpenFileName(dialog, "Open STL file", "", "STL files (*.stl)")
        self.filename_input.setText(filename.split('/')[-1])
        item = QStandardItem()
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setData(QVariant(Qt.Unchecked), Qt.CheckStateRole)
        item.setData(filename, Qt.UserRole)
        item.setData(filename.split('/')[-1], Qt.DisplayRole)
        self.list_model.appendRow(item)

    def update_preview(self, item):
        if item.data(Qt.CheckStateRole) == QVariant(Qt.Checked):
            self.create_actor(item)
        else:
            self.remove_actor(item)

    def create_actor(self, item):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(item.data(Qt.UserRole))

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.actors[id(item)] = actor
        self.renderer.AddActor(actor)
        self.vtk_widget.update()

    def remove_actor(self, item):
        self.renderer.RemoveActor(self.actors[id(item)])
        self.actors.pop(id(item))
        self.vtk_widget.update()

    def delete_selected(self):
        for i in range(self.list_model.rowCount()-1, -1, -1):
            if self.list_model.item(i).data(Qt.CheckStateRole) == QVariant(Qt.Checked):
                self.remove_actor(self.list_model.item(i))
                self.list_model.removeRow(i)

    def connect_quit_button(self, app: QApplication):
        self.quit_button.pressed.connect(app.quit)


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.connect_quit_button(app)
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
