import cv2
import pyautogui
import json
import config

with open('options.json', 'r') as options_values:
    global options 
    options = json.load(options_values)

def update_options(x):
    if config.debug:
        options["hue"]["min"] = cv2.getTrackbarPos('h min','calibrate')
        options["hue"]["max"]  = cv2.getTrackbarPos('h max','calibrate')
        options["sat"]["min"]  = cv2.getTrackbarPos('s min','calibrate')
        options["sat"]["max"] = cv2.getTrackbarPos('s max','calibrate')
        options["val"]["min"]  = cv2.getTrackbarPos('v min','calibrate')
        options["val"]["max"] = cv2.getTrackbarPos('v max','calibrate')
        options['minarea'] = cv2.getTrackbarPos('min area','calibrate')
    options['sens'] = cv2.getTrackbarPos('sens','sensitivity')
    
def create_trackbars():
    if config.debug:
        cv2.namedWindow('calibrate')
        cv2.createTrackbar('h min','calibrate', options["hue"]["min"], 255, update_options)
        cv2.createTrackbar('h max','calibrate', options["hue"]["max"], 255, update_options)
        cv2.createTrackbar('s min','calibrate', options["sat"]["min"], 255, update_options)
        cv2.createTrackbar('s max','calibrate', options["sat"]["max"], 255, update_options)
        cv2.createTrackbar('v min','calibrate', options["val"]["min"], 255, update_options)
        cv2.createTrackbar('v max','calibrate', options["val"]["max"], 255, update_options)
        cv2.createTrackbar('min area','calibrate', options["minarea"], 2000, update_options)
    cv2.namedWindow('sensitivity')
    cv2.createTrackbar('sens','sensitivity', options["sens"], 100, update_options)


# def move_cursor(x,y):
#     win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/config.screen_width*65535.0), int(y/config.screen_height*65535.0))

def start(debug):
    allow_movement = False
    cap = cv2.VideoCapture(config.capture_index)
    print("opening camera")
    create_trackbars()
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    print("camera opened")
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        lower_bound = (
            options["hue"]["min"], 
            options["sat"]["min"],
            options["val"]["min"]
        )
        upper_bound = (
            options["hue"]["max"], 
            options["sat"]["max"],
            options["val"]["max"]
        )
        img = cv2.resize(frame, (int(config.frame_width), int(config.frame_height)), interpolation=cv2.INTER_CUBIC)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsv_mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
        img = cv2.bitwise_and(img, img, mask=hsv_mask)

        
        # Display the resulting frame
        

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for (index, contour) in enumerate(contours):
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            area = cv2.contourArea(approx)
            # cv2.drawContours(img, contours, index, (0,0,255), 2)
            if area > options["minarea"]:
                x, y, w, h = cv2.boundingRect(approx)
                center_y = y + h/2
                if allow_movement:
                    sens_multiplier = (1 + options['sens'] * .01)
                    pyautogui.moveTo(x / 640 * config.screen_width * sens_multiplier, center_y / 640 * config.screen_height * sens_multiplier)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # print(center_x / 640 * config.screen_width , center_y / 480 * config.screen_height)
                
        cv2.imshow('hsv', img)
        key = cv2.waitKey(1)

        #keybinds
        if key == ord('p'):
                if allow_movement:
                    allow_movement = False
                else:
                    allow_movement = True
        if key == ord('q'):
                break
        if key == ord('c'):
            pyautogui.click()

        if debug is True:
            cv2.imshow('frame', frame)
            if key == ord('w'):
                print("saved hsv values")
                with open("options.json", 'w') as file:
                    json.dump(options, file)
            

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    start(config.debug)