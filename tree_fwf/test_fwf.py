#coding:utf-8
import re
import datetime 
from decimal import Decimal

from unittest import TestCase
from mock import patch

from fwf import FixedWidthFormatParser

class FixedWidthFormatTest(TestCase):

    def setUp(self):

        self.linha = '02RETORNO01COBRANCA       073000035110        PLUTO ALTO ELENTAS LTDA ME    341BANCO ITAU S.A.20051301600BPI00025210513                                                                                                                                                                                                                                                                                   000001'
        self.configuracao = [
            (u'Tipo de registro' , '9(01)'),
            (u'OperaÃ§Ã£o' , '9(01)'),
            (u'Literal de remessa' , 'X(07)'),
            (u'Codigo do servico' , '9(02)' ),
            (u'Literal de servico' , 'X(15)'),
            (u'Agencia' , '9(04)'),
            (None , '9(02)'),
            (u'Conta' , '9(05)'),
            (u'DAC' , '9(01)'),
            (None , 'X(08)'),
            (u'Nome da empresa' , 'X(30)'),
            (u'CÃ³digo do banco' , '9(03)'),
            (u'Nome do banco' , 'X(15)'),
            (u'Data de geraÃ§Ã£o' , 'X(06)'),
            (None , 'X(294)'),
            (u'NÃºmero sequencial' , '9(06)')
        ]

        self.manager = FixedWidthFormatParser()


    def test_init_deve_iniciar_dicionario_resultante(self):
        self.assertEquals(self.manager.dicionario_resultante, {})

    def test_init_deve_iniciar_caracter(self):
        self.assertEquals(self.manager.caracter, 0)

    def test_ler_atributo_deve_ler_dados_da_linha_e_incrementar_caracter(self):
        resposta = self.manager._ler_atributo(self.linha, ('tipo_de_registro' , '9(01)'))
        esperado = '0'
        self.assertEquals(resposta, esperado)

    def teste_parse_leitura_deve_retornar_date(self):
        resposta_lower = self.manager._parse_leitura('011120', 'ddmmaa')
        resposta_upper = self.manager._parse_leitura('011120', 'DDMMAA')
        esperado = datetime.date(day=1,month=11, year=2020)
        self.assertEquals(resposta_lower, esperado)
        self.assertEquals(resposta_upper, esperado)

    def test_parse_leitura_deve_retornar_string_sem_espacos(self):
        resposta_lower = self.manager._parse_leitura('parse da leitura        ', 'x(24)')
        resposta_upper = self.manager._parse_leitura('parse da leitura        ', 'X(24)')
        esperado = 'parse da leitura'
        self.assertEquals(resposta_lower, esperado)
        self.assertEquals(resposta_upper, esperado)

    def test_atualiza_dicionario_deve_atualizar_dicionario_de_forma_correta(self):
        self.manager._atualiza_dicionario((u'Tipo de registro' , '9(01)'), '0')
        self.assertEquals(self.manager.dicionario_resultante, {u'Tipo de registro' : Decimal(0)})

    def test_parse_leitura_deve_retornar_decimal_com_quantidade_de_casas_corretas(self):
        resposta_lower = self.manager._parse_leitura('1234567890', '9(10)v9(2)')
        resposta_upper = self.manager._parse_leitura('1234567890', '9(10)V9(2)')
        esperado = Decimal('12345678.90') 
        self.assertEquals(resposta_lower, esperado)
        self.assertEquals(resposta_upper, esperado)

    def test_parse_leitura_deve_retornar_inteiro_como_decimal(self):
        resposta = self.manager._parse_leitura('123456', '9(6)')
        esperado = Decimal(123456)
        self.assertEquals(resposta, esperado)

    def test_parse_leitura_deve_levantar_erro_com_configuracao_errada(self):
        with self.assertRaisesRegexp(AttributeError, r"Configuracao errada! opcoes: "):
            self.manager._parse_leitura('1234', 'configuracao inexistente')

    def test_quantidade_de_caracteres_do_atributo_deve_retornar_valor_correto_para_data_format_DDMMAA(self):
        resposta = self.manager._quantidade_de_caracteres_do_atributo(('teste' , 'DDMMAA'))
        esperado = 6
        self.assertEquals(resposta,esperado)

    def test_quantidade_de_caracteres_do_atributo_deve_retornar_valor_correto_para_data_format_AAAAMMDD(self):
        resposta = self.manager._quantidade_de_caracteres_do_atributo(('teste' , 'AAAAMMDD'))
        esperado = 8
        self.assertEquals(resposta,esperado)


    def test_quantidade_de_caracteres_do_atributo_deve_retornar_valor_correto(self):
        resposta = self.manager._quantidade_de_caracteres_do_atributo(('teste' , 'X(05)'))
        esperado = 5
        self.assertEquals(resposta, esperado)

    def test_quantidade_de_caracteres_do_atributo_deve_somar_decimais(self):
        resposta = self.manager._quantidade_de_caracteres_do_atributo(('teste' , '9(5)V9(2)'))
        esperado = 7 
        self.assertEquals(resposta, esperado)

    def test_verifica_tamanho_configuracao(self):
        """
        validar_tamanho_configuracao deve verificar
        se a soma das configuraÃ§Ãµes esta correta,
        se nÃ£o estiver vai levantar erro.
        """
        del self.configuracao[0]
        with self.assertRaisesRegexp(AttributeError, "Tamanho da linha incorreto! tamanho da configuracao esperada: 399 - : 400. tamanhos:\[1, 7, 2, 15, 4, 2, 5, 1, 8, 30, 3, 15, 6, 294, 6\]"):
            self.manager._verifica_tamanho_configuracao(self.configuracao, 400)

    def test_verifica_tamanho_configuracao_deve_retornar_true_se_estiver_correto(self):
        resposta = self.manager._verifica_tamanho_configuracao(self.configuracao, 400)
        esperado = True
        self.assertEquals(resposta, esperado)

    def test_linha_para_escrita_deve_retornar_string_correta(self):
        resposta = self.manager.linha_para_escrita({
            'inteiro' : 10,
            'data' : datetime.date(day=1, month=2, year=2003),
            'string' : 'teste',
            'decimal' : Decimal('101.22'),
        },[
            ('inteiro', '9(200)'),
            ('data' , 'DDMMAA'),
            ('string' , 'x(94)'),
            ('decimal' , '9(98)v9(2)'),
        ])
        esperado = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010010203teste                                                                                         0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010122\r\n' 
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_levantar_erro_com_configuracao_errada(self):
        with self.assertRaisesRegexp(AttributeError, "Configuracao errada!"):
            self.manager._string_escrita({'teste': 1}, ('teste', 'xyz'))

    def test_string_escrita_deve_retornar_string_correta_para_inteiro_sem_o_dado(self):
        resposta = self.manager._string_escrita({}, ('None', '9(10)'))
        esperado = '0000000000'
        self.assertEquals(len(resposta), 10)
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_retornar_string_correta_para_inteiro(self):
        resposta = self.manager._string_escrita({'teste' : 100}, ('teste', '9(10)'))
        esperado = '0000000100'
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_retornar_string_correta_para_decimal(self):
        resposta = self.manager._string_escrita({'teste' : Decimal('10.25')}, ('teste', '9(10)v9(2)'))
        esperado = '000000001025'
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_retornar_data_correta_para_string_format_DDMMAA(self):
        resposta = self.manager._string_escrita({'teste' : datetime.date(day=1, month=2, year=2012)}, ('teste', 'DDMMAA'))
        esperado = '010212'
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_retornar_data_correta_para_string_format_AAAAMMDD(self):
        resposta = self.manager._string_escrita({'teste' : datetime.date(day=1, month=2, year=2012)}, ('teste', 'AAAAMMDD'))
        esperado = '20120201'
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_retornar_string_correta_para_string_sem_valor(self):
        resposta = self.manager._string_escrita({}, ('teste', 'x(20)'))
        esperado = '                    '
        self.assertEquals(len(resposta), 20) 
        self.assertEquals(resposta, esperado)

    def test_string_escrita_deve_retornar_string_correta_para_string(self):
        # FIX: Apaguei um espaço em branco do esperado. Verificar com o andre se é isso mesmo.
        resposta = self.manager._string_escrita({'teste' : 'Murilo chaves'}, ('teste', 'x(19)'))
        esperado = 'Murilo chaves      '
        self.assertEquals(resposta, esperado)

    def test_parse_deve_retornar_dicionario_correto(self):
        resposta = self.manager.parse({
            'tamanho_linha' : 400,
            'linha' : self.linha,
            'configuracao' : self.configuracao,
        })
        esperado = {
            u'Agencia': Decimal('730'),
            u'Codigo do servico': Decimal('1'),
            u'Conta': Decimal('3511'),
            u'CÃ³digo do banco': Decimal('341'),
            u'DAC': Decimal('0'),
            u'Data de geraÃ§Ã£o': '200513',
            u'Literal de remessa': 'RETORNO',
            u'Literal de servico': 'COBRANCA',
            u'Nome da empresa': 'PLUTO ALTO ELENTAS LTDA ME',
            u'Nome do banco': 'BANCO ITAU S.A.',
            u'NÃºmero sequencial': Decimal('1'),
            u'OperaÃ§Ã£o': Decimal('2'),
            u'Tipo de registro': Decimal('0')
        }
        self.assertEquals(resposta, esperado)
