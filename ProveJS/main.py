import json

from django.http import JsonResponse, HttpResponse
from collections import defaultdict

# import requests

import cv2
import numpy as np
import yaml
import urllib.request


# from .coordinates_generatorTEST import *
from colors import *


# Create your views here.

def get_image(nomeImg):
    image_data = open(nomeImg, "rb").read()
    return HttpResponse(image_data, content_type="image/png")


def getFrame(linkRtsp):
    # Opens the Video file
	cap = cv2.VideoCapture(linkRtsp)
	i = 0

	ret, frame = cap.read()

	cv2.imwrite('ima.png', frame)

	cap.release()
	return "ima.png"



# def avvio_mappatura(nomeYml, imagePng):
# 	data_file = nomeYml
#
# 	with open(data_file, "w+") as points:
# 		generator = CoordinatesGenerator(imagePng, points, COLOR_RED)
# 		generator.generate()
#
# 	with open(data_file, 'r') as stream:
# 		parking_data = yaml.safe_load(stream)
#
# 	return parking_data


def avvio_detection(imaaa):
    # Load Yolo
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    tonyStr=""
    # Loading image
    #imaaa = getFrame(linkRtsp)
    img = cv2.imread('ima2.png')
    assert not isinstance(img, type(None)), 'image not found'

    # img = cv2.imread(linkRtsp)
    # img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []

    array = []
    cont=0

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)

                w = int(detection[2] * width)
                h = int(detection[3] * height)


                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)


                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # print(array)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    # print(indexes)
    font = cv2.FONT_ITALIC

    spot = 0
    veicoli=[]

    for i in range(len(boxes)):
        if i in indexes:
            spot += 1
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[class_ids[i]]

            xmax=x + w
            ymax=y + h

            altezza = ymax - y

            larghezza = xmax - x

            nuovo_y = y + (altezza / 2)
            nuovo_x = x + (larghezza / 2)

            # print(x)
            # print(y)
            # print(xmax)
            # print(ymax)
            # print("/////////////////")

            tonyStr+=str(x)+"\n"+str(y)+"\n"+str(xmax)+"\n"+str(ymax)+"\n"+"//////////"
            veicoli.append(str(x)+","+str(y)+","+str(xmax)+","+str(ymax))

            # cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            # cv2.putText(img, label+" "+str(spot), (x, y + 30), font, 1, color, 1)

            # cv2.circle(img, (x, y), radius=2, color=(0, 0, 255), thickness=2)  # alto sin
            # cv2.circle(img, (x, y+h), radius=2, color=(0, 0, 255), thickness=2)  # basso sin

            # cv2.circle(img, (x+w, y), radius=2, color=(0, 0, 255), thickness=2)  # asto des
            # cv2.circle(img, (x+w, y+h), radius=2, color=(0, 0, 255), thickness=2)  # asto des

            # cv2.circle(img, (int(nuovo_x), int(nuovo_y)), radius=2, color=(0, 0, 255), thickness=6)  # ccenter point

    # print(tonyStr)
    print("FINE")
    return veicoli


#///////////////////////////////////API/////////////////////////////////////////////


def home(request):
    return HttpResponse("up")



def dammiCondizioni(request):
    # http://127.0.0.1:8000/dammiCondizioni?link=rtsp://localhost/live
    link=request.GET["link"]
    # request.POST["id"]
    print(link)
    nameimg=getFrame(link)


    image_data = open(nameimg, "rb").read()
    return HttpResponse(image_data, content_type="image/png")

    # get_image(nameimg)
    # return HttpResponse(link)
# rtsp://localhost/live


equazione_retta_passante_per_punto_di_fuga_verticale_x=1071.7197725395097
equazione_retta_passante_per_punto_di_fuga_verticale_y=46.87808476463806

equazione_retta_passante_per_punto_di_fuga_orizzontale_x=204.8875585718358
equazione_retta_passante_per_punto_di_fuga_orizzontale_y=111.82668312559738

equazione_retta_passante_per_punto_di_fuga_verticale=None
equazione_retta_passante_per_punto_di_fuga_orizzontale=None

