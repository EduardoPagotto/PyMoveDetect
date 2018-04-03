#!/usr/bin/env python3
'''
Created on 20180402
Update on 20180402
@author: Eduardo Pagotto
'''

#pylint: disable=C0301
#pylint: disable=C0103
#pylint: disable=W0703

import glob

# Importando o módulo Pillow para abrir a imagem no script
from PIL import Image, ImageEnhance #,ImageFilter

from tesserocr import PyTessBaseAPI, RIL, iterate_level
#import tesserocr

def filtro_adaptado(pathImagem):
    '''produc blur'''
    im = Image.open(pathImagem)

    size = im.size
    w = size[0]#size[0] * 3
    h = size[1]#size[1] * 3
    im = im.resize((w, h), Image.ADAPTIVE)

    #im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(1.25)#.show("30% more contrast")
    im = im.convert('1')
    im.save('tmp/big.tif', dpi=(75, 75))
    return 'tmp/big.tif'

def filtro_linhas(pathImagem):
    '''Filtra Linhas'''
    chop = 1

    image = Image.open(pathImagem)#.convert('1')
    #image = image.resize((256, 128), Image.NEAREST)

    width, height = image.size
    data = image.load()

    # Iterate through the rows.
    for y in range(height):
        for x in range(width):

            # Make sure we're on a dark pixel.
            if data[x, y] > 128:
                continue

            # Keep a total of non-white contiguous pixels.
            total = 0

            # Check a sequence ranging from x to image.width.
            for c in range(x, width):

                # If the pixel is dark, add it to the total.
                if data[c, y] < 128:
                    total += 1

                # If the pixel is light, stop the sequence.
                else:
                    break

            # If the total is less than the chop, replace everything with white.
            if total <= chop:
                for c in range(total):
                    data[x + c, y] = 255

            # Skip this sequence we just altered.
            x += total


    # Iterate through the columns.
    for x in range(width):
        for y in range(height):

            # Make sure we're on a dark pixel.
            if data[x, y] > 128:
                continue

            # Keep a total of non-white contiguous pixels.
            total = 0

            # Check a sequence ranging from y to image.height.
            for c in range(y, height):
                # If the pixel is dark, add it to the total.
                if data[x, c] < 128:
                    total += 1

                # If the pixel is light, stop the sequence.
                else:
                    break

            # If the total is less than the chop, replace everything with white.
            if total <= chop:
                for c in range(total):
                    data[x, y + c] = 255

            # Skip this sequence we just altered.
            y += total

    image.save('tmp/filtrada.jpeg', dpi=(200, 200))
    return 'tmp/filtrada.jpeg'

def reconhece(nomeArquivo):
    '''reconhece caracteres'''

    #return tesserocr.file_to_text(nomeArquivo)

    dados = ''
    # todos = ''

    imageDados = Image.open(nomeArquivo)

    w, h = imageDados.size

    slice_w = w / 4
    slice_w = slice_w * 4

    quartenario = [0, 0, slice_w, h]

    try:

        with PyTessBaseAPI() as api:
            api.SetImageFile(nomeArquivo)
            #api.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVXWYZabcdefghijklmnopqrstuvwxyz")
            api.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            api.SetVariable("save_blob_choices", "T")
            #api.SetVariable("tessedit_unrej_any_wd", True)
            api.SetRectangle(quartenario[0], quartenario[1], quartenario[2], quartenario[3])
            api.Recognize()

            ri = api.GetIterator()
            level = RIL.SYMBOL
            for r in iterate_level(ri, level):
                symbol = r.GetUTF8Text(level)
                if symbol:
                    dados = dados + symbol
                    #todos = todos +'[{0} : {1:2.2f}], '.format(symbol, conf)

                # ci = r.GetChoiceIterator()
                # for c in ci:
                #     choice = c.GetUTF8Text()
                #     todos = todos +'[{0} : {1:2.2f}], '.format(choice, c.Confidence())

                # todos = todos + '\n'


    except Exception as exp:
        raise exp

    return dados

def reconhecimento_ocr(arquivoJpeg):
    '''Reconhece arquivo e retorna seu valor'''
    bigFile = filtro_adaptado(arquivoJpeg)
    sem_limnha = filtro_linhas(bigFile)
    valor = reconhece(sem_limnha)

    if valor is '':
        return None
    elif len(valor) != 4:
        return None

    return valor
