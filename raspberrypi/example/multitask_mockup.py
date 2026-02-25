import cv2
import multiprocessing as mp_proc
import time

# --- CONFIGURATION ---
VIDEO_PATH = "video.mp4"

# TARGET RESOLUTION: 
# Resizing in the worker is CRITICAL for performance. 
# Sending massive frames through multiprocessing queues causes lag (20fps).
# 1280x720 is a good balance of speed and quality. 
# The Fullscreen window will stretch this to fit your monitor automatically.
RESIZE_W, RESIZE_H = 1920, 1080 

TARGET_FPS = 30
FRAME_INTERVAL_MS = int(1000 / TARGET_FPS)

def video_worker(video_path, queue, state_flag):
    """Reads video, resizes it, and puts it in the queue."""
    cap = cv2.VideoCapture(video_path)
    
    try:
        while True:
            # Pause processing if in Camera mode to save CPU
            if state_flag.value == 1:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # 1. RESIZE HERE (The Performance Fix)
            # Resizing before the queue reduces the data size significantly.
            frame = cv2.resize(frame, (RESIZE_W, RESIZE_H))

            # 2. BLOCKING PUT
            # If queue is full, this waits. This synchronizes worker with Main UI.
            queue.put(frame)
    finally:
        cap.release()

def camera_worker(queue, state_flag):
    print("[Camera] Worker started. Opening Camera...")
    
    # Try removing cv2.CAP_V4L2 if on Windows, or if it causes issues
    cam_idx = 2
    cap = cv2.VideoCapture(cam_idx, cv2.CAP_V4L2) 
    
    if not cap.isOpened():
        print(f"[Camera] CRITICAL ERROR: Could not open camera (Index {cam_idx}).")
        return

    # Try MJPG again, but we will print if it works
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) # 2560 | 1920 | 1280 | 640
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) # 1440 | 1080 | 720  | 360
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)

    print("[Camera] Camera opened successfully.")

    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("[Camera] Error: Read failed! (Camera disconnected?)")
                time.sleep(1) # Prevent spamming logs
                continue
            
            if state_flag.value == 1:
                # Drop old frames to keep latency low
                if queue.full():
                    try: queue.get_nowait()
                    except: pass
                
                queue.put(frame)
            else:
                # IMPORTANT: We must still keep the camera buffer empty
                # even when not displaying, otherwise when we switch back
                # we will see 5 seconds of old delayed footage.
                # So we DON'T sleep for long, and we DON'T skip reading.
                time.sleep(0.01)
    finally:
        cap.release()


if __name__ == "__main__":
    state_flag = mp_proc.Value('i', 0) 
    
    # Buffer size 3 is enough to smooth jitter without adding latency
    video_q = mp_proc.Queue(maxsize=3)
    camera_q = mp_proc.Queue(maxsize=3)

    p_video = mp_proc.Process(target=video_worker, args=(VIDEO_PATH, video_q, state_flag))
    p_camera = mp_proc.Process(target=camera_worker, args=(camera_q, state_flag))
    
    p_video.start()
    p_camera.start()

    # Setup Full Screen Window
    window_name = "Main UI"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("UI Started. Press 'c' for Camera, 'v' for Video, 'q' to Quit")

    # --- FPS CALCULATION VARIABLES ---
    prev_frame_time = 0
    new_frame_time = 0
    fps_buffer = [] 
    last_print_time = time.time()
    frame_counter = 0
    fps_label = f"FPS: N/A"

    try:
        while True:
            loop_start = time.time()
            display_frame = None

            # 1. Get Frame
            if state_flag.value == 0:
                if not video_q.empty():
                    display_frame = video_q.get()
            else:
                if not camera_q.empty():
                    display_frame = camera_q.get()

            if display_frame is not None:
                display_frame = cv2.resize(display_frame, (RESIZE_W, RESIZE_H))

                # 2. Calculate FPS
                new_frame_time = time.time()
                # Avoid division by zero
                diff = new_frame_time - prev_frame_time
                fps = 1 / diff if diff > 0 else 0
                prev_frame_time = new_frame_time
                
                # Update counters for console print
                frame_counter += 1
                
                # 3. Print FPS to Console (Every 1 Second)
                if time.time() - last_print_time >= 1.0:
                    print(f"[Main Loop] FPS: {frame_counter}")
                    fps_label = f"FPS: {int(frame_counter)}"
                    frame_counter = 0
                    last_print_time = time.time()

                # 4. Draw Info on UI
                source_label = "SOURCE: CAMERA" if state_flag.value == 1 else "SOURCE: VIDEO"
                
                # Draw black background rectangle for text readability
                cv2.rectangle(display_frame, (0, 0), (350, 100), (0, 0, 0), -1)
                
                cv2.putText(display_frame, source_label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(display_frame, fps_label, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow(window_name, display_frame)

            process_time_ms = (time.time() - loop_start) * 1000
            wait_ms = max(1, int(FRAME_INTERVAL_MS - process_time_ms))

            # 5. Handle Keys
            key = cv2.waitKey(wait_ms) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                state_flag.value = 1
                # Clear video queue to avoid "old" frames when switching back later
                while not video_q.empty(): video_q.get()
            elif key == ord('v'):
                state_flag.value = 0

    finally:
        p_video.terminate()
        p_camera.terminate()
        cv2.destroyAllWindows()