def setCoordinates(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)

    else:
        return HttpResponse("NO")

    equazione_retta_passante_per_punto_di_fuga_verticale=received_json_data["fuga_verticale"]
    equazione_retta_passante_per_punto_di_fuga_orizzontale=received_json_data["fuga_orizzontale"]

    equazione_retta_passante_per_punto_di_fuga_verticale_x=received_json_data["fuga_verticale"]["x"]
    equazione_retta_passante_per_punto_di_fuga_verticale_y=received_json_data["fuga_verticale"]["y"]

    equazione_retta_passante_per_punto_di_fuga_orizzontale_x=received_json_data["fuga_orizzontale"]["x"]
    equazione_retta_passante_per_punto_di_fuga_orizzontale_y=received_json_data["fuga_orizzontale"]["y"]


    # print(received_json_data["stalli"]["0"])

    data_file="coordinates_1.yml"
    with open(data_file, "w+") as points:
        for i in range(0,len(received_json_data["stalli"])):

            # print(received_json_data["stalli"][str(i)][str(0)]["x"])
            # print(received_json_data["stalli"][str(i)][str(0)]["y"])
            # print(received_json_data["stalli"][str(i)][str(1)]["x"])
            # print(received_json_data["stalli"][str(i)][str(1)]["y"])
            # print(received_json_data["stalli"][str(i)][str(2)]["x"])
            # print(received_json_data["stalli"][str(i)][str(2)]["y"])
            # print(received_json_data["stalli"][str(i)][str(3)]["x"])
            # print(received_json_data["stalli"][str(i)][str(3)]["y"])

            points.write("-\n          id: " + str(i) + "\n          coordinates: [" +
                              "[" + str(received_json_data["stalli"][str(i)][str(0)]["x"]) + "," + str(received_json_data["stalli"][str(i)][str(0)]["y"]) + "]," +
                              "[" + str(received_json_data["stalli"][str(i)][str(1)]["x"]) + "," + str(received_json_data["stalli"][str(i)][str(1)]["y"]) + "]," +
                              "[" + str(received_json_data["stalli"][str(i)][str(2)]["x"]) + "," + str(received_json_data["stalli"][str(i)][str(2)]["y"]) + "]," +
                              "[" + str(received_json_data["stalli"][str(i)][str(3)]["x"]) + "," + str(received_json_data["stalli"][str(i)][str(3)]["y"]) + "]]\n")

        # print("///////\n")

    return HttpResponse(request.body)


# def sendData():#mando json stallo -> percentuale riferito al parcheggio rtsp1
#     url = "http://localhost:8080"
#     data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
#     headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#     r = requests.post(url, data=json.dumps(data), headers=headers)

def getParkingDataFromYml(data_file):
    with open(data_file, 'r') as stream:
        parking_data = yaml.safe_load(stream)

    return parking_data


# ///////////////////////////////////////////////////////////////-----TONY-----///////////////////////////////////////////////////////////////

def retta_da_punti(x_retta_1, y_retta_1, x_retta_2, y_retta_2):
    if (x_retta_1 == x_retta_2):

        # m
        x = 1
        y = 0
        # b
        noto = (-1) * x_retta_1

    else:
        # m
        x = (y_retta_2 - y_retta_1) / (x_retta_2 - x_retta_1)
        y = 1
        # b
        noto = y_retta_1 + ((-1) * (x * x_retta_1))


    # vettore_valori = []
    vettore_valori = {}

    vettore_valori["x"] = x
    vettore_valori["y"] = y
    vettore_valori["noto"] = noto

    print("{}{}{}{}{}{}{}")
    return vettore_valori
    print("{}{}{}{}{}{}{}")



