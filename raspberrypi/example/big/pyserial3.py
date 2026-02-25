import cv2
import time
import serial
from ultralytics import YOLO

SERIAL_PORT_NAME = "COM7" 
BAUD_RATE = 9600
try:
    ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout=0.05) 
    time.sleep(2) 
    print(f"Connected to {SERIAL_PORT_NAME}")
except Exception as e:
    print(f"Serial Error: {e}")
    ser = None

model = YOLO(r'D:\AI_3\เทอม2\Robotics_yolo\yolo26n.pt') 
cap = cv2.VideoCapture(0)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 

while True:
    ret, frame = cap.read()
    if not ret: break

    results = list(model(frame, stream=True, classes=[0], max_det=8))
    
    annotated_frame = frame.copy()
    target_angle = 90 
    max_area = 0
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            w = x2 - x1
            h = y2 - y1
            area = w * h

            if area > max_area:
                max_area = area
                center_x = x1 + (w / 2)

                target_angle = abs(180 - int((center_x / frame_width) * 180))
                
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                cv2.circle(annotated_frame, (int(center_x), int(y1 + h/2)), 5, (0, 0, 255), -1)

    if ser and ser.is_open:
        data_to_send = f"{target_angle}\n"
        ser.write(data_to_send.encode('utf-8'))
        
        cv2.putText(annotated_frame, f'Servo Angle: {target_angle}', (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("YOLO26 Nano - Servo Tracking", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if ser and ser.is_open:
    ser.close()