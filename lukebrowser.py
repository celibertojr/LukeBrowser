
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QTabWidget,
    QMessageBox, QMenuBar, QInputDialog, QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEnginePage, QWebEngineProfile
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".lukebrowser")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class TelaConfiguracao(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações do LuKe Browser")
        self.setGeometry(200, 200, 400, 300)
        self._simular_interface()

    def _simular_interface(self):
        label = QLabel("Aqui você poderá ajustar configurações futuras como cache, desempenho, etc.", self)
        label.setWordWrap(True)
        label.setGeometry(20, 20, 360, 260)

class BloqueadorRequisicoes(QWebEngineUrlRequestInterceptor):
    def __init__(self, ativado=True):
        super().__init__()
        self.ativado = ativado
        self.dominios_bloqueados = [
            "doubleclick.net", "googlesyndication.com", "googleadservices.com",
            "ads.pubmatic.com", "adnxs.com", "facebook.net", "criteo.com",
            "taboola.com", "scorecardresearch.com", "quantserve.com"
        ]

    def interceptRequest(self, info):
        if self.ativado:
            url = info.requestUrl().toString()
            for dominio in self.dominios_bloqueados:
                if dominio in url:
                    info.block(True)
                    return

def icone_default(nome):
    style = QApplication.style()
    
    
    
    
    
    
    
    return {
        "voltar": style.standardIcon(QStyle.SP_ArrowBack),
        "avancar": style.standardIcon(QStyle.SP_ArrowForward),
        "recarregar": style.standardIcon(QStyle.SP_BrowserReload),
        "home": style.standardIcon(QStyle.SP_DirHomeIcon),
        "ir": style.standardIcon(QStyle.SP_ArrowRight),
        "novaaba": style.standardIcon(QStyle.SP_FileDialogNewFolder),
        "fecharaba": style.standardIcon(QStyle.SP_DockWidgetCloseButton),
    }.get(nome, QIcon())

class BrowserAba(QWidget):
    def __init__(self, url_inicial, perfil):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.page = QWebEnginePage(perfil, self.web_view)
        self.web_view.setPage(self.page)
        self.web_view.load(QUrl(url_inicial))
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

class LuKeBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LuKe Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.bloqueio_ativo = True
        self.bloqueador = BloqueadorRequisicoes(self.bloqueio_ativo)

        self.modo_privado = False
        self.perfil_padrao = QWebEngineProfile.defaultProfile()
        self.perfil_padrao.setRequestInterceptor(self.bloqueador)

        self.perfil_privado = QWebEngineProfile()
        self.perfil_privado.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.perfil_privado.setRequestInterceptor(self.bloqueador)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.fechar_aba)
        self.tabs.currentChanged.connect(self.atualizar_url_bar)
        self.setCentralWidget(self.tabs)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navegar_para_url)

        self._criar_toolbar()
        self._criar_menu()

        self.nova_aba(self._carregar_url_padrao())

    def _criar_toolbar(self):
        toolbar = QToolBar("Navegação")
        toolbar.setIconSize(QSize(36, 36))
        self.addToolBar(toolbar)
        
        
        # Aplicar estilo aos botões da toolbar
        toolbar.setStyleSheet("""
            QToolButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background-color: #f5f5f5;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
            QToolTip {
                font-size: 12px;
                color: #fff;
                background-color: #333;
                border: 1px solid #666;
                padding: 4px;
            }
        """)
        
        
        
        
        
        

        btn_voltar = QAction(icone_default("voltar"), "Voltar", self)
        btn_voltar.triggered.connect(lambda: self.tab_atual().web_view.back())
        toolbar.addAction(btn_voltar)

        btn_avancar = QAction(icone_default("avancar"), "Avançar", self)
        btn_avancar.triggered.connect(lambda: self.tab_atual().web_view.forward())
        toolbar.addAction(btn_avancar)

        btn_recarregar = QAction(icone_default("recarregar"), "Recarregar", self)
        btn_recarregar.triggered.connect(lambda: self.tab_atual().web_view.reload())
        toolbar.addAction(btn_recarregar)

        btn_home = QAction(icone_default("home"), "Início", self)
        btn_home.triggered.connect(lambda: self.tab_atual().web_view.load(QUrl(self._carregar_url_padrao())))
        toolbar.addAction(btn_home)

        toolbar.addWidget(self.url_bar)

        btn_ir = QAction(icone_default("ir"), "Ir", self)
        btn_ir.triggered.connect(self.navegar_para_url)
        toolbar.addAction(btn_ir)

        btn_nova = QAction(icone_default("novaaba"), "Nova aba", self)
        btn_nova.triggered.connect(lambda: self.nova_aba(self._carregar_url_padrao()))
        toolbar.addAction(btn_nova)

    def _criar_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        arquivo = menu_bar.addMenu("Arquivo")
        arquivo.addAction("Nova aba", lambda: self.nova_aba(self._carregar_url_padrao()))
        arquivo.addAction("Sair", self.close)

        ferramentas = menu_bar.addMenu("Ferramentas")

        self.acao_bloqueio = QAction("Bloquear anúncios e rastreadores", self, checkable=True, checked=True)
        self.acao_bloqueio.triggered.connect(self.alternar_bloqueio)
        ferramentas.addAction(self.acao_bloqueio)
        
        
        self.acao_privado = QAction("Ativar Privado", self, checkable=True, checked=True)
        self.acao_privado.triggered.connect(self.alternar_privado)
        ferramentas.addAction(self.acao_privado)
        
        
        
        

        #ferramentas.addAction("Ativar modo privado", self.ativar_modo_privado)
        #ferramentas.addAction("Desativar modo privado", self.desativar_modo_privado)
        
        ferramentas.addAction("Definir página inicial", self.definir_pagina_inicial)
        ferramentas.addAction("Configurações", self.abrir_configuracoes)

        ajuda = menu_bar.addMenu("Ajuda")
        ajuda.addAction("Sobre", self.mostrar_sobre)

    def abrir_configuracoes(self):
        self.config_window = TelaConfiguracao()
        self.config_window.show()

    def alternar_bloqueio(self):
        self.bloqueio_ativo = self.acao_bloqueio.isChecked()
        self.bloqueador.ativado = self.bloqueio_ativo
        msg = "Bloqueio ativado." if self.bloqueio_ativo else "Bloqueio desativado."
        QMessageBox.information(self, "Bloqueio de anúncios", msg)
        
        
    def alternar_privado(self):
        self.modo_privado = self.acao_privado.isChecked()
        msg = "Privado ativado." if self.modo_privado else "Privado desativado."
        QMessageBox.information(self, "Privado ON/OFF", msg)
       


    def tab_atual(self):
        return self.tabs.currentWidget()

    def nova_aba(self, url):
        perfil = self.perfil_privado if self.modo_privado else self.perfil_padrao
        nova = BrowserAba(url, perfil)
        idx = self.tabs.addTab(nova, "Nova Aba")
        self.tabs.setCurrentIndex(idx)
        nova.web_view.loadFinished.connect(lambda: self.tabs.setTabText(idx, nova.web_view.title()))
        nova.web_view.urlChanged.connect(lambda _: self.atualizar_url_bar(self.tabs.currentIndex()))

    def fechar_aba(self, idx):
        if self.tabs.count() > 1:
            self.tabs.removeTab(idx)

    def navegar_para_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.tab_atual().web_view.load(QUrl(url))

    def atualizar_url_bar(self, idx):
        if idx >= 0:
            url = self.tab_atual().web_view.url().toString()
            self.url_bar.setText(url)

    def _carregar_url_padrao(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    return config.get("home", "https://www.google.com")
            except:
                pass
        return "https://www.google.com"

    def definir_pagina_inicial(self):
        url, ok = QInputDialog.getText(self, "Página inicial", "Digite a URL:")
        if ok and url:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump({"home": url}, f)
            QMessageBox.information(self, "Sucesso", "Página inicial definida.")

    def mostrar_sobre(self):
        QMessageBox.information(self, "Sobre", "LuKe Browser Alfa7 - com bloqueio e menu de configurações.")

    #def ativar_modo_privado(self):
    #    self.modo_privado = True
    #    QMessageBox.information(self, "Modo Privado", "Modo privado ativado.")

    #def desativar_modo_privado(self):
    #    self.modo_privado = False
    #    QMessageBox.information(self, "Modo Privado", "Modo privado desativado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    navegador = LuKeBrowser()
    navegador.show()
    sys.exit(app.exec_())