def vettore_univoco(vettore):

    # print("Vettore  ---->")
    # print(vettore)

    vettore_iniziale = vettore

    # vettore_iniziale = defaultdict(dict)-->dovrebbe gia' esserlo

    # vettore_finale = []

    # print("Nuooovo")
    # print(vettore_iniziale)

    ok=False#DA AGGIUSTARE

    if(len(vettore_iniziale)>2):

        # print("ciao %d"%(len(vettore_iniziale)))
        for i in range(0,len(vettore_iniziale)):

            if ok==True:
                break

            for i_2 in range(0,i):
                # print(len(vettore_iniziale))

                # print("len(vettore_iniziale) %d - i_2 %d - i %d"%(len(vettore_iniziale),i_2,i))
                # print("ci arrivo")
                # try:
                #     print(i_2)
                #     print(vettore_iniziale)
                #     print(vettore_iniziale[i_2]['x'])
                #     print("qui no")
                #     print(vettore_iniziale[i]['x'])
                #     print(vettore_iniziale[i_2]['y'])
                #     print(vettore_iniziale[i]['y'])
                # except:
                #     print("111EXE111")

                if (vettore_iniziale[i_2]['x'] == vettore_iniziale[i]['x'] and vettore_iniziale[i_2]['y'] == vettore_iniziale[i]['y']):

                    # print("entrooooooooooooooooooooooooooooooooo")
                    # vettore_iniziale.splice(i_2, 1)
                    # del vettore_iniziale[i_2]
                    # print(vettore_iniziale[i_2])
                    del vettore_iniziale[i_2]
                    # vettore_iniziale=np.delete(vettore_iniziale,i_2)

                    # break
                    # print(vettore_iniziale[i_2])
                    # print("ook")
                    ok=True





    # print("Vettore iniziale ---->")
    # print(vettore_iniziale)
    # print("FINEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")

    # except:
    #     print("An exception occurred crea_poligono_tridimensionale")
    return vettore_iniziale


def intersezione_tra_due_rette(noto_retta_1, noto_retta_2, x_retta_1, x_retta_2, y_retta_1, y_retta_2):

    x = ((noto_retta_2 + ((-1) * (noto_retta_1 * y_retta_2))) / ((y_retta_2 * x_retta_1) + ((-1) * x_retta_2)))

    y = (x_retta_1 * x) + noto_retta_1

    noto = None

    # vettore_valori = []
    vettore_valori = {}

    vettore_valori["x"] = x
    vettore_valori["y"] = y
    vettore_valori["noto"] = noto

    print(">>>>><<<<<<")
    print(vettore_valori)
    print(">>>>><<<<<<")

    return vettore_valori



def intersezione_tra_poligono_retta(x_poligono, y_poligono, larghezza_poligono, altezza_poligono, noto_retta, x_retta, y_retta):

    # print(".....................")
    # print(x_poligono)
    # print(y_poligono)
    # print(larghezza_poligono)
    # print(altezza_poligono)
    # print(noto_retta)
    # print(x_retta)
    # print(y_retta)
    # print(".....................")


    lati = []

    vettore_valori = []

    count_valori = 0

    # lati[0] = [x_poligono, y_poligono, (x_poligono + larghezza_poligono), y_poligono]
    lati.append([x_poligono, y_poligono, (x_poligono + larghezza_poligono), y_poligono])

    # lati[1] = [(x_poligono + larghezza_poligono), y_poligono, (x_poligono + larghezza_poligono),(y_poligono + altezza_poligono)]
    lati.append([(x_poligono + larghezza_poligono), y_poligono, (x_poligono + larghezza_poligono),(y_poligono + altezza_poligono)])

    # lati[2] = [(x_poligono + larghezza_poligono), (y_poligono + altezza_poligono), x_poligono,(y_poligono + altezza_poligono)]
    lati.append([(x_poligono + larghezza_poligono), (y_poligono + altezza_poligono), x_poligono,(y_poligono + altezza_poligono)])

    # lati[3] = [x_poligono, (y_poligono + altezza_poligono), x_poligono, y_poligono]
    lati.append([x_poligono, (y_poligono + altezza_poligono), x_poligono, y_poligono])

    vettore_valori = defaultdict(dict)

    for i in range (0,len(lati)):

        equazione_retta_lato  = retta_da_punti(lati[i][0], lati[i][1], lati[i][2], lati[i][3])



        equazione_intersezione_lato_retta = intersezione_tra_due_rette(noto_retta, equazione_retta_lato["noto"], x_retta, equazione_retta_lato["x"], y_retta, equazione_retta_lato["y"])

        if((round(equazione_intersezione_lato_retta["x"],0) >= lati[i][0] and round(equazione_intersezione_lato_retta["x"],0) <= lati[i][2] and round(equazione_intersezione_lato_retta["y"],0) >= lati[i][1] and round(equazione_intersezione_lato_retta["y"],0) <= lati[i][3]) or (round(equazione_intersezione_lato_retta["x"],0) <= lati[i][0] and round(equazione_intersezione_lato_retta["x"],0)>= lati[i][2] and round(equazione_intersezione_lato_retta["y"],0) <= lati[i][1] and round(equazione_intersezione_lato_retta["y"],0) >= lati[i][3])):

            # vettore_valori = defaultdict(dict)# -->dichiaratoo su VA VISTO
            vettore_valori[count_valori]["x"]=int(round(equazione_intersezione_lato_retta["x"],0))
            vettore_valori[count_valori]["y"]=int(round(equazione_intersezione_lato_retta["y"],0))

            count_valori+=1


        else:
            # print("entro nell'else")
            pass

    # print(">>>>>>>>>>>>>>>>>>>>")
    # print(vettore_valori)
    return vettore_valori


