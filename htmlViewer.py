import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTreeView,
                               QSplitter, QMessageBox)
from PySide6.QtCore import (Qt, QDir, QSortFilterProxyModel,
                            QModelIndex, QItemSelectionModel, QUrl)
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QFileSystemModel

class HtmlDirFilterProxy(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        
        # Mostrar diretórios e arquivos .html (case insensitive)
        if source_model.isDir(index):
            return True
        file_name = source_model.fileName(index)
        return file_name.lower().endswith('.html')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_root = None
        self.initUI()
        self.setupModels()
        self.setupConnections()

    def initUI(self):
        self.setWindowTitle('HTML Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Criar widgets
        self.splitter = QSplitter(Qt.Horizontal)
        self.tree_view = QTreeView()
        self.web_view = QWebEngineView()
        
        # Configurar layout
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.web_view)
        self.splitter.setSizes([200, 600])
        self.setCentralWidget(self.splitter)

        # Criar menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&Arquivo')
        
        open_action = QAction('Abrir Diretório', self)
        open_action.triggered.connect(self.open_directory)
        file_menu.addAction(open_action)

    def setupModels(self):
        # Modelo de sistema de arquivos
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath('')
        self.file_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)

        # Proxy model para filtragem
        self.proxy_model = HtmlDirFilterProxy()
        self.proxy_model.setSourceModel(self.file_model)
        
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.hideColumn(1)  # Esconder colunas extras
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)

    def setupConnections(self):
        # Conectar clique na árvore
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        
        # Conectar mudança de URL no web view
        self.web_view.urlChanged.connect(self.on_url_changed)

    def open_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório")
        if dir_path:
            self.current_root = dir_path
            source_index = self.file_model.index(dir_path)
            proxy_index = self.proxy_model.mapFromSource(source_index)
            self.tree_view.setRootIndex(proxy_index)
            self.tree_view.expand(proxy_index)
            self.tree_view.selectionModel().clearSelection()

    def on_tree_view_clicked(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        file_path = self.file_model.filePath(source_index)
        
        if not self.file_model.isDir(source_index):
            self.load_html_file(file_path)

    def load_html_file(self, file_path):
        url = QUrl.fromLocalFile(file_path)
        self.web_view.load(url)

    def on_url_changed(self, url):
        if url.isLocalFile():
            file_path = url.toLocalFile()
            
            if self.current_root and file_path.startswith(self.current_root):
                source_index = self.file_model.index(file_path)
                if source_index.isValid():
                    proxy_index = self.proxy_model.mapFromSource(source_index)
                    self.tree_view.selectionModel().select(
                        proxy_index, 
                        QItemSelectionModel.ClearAndSelect
                    )
                    self.tree_view.scrollTo(proxy_index)
            else:
                # Se o arquivo está fora do diretório raiz, abrir no navegador padrão
                QApplication.instance().desktop().openUrl(url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())