import cv2
import requests
import time
import json
import os
from qr_decoder import decode_qr
from dotenv import load_dotenv

load_dotenv()

qrCode = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()

while True:
    ret, frame = cap.read()

    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr:
            for info, point in zip(decoded_info, points):
                if info:
                    color = (0, 255, 0)
                    decoded_link = decode_qr(info)
                    print(f"QR Decoded: {decoded_link}")

                    # Realizar la petición HTTP con el link decodificado
                    url = "https://academia.unibague.edu.co/atlante/appunibague/valida_salon.php"
                    params = {
                        "usuario": "maria.castillo",
                        "aula": os.getenv("AULA"),
                        "fecha": "20240507",
                        "hor": "8",
                        "min": "7"
                    }
                    try:
                        response = requests.get(url, params=params)
                        response_text = response.text
                        print(f"HTTP Response Raw: {response_text}")  # Imprimir la respuesta cruda

                        # Intentar extraer la parte JSON
                        try:
                            start_index = response_text.index("[")
                            end_index = response_text.rindex("]") + 1
                            json_text = response_text[start_index:end_index]
                            print(f"Extracted JSON: {json_text}")  # Imprimir el JSON extraído
                            response_data = json.loads(json_text)
                            
                            # Verificar el valor de "access"
                            if response_data and response_data[0]['access'] == 1:
                                # Aca esta el codigo para que se pueda abrir la puerta!

                                print("Abre puerta")

                            else:
                                print("Acceso denegado")
                        except (ValueError, json.JSONDecodeError) as e:
                            print(f"Error al parsear la respuesta JSON: {e}")

                    except requests.RequestException as e:
                        print(f"Error realizando la solicitud: {e}")

                    # Esperar 10 segundos antes de continuar
                    time.sleep(10)
                else:
                    color = (0, 0, 255)
                frame = cv2.polylines(frame, [point.astype(int)], True, color, 8)
    else:
        print("No se puede recibir el fotograma (¿final de la transmisión?). Saliendo ...")
        break

    cv2.imshow('Detector de codigos QR', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