def crea_poligono_tridimensionale(x_poligono, y_poligono, larghezza_poligono, altezza_poligono):

    punti_salienti = []
    punti = []#defaultdict(dict)


    # equazione_retta_passante_per_punto_di_fuga_verticale_x-->equazione_retta_1_x
    # equazione_retta_passante_per_punto_di_fuga_verticale_y-->equazione_retta_1_y

    # equazione_retta_passante_per_punto_di_fuga_orizzontale_x -->equazione_retta_2
    # equazione_retta_passante_per_punto_di_fuga_orizzontale_y -->equazione_retta_2


    # punti[0] = [(x_poligono + (larghezza_poligono / 2)), (y_poligono + (altezza_poligono / 2)), equazione_retta_1]
    punti.append([(x_poligono + (larghezza_poligono / 2)), (y_poligono + (altezza_poligono / 2)), equazione_retta_passante_per_punto_di_fuga_verticale_x,equazione_retta_passante_per_punto_di_fuga_verticale_y,[]])

    # punti[1] = [x_poligono, (y_poligono + (altezza_poligono / 2)), equazione_retta_2]
    punti.append([x_poligono, (y_poligono + (altezza_poligono / 2)), equazione_retta_passante_per_punto_di_fuga_orizzontale_x,equazione_retta_passante_per_punto_di_fuga_orizzontale_y,[]])

    # punti[2] = [x_poligono, (y_poligono + altezza_poligono), equazione_retta_1]
    punti.append([x_poligono, (y_poligono + altezza_poligono), equazione_retta_passante_per_punto_di_fuga_verticale_x,equazione_retta_passante_per_punto_di_fuga_verticale_y,[]])

    # punti[3] = [(x_poligono + larghezza_poligono), (y_poligono + altezza_poligono), equazione_retta_2]
    punti.append([(x_poligono + larghezza_poligono), (y_poligono + altezza_poligono), equazione_retta_passante_per_punto_di_fuga_orizzontale_x,equazione_retta_passante_per_punto_di_fuga_orizzontale_y,[]])

    for i in range(0,len(punti)):

        # equazione_retta_fuga_verticale_auto = retta_da_punti(punti[i][0], punti[i][1], punti[i][2]["x"], punti[i][2]["y"])
        equazione_retta_fuga_verticale_auto = retta_da_punti(punti[i][0], punti[i][1], punti[i][2], punti[i][3])

        # print(equazione_retta_fuga_verticale_auto["x"])
        # prova=intersezione_tra_poligono_retta(x_poligono, y_poligono, larghezza_poligono, altezza_poligono,
        #                                 equazione_retta_fuga_verticale_auto["noto"],
        #                                 equazione_retta_fuga_verticale_auto["x"],
        #                                 equazione_retta_fuga_verticale_auto["y"])

        # print(prova)

        # prova2=vettore_univoco(prova)

        # print("***************************")

        # print(prova2)

        intersezioni_tra_poligono_retta = vettore_univoco(intersezione_tra_poligono_retta(x_poligono, y_poligono, larghezza_poligono, altezza_poligono, equazione_retta_fuga_verticale_auto["noto"], equazione_retta_fuga_verticale_auto["x"], equazione_retta_fuga_verticale_auto["y"]))

        # print(intersezioni_tra_poligono_retta)

        # print("//////////////////////////////sono in -->crea_poligono_tridimensionale")
        #
        # print(dict(intersezioni_tra_poligono_retta))

        # punti[i]["retta"] = intersezioni_tra_poligono_retta#non si puo fare

        punti[i][4] = intersezioni_tra_poligono_retta  # non si puo fare {1: {'x': 153, 'y': 418}}

        # print("------------------")
        # print(punti[i][4])

        # print("QUIIIIIIIIIIII")
        # print(punti[i][4])




    # print("///////////////////////")
    # print(punti[3][4].items())



    data = list(punti[3][4].items())
    an_array = np.array(data)

    
    
    # print(an_array)
    # print(an_array[0][1]['x'])

    # print("///////////////////////")


    
    # equazione_retta_passante_veicolo_1 = retta_da_punti(punti[0]["retta"][0]["x"], punti[0]["retta"][0]["y"],punti[0]["retta"][1]["x"], punti[0]["retta"][1]["y"])
    #
    # equazione_retta_passante_veicolo_2 = retta_da_punti(punti[1]["retta"][0]["x"], punti[1]["retta"][0]["y"],punti[1]["retta"][1]["x"], punti[1]["retta"][1]["y"])
    #
    # equazione_retta_passante_veicolo_3 = retta_da_punti(punti[2]["retta"][0]["x"], punti[2]["retta"][0]["y"],punti[2]["retta"][1]["x"], punti[2]["retta"][1]["y"])

    # equazione_retta_passante_veicolo_4 = retta_da_punti(punti[3]["retta"][0]["x"], punti[3]["retta"][0]["y"],punti[3]["retta"][1]["x"], punti[3]["retta"][1]["y"])
    equazione_retta_passante_veicolo_4 = retta_da_punti(an_array[0][1]['x'], an_array[0][1]['y'],an_array[1][1]['x'],an_array[1][1]['y'])


    # print(equazione_retta_passante_veicolo_4)

    # DA VEDERE
    # equazione_retta_passante_veicolo_4 = retta_da_punti(punti[3]["retta"][0][3], punti[3]["retta"][0][4],punti[3]["retta"][1][3], punti[3]["retta"][1][4])
    # equazione_retta_passante_veicolo_4 = retta_da_punti(punti[3][4][0][3], punti[3][4][0][4],punti[3][4][1][3], punti[3][4][1][4])

    equazione_retta_passante_veicolo_5 = retta_da_punti(x_poligono + (larghezza_poligono / 2), y_poligono,x_poligono + (larghezza_poligono / 2),y_poligono + altezza_poligono)

    equazione_intersezione_tra_retta_passante_veicolo_4_5 = intersezione_tra_due_rette(equazione_retta_passante_veicolo_4["noto"],equazione_retta_passante_veicolo_5["noto"],equazione_retta_passante_veicolo_4["x"],equazione_retta_passante_veicolo_5["x"],equazione_retta_passante_veicolo_4["y"],equazione_retta_passante_veicolo_5["y"])

    equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_verticale = retta_da_punti(equazione_intersezione_tra_retta_passante_veicolo_4_5["x"],equazione_intersezione_tra_retta_passante_veicolo_4_5["y"],equazione_retta_passante_per_punto_di_fuga_verticale_x,equazione_retta_passante_per_punto_di_fuga_verticale_y)

    equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_orizzontale = retta_da_punti(equazione_intersezione_tra_retta_passante_veicolo_4_5["x"],equazione_intersezione_tra_retta_passante_veicolo_4_5["y"],equazione_retta_passante_per_punto_di_fuga_orizzontale_x,equazione_retta_passante_per_punto_di_fuga_orizzontale_y)


    n_punto_tolleranza = 0

    punti_salienti = []
    for i_4 in range(-10,10):

        equazione_intersezione_tra_retta_passante_veicolo_4_5_tolleranza_y = (intersezione_tra_due_rette(equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_verticale["noto"],(equazione_intersezione_tra_retta_passante_veicolo_4_5["y"]-i_4),equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_verticale["x"],0,equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_verticale["y"],1))


        # punti_salienti[n_punto_tolleranza] =[]



        punti_salienti.append(equazione_intersezione_tra_retta_passante_veicolo_4_5_tolleranza_y)

        # punti_salienti[n_punto_tolleranza] = equazione_intersezione_tra_retta_passante_veicolo_4_5_tolleranza_y

        # n_punto_tolleranza+=1


        equazione_intersezione_tra_retta_passante_veicolo_4_5_tolleranza_x = (intersezione_tra_due_rette(equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_orizzontale["noto"],((-1) * (equazione_intersezione_tra_retta_passante_veicolo_4_5["x"]-i_4)),equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_orizzontale["x"],1,equazione_retta_passante_centro_prospettiva_veicolo_punto_di_fuga_orizzontale["y"],0))


        # punti_salienti[n_punto_tolleranza] =[]

        punti_salienti.append(equazione_intersezione_tra_retta_passante_veicolo_4_5_tolleranza_x)

        # punti_salienti[n_punto_tolleranza] = equazione_intersezione_tra_retta_passante_veicolo_4_5_tolleranza_x

        # n_punto_tolleranza+=1


    # print("FINE crea_poligono_tridimensionale")
    # print(punti_salienti)
    return punti_salienti



