##################################################################################################################
#
# Copyright (C) 2014 KTec S.r.l.
#
# Author: Luigi Di Naro: Luigi.DiNaro@KTec.it
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################################################


import datetime
from utils import piva

lxml = False

try:
    import lxml.etree as etree
    lxml = True
except ImportError:
    import xml.etree.ElementTree as etree

TP = ('AC', 'AD', 'AM', 'CC', 'CD', 'OA', 'VC', 'VP')

EP = ('F','T','C','P')

RG = ('M8P', 'M9P', 'M10P', 'M11P', 'M12P', 'M13P', 'M14P', 'M15P', 'NOTI', 'NOTIB', 'M22P',
      'M35P', 'M36P', 'M37P', 'M38P', 'M39P', 'M40P', 'M42P', 'IGN', 'M45P','M46P',
      'M52P', 'M53P', 'M54P', 'MAIP')

TI = ('A', 'B', 'C', 'I', 'D', 'T', 'M', 'N')


class ValidateException(Exception):
    pass


def validateprot(value):

    try:
        if len(value) <= 11 and len(value.split('/')) == 2 \
                and value.split('/')[0].isdigit() \
                and value.split('/')[1].isdigit():
            return True
    except:
        return False
    return False


def is_number(s):
    try:
        float(s)
        return True
    except:
        return False


def validate(value):

    err = ''

    if 'beneficiario' not in value or not piva(value['beneficiario']):
        err = err + 'Volore errato per beneficiario '
    elif 'tipopagamento' not in value or value['tipopagamento'] not in TP:
        err = err + 'Volore errato per tipopagamento '
    elif 'entepagante' not in value or value['entepagante'] not in EP:
        err = err + 'Volore errato per entepagante '
    elif 'numerofattura' not in value or value['numerofattura'] is None:
        err = err + 'Volore errato per numerofattura '
    elif 'numeromodello37' in value and value['numeromodello37'] is not None \
            and not (validateprot(value['numeromodello37']) or len(value['numeromodello37']) == 0):
        err = err + 'Volore errato per numeromodello37 '
    elif 'registro' in value and not value['registro'] in RG:
        err = err + 'Volore errato per registro '
    elif 'datafattura' not in value or not isinstance(value['datafattura'], datetime.datetime):
        err = err + 'Volore errato per datafattura '
    elif 'importototale' not in value or not is_number(value['importototale']):
        err = err + 'Volore errato per importototale '
    elif 'importoiva' not in value or not is_number(value['importoiva']):
        err = err + 'Volore errato per importoiva '
    elif 'nr_rg' in value and value['nr_rg'] is not None and not \
            (validateprot(value['nr_rg']) or len(value['nr_rg']) == 0):
        err = err + 'Volore errato per nr_rg '
    elif 'sede' not in value or value['sede'] is None:
        err = err + 'Volore errato per sede '
    elif 'datainizioprestazione' not in value or not isinstance(value['datainizioprestazione'], datetime.datetime):
        err = err + 'Volore errato per datainizioprestazione '
    elif 'datafineprestazione' not in value or not isinstance(value['datafineprestazione'], datetime.datetime):
        err = err + 'Volore errato per datafineprestazione '
    elif 'cognomemagistrato' not in value or value['cognomemagistrato'] is None:
        err = err + 'Volore errato per cognomemagistrato '
    elif 'nomemagistrato' not in value or value['nomemagistrato'] is None:
        err = err + 'Volore errato per nomemagistrato '
    elif 'tipointercettazione' not in value or not value['tipointercettazione'] in TI:
        err = err + 'Volore errato per tipointercettazione'

    if err != '':
        raise ValidateException(err)


def serialize(value):

    validate(value)

    NSMAP = {'od': 'urn:schemas-microsoft-com:officedata',
             'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

    #: lxml and ElementTree support, different namespace definition
    #: try find better solution

    if lxml:
        siammxml = etree.Element('dataroot', nsmap = NSMAP)
        siammxml.set('{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation','Intercettazioni.xsd')
    else:
        siammxml = etree.Element('dataroot')
        siammxml.set('xmlns:od', 'urn:schemas-microsoft-com:officedata')
        siammxml.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        siammxml.set('xsi:noNamespaceSchemaLocation', 'Intercettazioni.xsd')

    intercettazioni = etree.Element('Intercettazioni')
    (etree.SubElement(intercettazioni, 'ID')).text = str(value['id']) if 'id' in value else '1'
    (etree.SubElement(intercettazioni, 'Beneficiario')).text = value['beneficiario'].strip('IT')
    (etree.SubElement(intercettazioni, 'TipoPagamento')).text = value['tipopagamento']
    (etree.SubElement(intercettazioni, 'EntePagante')).text = value['entepagante']
    (etree.SubElement(intercettazioni, 'NumeroFattura')).text = value['numerofattura']
    (etree.SubElement(intercettazioni, 'DataEmissioneProvv')).text = ''
    (etree.SubElement(intercettazioni, 'NumeroModello37')).text = \
        value['numeromodello37'] if 'numeromodello37' in value else None
    (etree.SubElement(intercettazioni, 'Registro')).text = value['registro']
    (etree.SubElement(intercettazioni, 'DataFattura')).text = \
        "{:%Y-%m-%dT%H:%M:%S}".format(value['datafattura'])
    (etree.SubElement(intercettazioni, 'ImportoTotale')).text = \
        '{:.2f}'.format(float(value['importototale']))
    (etree.SubElement(intercettazioni, 'ImportoIVA')).text = \
        '{:.2f}'.format(float(value['importoiva']))
    (etree.SubElement(intercettazioni, 'NR_RG')).text = value['nr_rg'] if 'nr_rg' in value else None
    (etree.SubElement(intercettazioni, 'Sede')).text = value['sede']
    (etree.SubElement(intercettazioni, 'DataInizioPrestazione')).text = \
        "{:%Y-%m-%dT%H:%M:%S}".format(value['datainizioprestazione'])
    (etree.SubElement(intercettazioni, 'DataFinePrestazione')).text = \
        "{:%Y-%m-%dT%H:%M:%S}".format(value['datafineprestazione'])
    (etree.SubElement(intercettazioni, 'CognomeMagistrato')).text = value['cognomemagistrato']
    (etree.SubElement(intercettazioni, 'NomeMagistrato')).text = value['nomemagistrato']
    (etree.SubElement(intercettazioni, 'TipoIntercettazione')).text = value['tipointercettazione']

    siammxml.append(intercettazioni)

    if lxml:
        return etree.tostring(siammxml, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    else:
        return etree.tostring(siammxml, encoding='UTF-8')