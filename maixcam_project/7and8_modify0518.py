import json
import time

from maix import app, camera, display, image, nn, pinmap, uart


pinmap.set_pin_function('A18', 'UART1_RX')
pinmap.set_pin_function('A19', 'UART1_TX')
serial_ctrl = uart.UART('/dev/ttyS1', 115200)

DETECT_MODEL = '/root/models/maixhub/model_271483.mud'
OCR_MODEL = '/root/models/pp_ocr.mud'
SOURCE_ID = 'maixcam_pro_uart1'

detector = nn.YOLOv5(DETECT_MODEL)
ocr = nn.PP_OCR(OCR_MODEL)

cam = camera.Camera(ocr.input_width(), ocr.input_height(), ocr.input_format())
disp = display.Display()

image.load_font('ppocr', '/maixapp/share/font/ppocr_keys_v1.ttf', size=22)
image.set_default_font('ppocr')


def clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def read_score(obj):
    for name in ('score', 'confidence', 'prob'):
        try:
            attr = getattr(obj, name)
        except AttributeError:
            continue

        try:
            value = attr() if callable(attr) else attr
            if value is not None:
                return float(value)
        except Exception:
            continue
    return None


def build_confidence(det_obj, ocr_objs):
    scores = []

    det_score = read_score(det_obj)
    if det_score is not None:
        scores.append(det_score)

    ocr_scores = []
    for obj in ocr_objs:
        score = read_score(obj)
        if score is not None:
            ocr_scores.append(score)
    if ocr_scores:
        scores.append(sum(ocr_scores) / len(ocr_scores))

    if not scores:
        return 0.5
    return clamp(sum(scores) / len(scores))


def plate_correct(raw_txt):
    if not raw_txt:
        return ''

    s = raw_txt.upper().replace(' ', '')
    norm_map = {'I': '1', '|': '1'}
    s = ''.join(norm_map.get(c, c) for c in s)

    province = '京津沪渝冀晋辽吉黑苏浙皖闽赣鲁豫鄂湘粤桂琼川贵云藏陕甘青宁新'
    letter = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    digit = '0123456789'
    valid_all = province + letter + digit
    s = ''.join(c for c in s if c in valid_all)

    if len(s) < 7 or len(s) > 8:
        return ''
    if s[0] not in province:
        return ''

    res = list(s)
    if len(res) >= 2 and res[1] in digit:
        if res[1] == '0':
            res[1] = 'Q'
        elif res[1] == '1':
            res[1] = 'L'
        elif res[1] == '2':
            res[1] = 'Z'
        elif res[1] == '8':
            res[1] = 'B'
    return ''.join(res)


def send_plate(serial_port, plate_text, confidence):
    payload = {
        'plate_text': plate_text,
        'confidence': round(clamp(confidence), 4),
        'timestamp_ms': int(time.time() * 1000),
        'source_id': SOURCE_ID,
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False) + '\r\n').encode('utf-8')
    serial_port.write(payload_bytes)
    print('send bytes:', payload_bytes)


while not app.need_exit():
    img = cam.read()
    plates = detector.detect(img)

    for plate_obj in plates:
        x, y, w, h = plate_obj.x, plate_obj.y, plate_obj.w, plate_obj.h
        img.draw_rect(x, y, w, h, image.COLOR_GREEN, 2)

        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img.width(), x1 + w)
        y2 = min(img.height(), y1 + h)
        plate_img = img.crop(x1, y1, x2 - x1, y2 - y1)

        ocr_objs = ocr.detect(plate_img)
        raw_str = ''.join(obj.char_str() for obj in ocr_objs)
        plate_num = plate_correct(raw_str)

        if plate_num:
            confidence = build_confidence(plate_obj, ocr_objs)
            img.draw_string(x, y - 25, '%s %.2f' % (plate_num, confidence), image.COLOR_GREEN)
            print('recognized plate:', plate_num, 'confidence:', confidence)
            send_plate(serial_ctrl, plate_num, confidence)

    #disp.show(img)