def identifica_veicoli(veicolo):

    # print(len(veicolo))
    veicoli_elaborati = defaultdict(dict)
    for i in range(0,len(veicolo)):
        punti = veicolo[i].split(",")

        # x = float(punti[0])
        # y = float(punti[1])
        # larghezza = float(punti[2] - x)
        # altezza = float(punti[3] - y)

        x = float(punti[0])
        y = float(punti[1])

        larghezza = float(punti[2]) - float(x)
        altezza = float(punti[3]) - float(y)

        # centro_x = (x + (larghezza / 2))
        # centro_y = (y + (altezza / 2))

        # equazione_retta_fuga_orizzontale_auto = retta_da_punti(centro_x, centro_y,equazione_retta_passante_per_punto_di_fuga_orizzontale_x,equazione_retta_passante_per_punto_di_fuga_orizzontale_y)

        # punti_salienti = crea_poligono_tridimensionale(x, y, larghezza, altezza,equazione_retta_passante_per_punto_di_fuga_verticale,equazione_retta_passante_per_punto_di_fuga_orizzontale)

        punti_salienti = crea_poligono_tridimensionale(x, y, larghezza, altezza)

        # print(punti_salienti)


        veicoli_elaborati[i] = {}

        veicoli_elaborati[i]["x_veicolo"] = x

        veicoli_elaborati[i]["y_veicolo"] = y

        veicoli_elaborati[i]["altezza"] = altezza

        veicoli_elaborati[i]["larghezza"] = larghezza

        print("<><><><><><><><><><><>")
        print(veicoli_elaborati)
        print("<><><><><><><><><><><>")


        veicoli_elaborati[i]["punti_salienti"] = punti_salienti
        # print("ALLORA QUI")

        # print(veicoli_elaborati[i]["punti_salienti"])


    return veicoli_elaborati


