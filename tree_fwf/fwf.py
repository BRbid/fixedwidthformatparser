#coding:utf-8
import re
import datetime
from decimal import Decimal

class FixedWidthFormatParser(object):
    ## data com tamanho 6 no formato DDMMAA
    ## numerico com tamanho 5 e duas casas decimais 9(5)V9(2) saida de exemplo: 123,45
    ## numerico inteiro de tamanho 3 9(03) saida de exemplo 123
    ## string com tamanho 10 X(7) saida de exemplo "remessa"

    def __init__(self):
        self.caracter = 0
        self.dicionario_resultante = {}

    def _parse_leitura(self, leitura, configuracao):
        data = re.compile(r"[D|d]{2}[m|M]{2}[A|a]{2}$").match(configuracao)
        if data:
            leitura = leitura.strip()
            return leitura and datetime.datetime.strptime(leitura, '%d%m%y').date()
        string = re.compile(r"^[x|X]\((?P<string>\d+)\)$").match(configuracao)
        if string:
            return leitura.strip()
        decimal = re.compile(r"^9\((?P<inteiro>\d+)\)[v|V]9\((?P<decimal>\d+)\)$").match(configuracao)
        if decimal:
            qtd_casas = int(decimal.group('decimal'))
            return (Decimal(leitura) / 10 ** qtd_casas ).quantize(Decimal(str(10 ** -qtd_casas)))
        inteiro = re.compile(r"^9\((?P<inteiro>\d+)\)$").match(configuracao)
        if inteiro:
            return int(leitura)
        raise AttributeError('Configuracao errada! opcoes: 9(\d+), 9(\d+)v9(\d+), x(\d+), DDMMAA, tipo passado: %s' % configuracao)

    def _string_escrita(self, dicionario_dados, tupla_configuracao):
        chave, configuracao = tupla_configuracao
        dado = dicionario_dados.get(chave, '')
        limite = self._quantidade_de_caracteres_do_atributo(tupla_configuracao)
        if not isinstance(dado, datetime.date) and len(unicode(dado)) > limite:
            raise AttributeError(u'Atributo: %s, e maior do que deveria! valor: %s limite: %s' % (chave, unicode(dado), limite))
        inteiro = re.compile(r"^9\((?P<tamanho>\d+)\)$").match(configuracao)
        if inteiro:
            tamanho = str(inteiro.group('tamanho'))
            mascara = '%0' + tamanho + 'd'
            return mascara % int(dado and "".join(re.findall('[\d]+',str(dado))) or 0)

        decimal = re.compile(r"^9\((?P<inteiro>\d+)\)[v|V]9\((?P<decimal>\d+)\)$").match(configuracao)
        if decimal:
            dado = dado and re.sub('[,|.]', '', str(dado)) or ''
            tamanho = str(int(decimal.group('inteiro')) + int(decimal.group('decimal')))
            mascara = '%0' + tamanho + 'd'
            return mascara % int(dado or 0)

        string = re.compile(r"^[x|X]\((?P<tamanho>\d+)\)$").match(configuracao)
        if string:
            tamanho = int(string.group('tamanho'))
            if not isinstance(dado, (str, unicode)):
                dado = dado and str(dado) or ''
            return dado.ljust(tamanho)

        data = re.compile(r"[D|d]{2}[m|M]{2}[A|a]{2}$").match(configuracao)
        if data:
            return dado and dado.strftime('%d%m%y') or '000000'
        raise AttributeError('Configuracao errada! opcoes: 9(\d+), 9(\d+)v9(\d+), x(\d+), DDMMAA, tipo passado: %s' % configuracao)

    def _atualiza_dicionario(self, atributo, leitura):
        chave, configuracao = atributo
        if chave:
            self.dicionario_resultante[chave] = self._parse_leitura(leitura ,configuracao)

    def _ler_atributo(self,linha, configuracao):
        qtd_char = self._quantidade_de_caracteres_do_atributo(configuracao)
        leitura = linha[self.caracter : self.caracter + qtd_char]
        self.caracter += qtd_char
        return leitura

    def parse(self, dicionario):
        configuracao = dicionario['configuracao']
        linha = dicionario['linha']
        for atributo in configuracao:
            leitura = self._ler_atributo(linha, atributo)
            self._atualiza_dicionario(atributo, leitura)
        return self.dicionario_resultante

    def linha_para_escrita(self, dicionario, configuracao):
        linha = ''
        for config in configuracao:
            linha += self._string_escrita(dicionario, config)
        return linha + '\r\n'

    def _quantidade_de_caracteres_do_atributo(self, tupla_configuracao):
        configuracao = tupla_configuracao[1]
        data = re.compile(r"[D|d]{2}[m|M]{2}[A|a]{2}$").match(configuracao)
        if data:
            return 6
        decimal = re.compile(r"^9\((?P<inteiro>\d+)\)[v|V]9\((?P<decimal>\d+)\)$").match(configuracao)
        if decimal:
            return int(decimal.group('inteiro')) + int(decimal.group('decimal'))
        try:
            return int(re.sub('^.\(|\).*', '', configuracao ))
        except:
            raise AttributeError("Configuracao errada! configuracao: %s" % configuracao)

    def _verifica_tamanho_configuracao(self, configuracao, tamanho_linha):
        tamanhos = map(lambda atributo: self._quantidade_de_caracteres_do_atributo(atributo), configuracao)
        tamanho_total = sum(tamanhos)
        if tamanho_total == tamanho_linha:
            return True
        raise AttributeError('Tamanho da linha incorreto! tamanho da configuracao esperada: %s - : %s. tamanhos:%s' % (tamanho_total, tamanho_linha, tamanhos))

