#import RPi.GPIO as GPIO
import cv2
import math
import pytesseract
#import baseDados
import time
try:
    from PIL import Image
except ImportError:
    import Image

MIN_PIXEL_LARGURA = 2
MIN_PIXEL_ALTURA = 8

MIN_ASPECT_RATIO = 0.25
MAX_ASPECT_RATIO = 1.0

MIN_PIXEL_AREA = 80
MAX_PIXEL_AREA = 1000

MIN_DIAG_SIZE = 0.3
MAX_DIAG_SIZE = 5.0

MAX_AREA = 0.5

MAX_LARGURA = 0.8
MAX_ALTURA = 0.2

MAX_ANGULO = 12.0

MIN_NUMERO = 3

ESCALA_AMARELO = (0.0, 255.0, 255.0)

PLACA_LARGURA_FATOR_PREENCHIMENTO = 1.05
PLACA_ALTURA_FATOR_PREENCHIMENTO = 1.05

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(26, GPIO.OUT)

class PossivelPlaca:

    # construtor #################################################################################
    def __init__(self):
        self.imgPlaca = None
        self.imgEscalaDeCinza = None
        self.imgThreshold = None
        self.X = None
        self.Y = None
        self.W = None
        self.H = None
        self.strCaracteres = ""
    # end construtor

# end class

class PossivelCaractere:

    # construtor #################################################################################
    def __init__(self, _contour):
        self.contour = _contour

        self.boundingRect = cv2.boundingRect(self.contour)

        [intX, intY, intWidth, intHeight] = self.boundingRect

        self.intBoundingRectX = intX
        self.intBoundingRectY = intY
        self.intBoundingRectWidth = intWidth
        self.intBoundingRectHeight = intHeight

        self.intBoundingRectArea = self.intBoundingRectWidth * self.intBoundingRectHeight

        self.intCenterX = (self.intBoundingRectX + self.intBoundingRectX + self.intBoundingRectWidth) / 2
        self.intCenterY = (self.intBoundingRectY + self.intBoundingRectY + self.intBoundingRectHeight) / 2

        self.fltDiagonalSize = math.sqrt((self.intBoundingRectWidth ** 2) + (self.intBoundingRectHeight ** 2))

        self.fltAspectRatio = float(self.intBoundingRectWidth) / float(self.intBoundingRectHeight)
    # end construtor

# end class

def combinarCharacter(list):

    newList = []
    finalList = []

    for char in list:
        for otherChar in list:
            if char == otherChar:
                continue

            fltDistancia = distancia(char, otherChar)

            fltAngulo = angulo(char, otherChar)

            fltChangeInArea = float(abs(char.intBoundingRectArea - otherChar.intBoundingRectArea)) / float(char.intBoundingRectArea)

            fltChangeInWidth = float(abs(char.intBoundingRectWidth - otherChar.intBoundingRectWidth)) / float(char.intBoundingRectWidth)

            fltChangeInHeight = float(abs(char.intBoundingRectHeight - otherChar.intBoundingRectHeight)) / float(char.intBoundingRectHeight)

            if (fltDistancia < (char.fltDiagonalSize * MAX_DIAG_SIZE) and fltAngulo < MAX_ANGULO and fltChangeInArea < MAX_AREA and
               fltChangeInWidth < MAX_LARGURA and fltChangeInHeight < MAX_ALTURA):
                newList.append(otherChar)
                newList.append(char)
            # end if
        # end for
        if len(newList) < MIN_NUMERO:
            newList = []
            continue
        # end if
        finalList.append(newList)

    return finalList

def distancia(first, second):
    intX = abs(first.intCenterX - second.intCenterX)
    intY = abs(first.intCenterY - second.intCenterY)

    return math.sqrt((intX ** 2) + (intY ** 2))
###################################################################################################
def angulo(first, second):
    fltAdj = float(abs(first.intCenterX - second.intCenterX))
    fltOpp = float(abs(first.intCenterY - second.intCenterY))

    if fltAdj != 0.0:
        fltAngleInRad = math.atan(fltOpp / fltAdj)
    else:
        fltAngleInRad = 1.5708
    # end if
    fltAngleInDeg = fltAngleInRad * (180.0 / math.pi)

    return fltAngleInDeg

