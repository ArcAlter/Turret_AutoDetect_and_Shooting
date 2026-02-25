import cv2
import time
import serial
from ultralytics import YOLO

# --- ตั้งค่า Serial ---
SERIAL_PORT_NAME = "COM7" 
BAUD_RATE = 9600
try:
    ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout=0.1) # ลด timeout ให้ลื่นขึ้น
    time.sleep(2) 
    print(f"Connected to {SERIAL_PORT_NAME}")
except Exception as e:
    print(f"Serial Error: {e}")
    ser = None

# --- ตั้งค่า YOLO & Camera ---
model = YOLO(r'D:\AI_3\เทอม2\Robotics_yolo\yolo26n.pt') 
cap = cv2.VideoCapture(0)
prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. คำนวณ FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # 2. Predict เฉพาะคน (classes=[0])
    results = list(model(frame, stream=True, classes=[0], max_det=8)) # ใช้ list เพื่อดึงค่าได้ง่ายขึ้น
    
    person_count = 0
    for r in results:
        person_count = len(r.boxes)
        annotated_frame = r.plot()

        # 3. ส่งข้อมูลไป Serial (ส่งเฉพาะเมื่อต่อสำเร็จ)
        if ser and ser.is_open:
            # ส่งจำนวนคน + \n เพื่อให้ฝั่งรับ (เช่น Arduino) แยกบรรทัดได้ง่าย
            data_to_send = f"{person_count * 23}\n"
            ser.write(data_to_send.encode('utf-8'))
            
            # ตรวจสอบว่ามีข้อมูลตอบกลับจากบอร์ดไหม (Non-blocking)
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                print(f"From Hardware: {response}")

        # 4. แสดงผลบนจอ
        cv2.putText(annotated_frame, f'FPS: {int(fps)}', (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(annotated_frame, f'People: {person_count}', (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("YOLO26 Nano - Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# คืนทรัพยากรทั้งหมด
cap.release()
cv2.destroyAllWindows()
if ser and ser.is_open:
    ser.close()