def appartenenza_punto_retta(x_punto, y_punto, x_inizio_retta, y_inizio_retta, x_fine_retta, y_fine_retta):
    #punto
    y = y_punto
    x = x_punto

    #retta
    x0 = x_inizio_retta
    y0 = y_inizio_retta

    x1 = x_fine_retta
    y1 = y_fine_retta

    equazione = (x * (y0 - y1)) - (y * (x0 - x1)) + (x0 * y1) - (x1 * y0)

    # print("eq:")
    # print(equazione)

    return equazione

def appartenenza_punto_poligono(centro_x, centro_y, punti_stallo_1_x, punti_stallo_1_y, punti_stallo_2_x, punti_stallo_2_y,punti_stallo_3_x, punti_stallo_3_y, punti_stallo_4_x, punti_stallo_4_y):
    # print("++++++++++++++++++++++++")
    if (appartenenza_punto_retta(centro_x, centro_y, punti_stallo_1_x, punti_stallo_1_y, punti_stallo_2_x,punti_stallo_2_y) < 0 and appartenenza_punto_retta(centro_x, centro_y,punti_stallo_4_x, punti_stallo_4_y,punti_stallo_1_x,punti_stallo_1_y) < 0 and appartenenza_punto_retta(centro_x, centro_y, punti_stallo_2_x, punti_stallo_2_y, punti_stallo_3_x,punti_stallo_3_y) < 0 and appartenenza_punto_retta(centro_x, centro_y, punti_stallo_3_x, punti_stallo_3_y,punti_stallo_4_x, punti_stallo_4_y) < 0):
        return True
    else:
        return False