def escreverCaracteresDaPlacaNaImagem(imgCenaOriginal, licPlaca):
    ptCenterOfTextAreaX = 0
    # este será o centro da área o texto será escrito para
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0
    # este será o canto inferior esquerdo da área que o texto será escrito para
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgCenaOriginal.shape
    PlacaHeight, PlacaWidth, PlacaNumChannels = licPlaca.imgPlaca.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX
    # escolher uma fonte para os caracteres
    fltFontScale = float(PlacaHeight) / 60.0
    # escala fonte base na altura da área da placa
    intFontThickness = int(round(fltFontScale * 0.5))
    # espessura da fonte base na escala de fonte

    textSize, baseline = cv2.getTextSize(licPlaca.strCaracteres, intFontFace, fltFontScale, intFontThickness)
    # chamar setTextSize

    # descompactar retângulo girado em ponto central, Largura e altura e ângulo
    ((intPlacaCenterX, intPlacaCenterY), (intPlacaWidth, intPlacaHeight),
     fltCorrectionAngleInDeg) = licPlaca.rrLocationOfPlacaInScene

    intPlacaCenterX = int(intPlacaCenterX)
    # certifique-se o centro é um inteiro
    intPlacaCenterY = int(intPlacaCenterY)

    ptCenterOfTextAreaX = int(intPlacaCenterX)
    # a localização horizontal da área de texto é o mesmo que a Placa

    if intPlacaCenterY < (sceneHeight * 0.75):
        # se a placa é na parte superior 3/4(tambem conhecido como 0,75) da imagem
        ptCenterOfTextAreaY = int(round(intPlacaCenterY)) + int(round(PlacaHeight * 1.6))
        # escrever os caracteres em baixo da Placa
    else:
        # senão se a placa é na parte inferior 1/4(tambem conhecido como 0,25) da imagem
        ptCenterOfTextAreaY = int(round(intPlacaCenterY)) - int(round(PlacaHeight * 1.6))
        # escrever os caracteres em cima da Placa
    # end if

    textSizeWidth, textSizeHeight = textSize
    # tamanho do texto descompactar Largura e altura

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))
    # calcular a origem inferior esquerda da área de texto
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))
    # com base no centro textarea, Largura, e Altura

    # escreva o texto na imagem
    cv2.putText(imgCenaOriginal, licPlaca.strCaracteres, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace,
                fltFontScale, ESCALA_AMARELO, intFontThickness)


# end function

###########################################################

def extrairPlaca(imgOriginal, listChar):
    possivelPlaca = PossivelPlaca()           # este será o valor de retorno

    listChar.sort(key = lambda matchingChar: matchingChar.intCenterX)
    # tipo caracteres da esquerda para a direita com base na posição x

    # calcular o ponto central da Placa
    fltPlacaCenterX = (listChar[0].intCenterX + listChar[len(listChar) - 1].intCenterX) / 2.0
    fltPlacaCenterY = (listChar[0].intCenterY + listChar[len(listChar) - 1].intCenterY) / 2.0

    ptPlacaCenter = fltPlacaCenterX, fltPlacaCenterY

    # calcular Largura e altura da Placa
    intPlacaWidth = int((listChar[len(listChar) - 1].intBoundingRectX + listChar[len(listChar) - 1].intBoundingRectWidth - listChar[0].intBoundingRectX) * PLACA_LARGURA_FATOR_PREENCHIMENTO)

    intTotalOfCaractereHeights = 0

    for matchingCaractere in listChar:
        intTotalOfCaractereHeights = intTotalOfCaractereHeights + matchingCaractere.intBoundingRectHeight
    # end for

    fltAverageCaractereHeight = intTotalOfCaractereHeights / len(listChar)

    intPlacaHeight = int(fltAverageCaractereHeight * PLACA_ALTURA_FATOR_PREENCHIMENTO)

    # calcular o ângulo de correção da região Placa
    fltOpposite = listChar[len(listChar) - 1].intCenterY - listChar[0].intCenterY
    fltHypotenuse = distancia(listChar[0], listChar[len(listChar) - 1])
    fltCorrectionAngleInRad = math.asin(fltOpposite / fltHypotenuse)
    fltCorrectionAngleInDeg = fltCorrectionAngleInRad * (180.0 / math.pi)
    # ponto central da região, Largura e altura e ângulo de correção da variável em rotação de retângulo de Placa
    possivelPlaca.rrLocationOfPlacaInScene = ( tuple(ptPlacaCenter), (intPlacaWidth, intPlacaHeight), fltCorrectionAngleInDeg )

    # passos finais são para realizar a rotação real

    # obter a matriz de rotação para o nosso ângulo de correção calculado
    rotationMatrix = cv2.getRotationMatrix2D(tuple(ptPlacaCenter), fltCorrectionAngleInDeg, 1.0)

    altura, largura, _ = imgOriginal.shape      # descompactar imagem original Largura e altura

    imgRotated = cv2.warpAffine(imgOriginal, rotationMatrix, (largura, altura))       # girar a imagem inteira

    imgCropped = cv2.getRectSubPix(imgRotated, (intPlacaWidth, intPlacaHeight), tuple(ptPlacaCenter))

    possivelPlaca.imgPlaca = imgCropped         # copiar a imagem Placa cortada na variável membro aplicável à possível Placa
    possivelPlaca.X = int(listChar[0].intBoundingRectX)
    possivelPlaca.Y = int(listChar[0].intBoundingRectY)
    possivelPlaca.W = int(intPlacaWidth)
    possivelPlaca.H = int(intPlacaHeight)

    return possivelPlaca
