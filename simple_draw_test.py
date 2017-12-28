import cv2
import numpy as np

from MoveDetect import Entidade, aglutinador

drawing = False # true if mouse is pressed
mode = True # if True, draw rectangle. Press 'm' to toggle to curve
ix,iy = -1,-1

def desenha_mais():

    def draw_circle(event,x,y,flags,param):
        global ix,iy,drawing,mode

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix,iy = x,y

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                if mode == True:
                    cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
                else:
                    cv2.circle(img,(x,y),5,(0,0,255),-1)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            if mode == True:
                cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
            else:
                cv2.circle(img,(x,y),5,(0,0,255),-1)

    img = np.zeros((512,512,3), np.uint8)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',draw_circle)

    while(1):
        cv2.imshow('image',img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('m'):
            mode = not mode
        elif k == 27:
            break

    cv2.destroyAllWindows()


def desenha_circulo():
    # mouse callback function
    def draw_circle(event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(img,(x,y),100,(255,0,0),-1)

    # Create a black image, a window and bind the function to window
    img = np.zeros((512,512,3), np.uint8)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',draw_circle)

    while(1):
        cv2.imshow('image',img)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    
    img = np.zeros((512,512,3), np.uint8)
    cv2.namedWindow('image')

    lista_geral = [ Entidade('Teste1', 10, 10, 20, 20, None), 
                    Entidade('Teste2', 20, 20, 50, 50, None),
                    Entidade('Teste3', 10, 100, 10, 10, None),
                    Entidade('Teste4', 20, 400, 10, 10, None),
                    Entidade('Teste5', 200, 400, 10, 10, None),
                    Entidade('Teste6', 100, 30, 20, 20, None),
                    Entidade('Teste7', 110, 15, 40, 40, None),
                    Entidade('Teste8', 300, 300, 100, 100, None),
                    Entidade('Teste9', 350, 290, 25, 25, None),
                    Entidade('Teste10', 400, 200, 30, 10, None),
                    Entidade('Teste11', 400, 450, 10, 20, None),
                    Entidade('Teste12', 440, 390, 12, 20, None)]

    ef = aglutinador(lista_geral)
    ef.cor_retangulo = (255, 255, 255)
    #d = e2.distancia(e3)

    # val = e2.is_colide(e3)
    # if val is True:
    #     e2.cor_retangulo = (255, 255, 255)

    #e1 = Entidade('Teste', 200, 100, 50, 50, None)
    #e1.size_texto = 0.5
    #e1.trick_retangulo = 1

    for e in lista_geral:
        e.draw_rectangle(img)
    
    ef.draw_rectangle(img)

    while(1):
        cv2.imshow('image',img)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    cv2.destroyAllWindows()