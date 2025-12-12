import cv2
import mediapipe as mp
import numpy as np
from pynput.keyboard import Controller
import time

# Initialize keyboard controller
keyboard = Controller()

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", "."],
    ["SPACE", "BACKSPACE", "ENTER"]
]

# Button class for keyboard keys
class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.text = text
        self.size = size

def draw_keyboard(img, button_list):
    """Draw virtual keyboard on screen"""
    for button in button_list:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
        cv2.putText(img, button.text, (x + 15, y + 55),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img

def create_button_list():
    """Create button objects for all keys"""
    button_list = []
    start_x = 50
    start_y = 200
    
    for i, row in enumerate(keys):
        x_offset = start_x + (i * 45)
        for j, key in enumerate(row):
            if key == "SPACE":
                button_list.append(Button([x_offset + j * 95, start_y + i * 95], key, [200, 85]))
            elif key == "BACKSPACE":
                button_list.append(Button([x_offset + j * 95 + 220, start_y + i * 95], key, [180, 85]))
            elif key == "ENTER":
                button_list.append(Button([x_offset + j * 95 + 420, start_y + i * 95], key, [140, 85]))
            else:
                button_list.append(Button([x_offset + j * 95, start_y + i * 95], key))
    
    return button_list

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Initialize
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
button_list = create_button_list()
typed_text = ""
last_key_time = 0
key_delay = 0.3

print("=" * 50)
print("🎹 VIRTUAL KEYBOARD STARTED!")
print("=" * 50)
print("Instructions:")
print("1. Show your hand to the camera")
print("2. Bring thumb and index finger close to click a key")
print("3. Press 'ESC' to exit")
print("=" * 50)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to access camera!")
        break
    
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    # Draw keyboard
    img = draw_keyboard(img, button_list)
    
    # Display typed text
    cv2.rectangle(img, (50, 50), (1230, 130), (255, 255, 255), cv2.FILLED)
    cv2.putText(img, typed_text[-40:], (60, 105), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = []
            for lm in hand_landmarks.landmark:
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append([cx, cy])
            
            if len(landmarks) >= 9:
                index_finger = landmarks[8]
                thumb = landmarks[4]
                
                distance = calculate_distance(index_finger, thumb)
                
                cv2.line(img, tuple(thumb), tuple(index_finger), (0, 255, 0), 3)
                cv2.circle(img, tuple(index_finger), 15, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, tuple(thumb), 15, (255, 0, 255), cv2.FILLED)
                
                current_time = time.time()
                if distance < 40 and (current_time - last_key_time) > key_delay:
                    for button in button_list:
                        x, y = button.pos
                        w, h = button.size
                        
                        if x < index_finger[0] < x + w and y < index_finger[1] < y + h:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 15, y + 55),
                                      cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                            
                            if button.text == "SPACE":
                                typed_text += " "
                            elif button.text == "BACKSPACE":
                                typed_text = typed_text[:-1]
                            elif button.text == "ENTER":
                                typed_text += "\n"
                            else:
                                typed_text += button.text
                            
                            last_key_time = current_time
                            time.sleep(0.15)
    
    cv2.putText(img, "Press ESC to exit", (50, 680), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    
    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("\n✅ Virtual Keyboard Closed Successfully!")