# end function


def mostraPlaca(str):
    return trocaCaracteres(str.replace(' ', '').replace("-",""))

def trocaCaracteres(str):
    return str[:3] + str[3:].replace("I", "1").replace("S", "5").replace("L","1").replace("J","1").replace("B","8")

def abrirPortao(txt):
    print("Abrindo portão para a placa: " + txt + ".")
#    GPIO.output(26, GPIO.HIGH)
#    sleep(0.2)
#    GPIO.output(26, GPIO.LOW)
    return True


#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("/home/vinicius/git/placas/imagens/frente-noite-02.mp4")
i = 1

while (1):
    _, img_original = cap.read()

    if img_original is None:
        continue

    if i % 1 == 0:
        i = 1
        h = int(img_original.shape[0] / 1.8)
        w = int(img_original.shape[1] / 1.8)
        y = int(img_original.shape[0] / 3)
        x = int(img_original.shape[1] / 3)
        crop_img = img_original #[y:y + h, x:x + w]
        #scale_percent = 100  # percent of original size
        #width = crop_img.shape[1] + int(crop_img.shape[1] * scale_percent / 100)
        #height = crop_img.shape[0] + int(crop_img.shape[0] * scale_percent / 100)
        #dim = (width, height)
        # resize image

        img = crop_img.copy()
    #    img[:, :, 0] = 0 # zerando o canal R (RED)
    #    img[:, :, 2] = 0 # zerando o canal B (BLUE)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _, _, imgValue = cv2.split(imgHSV)

        structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        img_gray = cv2.subtract(cv2.add(imgValue, cv2.morphologyEx(imgValue, cv2.MORPH_TOPHAT, structuringElement)), cv2.morphologyEx(imgValue, cv2.MORPH_BLACKHAT, structuringElement))

        imgThreshold = cv2.adaptiveThreshold(cv2.GaussianBlur(img_gray, (3, 3), 0), 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)

        #imgThreshold = cv2.resize(imgThreshold, dim, interpolation=cv2.INTER_LINEAR_EXACT)
        imgNormal = img #cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR_EXACT)
        img_copia = imgThreshold.copy()

        conts, _ = cv2.findContours(img_copia, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        listaCaracteres = []
        for cnt in conts:
            area = cv2.contourArea(cnt)
            x,y,w,h = cv2.boundingRect(cnt)
            fltAspectRatio = float(w) / float(h)
            possivelCaractere = PossivelCaractere(cnt)

            if (area > MIN_PIXEL_AREA  and area < MAX_PIXEL_AREA
                    and w > MIN_PIXEL_LARGURA and h > MIN_PIXEL_ALTURA and
                    MIN_ASPECT_RATIO < fltAspectRatio and fltAspectRatio < MAX_ASPECT_RATIO):
                listaCaracteres.append(possivelCaractere)
            # end if

        listaCombinada =  combinarCharacter(listaCaracteres)
        list = []

        for listChar in listaCombinada:
            possivelPlaca = extrairPlaca(img, listChar)

            if possivelPlaca.imgPlaca is not None and possivelPlaca.W < 30 :
                list.append(possivelPlaca)
            # end if
        # end for
        #list.sort(key=lambda possivelPlaca: len(possivelPlaca.strCaracteres), reverse=True)
        if len(list) > 0:
            licPlaca = list[0]

            h = licPlaca.H
            w = licPlaca.W
            y = licPlaca.Y
            x = licPlaca.X
            crop_img = imgThreshold[y:y + h, x:x + w]

            cv2.rectangle(imgNormal, (licPlaca.X, licPlaca.Y), (licPlaca.X+licPlaca.W, licPlaca.Y+licPlaca.H), (0, 0, 255), 3)

            txt = pytesseract.image_to_string(Image.fromarray(crop_img), lang='eng', config='--psm 10  --oem 3 -c tessedit_char_whitelist=1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            licPlaca.strCaracteres = mostraPlaca(txt)
            escreverCaracteresDaPlacaNaImagem(imgNormal, licPlaca)
            print("Original:" + txt + " - Identificado:" + licPlaca.strCaracteres)
            cv2.imwrite('/var/log/placas/' + licPlaca.strCaracteres + "_original.png", img_original)
            cv2.imwrite('/var/log/placas/' + licPlaca.strCaracteres + "_placa.png", crop_img)
            #if baseDados.existePlaca(licPlaca.strCaracteres):
            #    abrirPortao(licPlaca.strCaracteres)
            #    cap.release()
            #    time.sleep(30)
            #    cap = cv2.VideoCapture(0)
        cv2.imshow("Cam", imgNormal)
        cv2.imshow("Cam2", imgThreshold)
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
        # end if
    i += 1
    #end if
#end while
#baseDados.closeConnection()
cap.release()
#cv2.destroyAllWindows()
