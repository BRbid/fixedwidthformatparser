#coding:utf-8
import datetime

from fwf import FixedWidthFormatParser

class FWFDemo(FixedWidthFormatParser):

    def _config_header(self):
        return (
            (u'Tipo de Registro', '9(1)'),
            (u'Tipo de Arquivo','x(12)'),
            (u'Inscrição do Prestador','9(8)'),
            (u'Versão do Arquivo','9(3)'),
            (u'Data do Arquivo','AAAAMMDD'),
        )

    def _config_linhas(self):
        return (
            (u'Tipo de Registro', '9(1)'),
            (u'Identificador Sistema legado', 'x(12)'),
            (u'Tipo de Codificação', '9(1)'),
            (u'Código do Serviço', '9(7)'),
            (u'Situação da Nota Fiscal', 'x(1)'),
            (u'Valor dos Serviços', '9(13)v9(2)'),
            (u'Valor da base de calculo', '9(13)v9(2)'),
            (u'CPF/CNPJ do tomador', '9(15)'),
            (u'Inscrição municipal do tomador', '9(8)'),
            (u'Inscrição estadual do tomador', '9(8)'),
            (u'Nome/Razão Social do tomador', 'x(100)'),
            (u'Endereço do Tomador', 'x(50)'),
            (u'Número do endereço', 'x(10)'),
            (u'Complemento do Endereço', 'x(30)'),
            (u'Bairro do Tomador', 'x(30)'),
            (u'Cidade do Tomador', 'x(50)'),
            (u'Unidade Federal do Tomador', 'x(2)'),
            (u'CEP do Tomador', '9(8)'),
            (u'E-mail do Tomador', 'x(100)'),
            (u'Discriminação dos serviços', 'x(1000)'),
        )

    def _config_footer(self):
        return (
            (u'Tipo de Registro', '9(1)'),
            (u'Número de Linhas detalhe', '9(10)'),
            (u'Valor Total dos serviços contidos no arquivo', '9(13)v9(2)'),
            (u'Valor total do valor base contido no arquivo', '9(13)v9(2)'),
        )

    def _dicionario_para_header(self, inscricao_municipal):

        hoje = datetime.date.today().strftime('%Y%m%d')

        dicionario = {
            u'Tipo de Registro': 1,
            u'Tipo de Arquivo': 'NFE_LOTE',
            u'Inscrição do Prestador': inscricao_municipal,
            u'Versão do Arquivo': '010',
            u'Data do Arquivo': hoje,
        }

        return dicionario

    def _dicionario_para_linha(self):

        dicionario = {
            u'Tipo de Registro': 2,
            u'Identificador Sistema legado': 'x(12)',   # verificar
            u'Tipo de Codificação': '9(1)',             # verificar
            u'Código do Serviço': '9(7)',               # verificar
            u'Situação da Nota Fiscal': 'T',            # Tributada, eu acho
            u'Valor dos Serviços': '9(13)v9(2)',        # pegar no sistema
            u'Valor da base de calculo': '9(13)v9(2)',  # pegar no sistema
            u'CPF/CNPJ do tomador': '9(15)',            # pegar no sistema
            u'Inscrição municipal do tomador': '9(8)',  # opcional / adicionar ao sistema
            u'Inscrição estadual do tomador': '9(8)',   # opcional / adicionar ao sistema
            u'Nome/Razão Social do tomador': 'x(100)',  # pegar no sistema
            u'Endereço do Tomador': 'x(50)',            # adicionar no sistema
            u'Número do endereço': 'x(10)',             # adicionar no sistema
            u'Complemento do Endereço': 'x(30)',        # adicionar no sistema
            u'Bairro do Tomador': 'x(30)',              # adicionar no sistema
            u'Cidade do Tomador': 'x(50)',              # adicionar no sistema
            u'Unidade Federal do Tomador': 'x(2)',      # adicionar no sistema
            u'CEP do Tomador': '9(8)',                  # adicionar no sistema
            u'E-mail do Tomador': 'x(100)',             # adicionar no sistema
            u'Discriminação dos serviços': 'x(1000)',   # pegar no sistema
        }

        return dicionario

    
    def _dicionario_footer(self):

        dicionario = {
            u'Tipo de Registro': 9,
            u'Número de Linhas detalhe': '9(10)',       # somar linhas geradas para corpo
            u'Valor Total dos serviços contidos no arquivo': '9(15)',   # calcular
            u'Valor total do valor base contido no arquivo': '9(15)',   # calcular
        }

        return dicionario

    def linha_para_footer(self):
        configuracoes = self._config_footer()
        dicionario = self._dicionario_footer()
        return self.linha_para_escrita(dicionario, configuracoes)

    def linha_para_header(self):
        configuracoes = self._config_header()
        dicionario = self._dicionario_header()
        return self.linha_para_escrita(dicionario, configuracoes)

    def linha_para_documento(self):
        configuracoes = self._config_linhas()
        dicionario = self._dicionario_para_linha()
        return self.linha_para_escrita(dicionario, configuracoes)

    def remessa(self, queryset):
        
        dados = unicode()

        cnab += self.linha_para_header()

        for dado in queryset:
            cnab += self.linha_para_documento(dad)

        cnab += self.linha_para_footer()
        return cnab