def nonesorter(a):
    if not a:
        return ""
    return a

def elabora(veicoli_elaborati,vettore_stalli_elaborato):

    for ind, park in enumerate(vettore_stalli_elaborato):#ind--> i
        points = np.array(park['coordinates'])

        # punti_stallo_1_x = vettore_stalli_elaborato[i][0]["x"]
        # punti_stallo_1_y = vettore_stalli_elaborato[i][0]["y"]

        punti_stallo_1_x=points[0][0]
        punti_stallo_1_y=points[0][1]

        # punti_stallo_2_x = vettore_stalli_elaborato[i][1]["x"]
        # punti_stallo_2_y = vettore_stalli_elaborato[i][1]["y"]

        punti_stallo_2_x=points[1][0]
        punti_stallo_2_y=points[1][1]

        # punti_stallo_3_x = vettore_stalli_elaborato[i][2]["x"]
        # punti_stallo_3_y = vettore_stalli_elaborato[i][2]["y"]

        punti_stallo_3_x=points[2][0]
        punti_stallo_3_y=points[2][1]

        # punti_stallo_4_x = vettore_stalli_elaborato[i][3]["x"]
        # punti_stallo_4_y = vettore_stalli_elaborato[i][3]["y"]

        punti_stallo_4_x=points[3][0]
        punti_stallo_4_y=points[3][1]

        risposta = {}
        for i_3 in range(0,len(veicoli_elaborati)):

            x = veicoli_elaborati[i_3]["x_veicolo"]
            y = veicoli_elaborati[i_3]["y_veicolo"]
            larghezza = veicoli_elaborati[i_3]["larghezza"]
            altezza = veicoli_elaborati[i_3]["altezza"]

            centro_x = (x+(larghezza/2))
            centro_y = (y+(altezza/2))
            tolleranza_stalli = [None] *(len(vettore_stalli_elaborato)+1)

            # print(x)
            # print(y)
            # print(larghezza)
            # print(altezza)

            # print(veicoli_elaborati[i_3]["punti_salienti"])

            for i_4 in range(0,len(veicoli_elaborati[i_3]["punti_salienti"])):

                centro_x = veicoli_elaborati[i_3]["punti_salienti"][i_4]["x"]
                centro_y = veicoli_elaborati[i_3]["punti_salienti"][i_4]["y"]

                if (appartenenza_punto_poligono(centro_x, centro_y, punti_stallo_1_x, punti_stallo_1_y, punti_stallo_2_x,punti_stallo_2_y, punti_stallo_3_x, punti_stallo_3_y, punti_stallo_4_x,punti_stallo_4_y)):
                    if tolleranza_stalli[ind]==None:
                        tolleranza_stalli[ind]=0

                    tolleranza_stalli[ind]=tolleranza_stalli[ind]+1#qui se torna true significa che e' all'interno del poligono e che mi salvo? il punto cosi' lo perdo
                    # print(tolleranza_stalli)

                else:
                    if(tolleranza_stalli[len(tolleranza_stalli)-1]==None):
                        tolleranza_stalli[len(tolleranza_stalli)-1]=0

                    tolleranza_stalli[len(tolleranza_stalli)-1]=tolleranza_stalli[len(tolleranza_stalli)-1]+1


            # tolleranza_stalli_intero = Object.values(tolleranza_stalli)
            tolleranza_stalli_intero=tolleranza_stalli


            # ordina_tolleranza_stalli_interno = tolleranza_stalli_intero.sort(function(a, b){return b - a})

            tolleranza_stalli_map={}
            for i in range(0,len(tolleranza_stalli_intero)):
                if i==len(tolleranza_stalli_intero)-1:
                    tolleranza_stalli_map["fuori"]=tolleranza_stalli_intero[i]
                else:
                    tolleranza_stalli_map[str(i)]=tolleranza_stalli_intero[i]



            # print(tolleranza_stalli_map)

            ordina_tolleranza_stalli_interno=sorted(tolleranza_stalli, key=lambda x: (x is None, x))

            # print("<<<<<<<<<<")
            # print(tolleranza_stalli)
            # print(ordina_tolleranza_stalli_interno)#perdo la chiave "fuori"
            # print("<<<<<<<<<<")



            #tolleranza_stalli_vincente = getKeyByValue(tolleranza_stalli, ordina_tolleranza_stalli_interno[0])

            inv_dict = {value:key for key, value in tolleranza_stalli_map.items()}
            # print(inv_dict[ordina_tolleranza_stalli_interno[0]])
            tolleranza_stalli_vincente=inv_dict[ordina_tolleranza_stalli_interno[0]]

            # tolleranza_stalli_vincente_valore = ordina_tolleranza_stalli_interno[0]
            tolleranza_stalli_vincente_valore =ordina_tolleranza_stalli_interno[0]

            #tolleranza_stalli_somma = tolleranza_stalli_intero.reduce((a, b) = > a + b, 0)
            tolleranza_stalli_somma=sum(filter(None,tolleranza_stalli_intero))



            tolleranza_stalli_vincente_percentuale = tolleranza_stalli_vincente_valore / tolleranza_stalli_somma * 100
            # print(tolleranza_stalli_vincente_percentuale)


            if (tolleranza_stalli_somma > 0 and tolleranza_stalli_vincente != "fuori"):
                # document.getElementById("dati").innerHTML += "<tr><td>Veicolo " + i_3 + "</td><td style=\"text-align: center;\">" + tolleranza_stalli_vincente + "</td><td>" + tolleranza_stalli_vincente_percentuale + "%</td></tr>"
                print(i_3)
                risposta["Veicolo "+str(i_3)+" Tolleranza_stalli_vincente"+str(tolleranza_stalli_vincente)]=int(tolleranza_stalli_vincente_percentuale)
                print("Veicolo %d tolleranza_stalli_vincente %s tolleranza_stalli_vincente_percentuale %d "%(i_3,tolleranza_stalli_vincente,tolleranza_stalli_vincente_percentuale))

    print(risposta)
            # myurl = "http://www.testmycode.com"
            #
            # req = urllib.request.Request(myurl)
            # req.add_header('Content-Type', 'application/json; charset=utf-8')
            # jsondata = json.dumps(risposta)
            # jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
            # req.add_header('Content-Length', len(jsondataasbytes))
            # response = urllib.request.urlopen(req, jsondataasbytes)

# ///////////////////////////////////////////////////////////////-----TONY-----///////////////////////////////////////////////////////////////

if __name__ == '__main__':

    nomeYml = "coordinates_1.yml"
    linkRtsp = "rtsp://localhost:554/live"

    # imaaa=getFrame(linkRtsp)

    imaaa = "ima2.png"
    # parking_data = avvio_mappatura(nomeYml, imaaa)

    parking_data = getParkingDataFromYml(nomeYml)

    for ind, park in enumerate(parking_data):
        points = np.array(park['coordinates'])
        # print(ind)
        # print(park)


    puntiAuto = avvio_detection(imaaa)

    print(puntiAuto)

    veicoli_elaborati= identifica_veicoli(puntiAuto)


    # print(veicoli_elaborati)

    elabora(veicoli_elaborati,parking_data)
