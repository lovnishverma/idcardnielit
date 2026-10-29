import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from django.conf import settings

CARD_DIR = Path(__file__).resolve().parent
DEFAULT_FONT_PATH = str(CARD_DIR / "MartianMono_SemiCondensed-Regular.ttf")


def get_download_dir():
    download_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def get_temp_dir():
    temp_dir = os.path.join(settings.BASE_DIR, 'static', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def draw_autofit_text(draw, position, text, max_width, initial_size=20, min_size=10, font_color=(0, 0, 0), font_path=DEFAULT_FONT_PATH):
    """
    Renders text onto a PIL Draw canvas, auto-scaling font size down from initial_size to min_size
    so it fits within max_width. If it still exceeds at min_size, truncates with ellipsis.
    """
    text = str(text if text is not None else "").strip()
    if not text:
        return

    chosen_font = None
    for size in range(initial_size, min_size - 1, -1):
        f = ImageFont.truetype(font_path, size=size)
        bbox = draw.textbbox((0, 0), text, font=f)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            chosen_font = f
            break

    if not chosen_font:
        chosen_font = ImageFont.truetype(font_path, size=min_size)
        while len(text) > 3:
            bbox = draw.textbbox((0, 0), text + "...", font=chosen_font)
            if bbox[2] - bbox[0] <= max_width:
                text = text + "..."
                break
            text = text[:-1]

    draw.text(position, text, font=chosen_font, fill=font_color)


def write_front_text(NAME, ID, EMAIL, PHONE, TEMPLATE_PATH):
    pil_image = Image.open(str(TEMPLATE_PATH)).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    fields = [
        ((250, 656), NAME, 315),
        ((250, 708), ID, 315),
        ((250, 760), EMAIL, 315),
        ((250, 812), PHONE, 315),
    ]

    for pos, val, max_w in fields:
        draw_autofit_text(draw, pos, val, max_w)

    output_image_path = os.path.join(get_temp_dir(), f"{ID}_front.jpg")
    pil_image.save(output_image_path, "JPEG", quality=95)
    return output_image_path


def write_text_back(DEPT, JOINING, ENDING, TEMPLATE_PATH, ID):
    pil_image = Image.open(str(TEMPLATE_PATH)).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    if not isinstance(JOINING, str) and JOINING:
        JOINING = JOINING.strftime("%d-%m-%Y")
    if not isinstance(ENDING, str) and ENDING:
        ENDING = ENDING.strftime("%d-%m-%Y")

    fields = [
        ((360, 665), DEPT, 205),
        ((360, 715), JOINING, 205),
        ((360, 765), ENDING, 205),
    ]

    for pos, val, max_w in fields:
        draw_autofit_text(draw, pos, val, max_w)

    output_image_path = os.path.join(get_temp_dir(), f"{ID}_back.jpg")
    pil_image.save(output_image_path, "JPEG", quality=95)
    return output_image_path


def write_front_image(IMG, ID):
    temp_image_path = os.path.join(get_temp_dir(), f"{ID}_front.jpg")
    if not os.path.exists(temp_image_path):
        temp_image_path = f"{ID}_front.jpg"

    output_image_path = os.path.join(get_download_dir(), f"{ID}_front.jpg")

    if not os.path.exists(temp_image_path):
        print(f"Error: Temporary front image {temp_image_path} not found.")
        return

    if not IMG:
        try:
            import shutil
            shutil.copyfile(temp_image_path, output_image_path)
            os.remove(temp_image_path)
        except OSError:
            pass
        return

    try:
        nparr = np.frombuffer(IMG, np.uint8)
        profile_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        existing_image = cv2.imread(temp_image_path)
        if existing_image is not None and profile_image is not None:
            pil_existing_image = Image.fromarray(cv2.cvtColor(existing_image, cv2.COLOR_BGR2RGB))
            existing_image_width, existing_image_height = pil_existing_image.size

            custom_width = 215
            custom_height = 274
            profile_image_resized = cv2.resize(profile_image, (custom_width, custom_height))

            new_image_x = (existing_image_width - custom_width) // 2
            x_start = new_image_x
            x_end = new_image_x + custom_width
            y_start = 345
            y_end = 345 + custom_height
            existing_image[y_start:y_end, x_start:x_end] = profile_image_resized

            cv_image_with_text = cv2.cvtColor(existing_image, cv2.COLOR_BGR2RGB)
            pil_image_with_text = Image.fromarray(cv_image_with_text)
            pil_image_with_text.save(output_image_path, "JPEG", quality=95)
        else:
            import shutil
            shutil.copyfile(temp_image_path, output_image_path)

        if os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except OSError:
                pass
    except Exception as e:
        print(f"Error in write_front_image for {ID}: {e}")


def write_qr(QR_PATH, ID):
    temp_image_path = os.path.join(get_temp_dir(), f"{ID}_back.jpg")
    if not os.path.exists(temp_image_path):
        temp_image_path = f"{ID}_back.jpg"

    if not os.path.exists(temp_image_path):
        return

    try:
        existing_image = cv2.imread(temp_image_path)
        profile_image = cv2.imread(QR_PATH)

        if existing_image is not None and profile_image is not None:
            pil_existing_image = Image.fromarray(cv2.cvtColor(existing_image, cv2.COLOR_BGR2RGB))
            existing_image_width, existing_image_height = pil_existing_image.size

            custom_width = 350
            custom_height = 350
            profile_image_resized = cv2.resize(profile_image, (custom_width, custom_height))

            new_image_x = (existing_image_width - custom_width) // 2
            x_start = new_image_x
            x_end = new_image_x + custom_width
            y_start = 280
            y_end = 280 + custom_height
            existing_image[y_start:y_end, x_start:x_end] = profile_image_resized

            cv_image_with_text = cv2.cvtColor(existing_image, cv2.COLOR_BGR2RGB)
            pil_image_with_text = Image.fromarray(cv_image_with_text)

            output_image_path = os.path.join(get_download_dir(), f"{ID}_back.jpg")
            pil_image_with_text.save(output_image_path, "JPEG", quality=95)
    finally:
        for p in [QR_PATH, temp_image_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def write_front_text_student(NAME, ID, COURSE, BRANCH, PHONE, TEMPLATE_PATH):
    pil_image = Image.open(str(TEMPLATE_PATH)).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    fields = [
        ((280, 648), NAME, 285),
        ((280, 690), ID, 285),
        ((280, 732), COURSE, 285),
        ((280, 774), BRANCH, 285),
        ((280, 816), PHONE, 285),
    ]

    for pos, val, max_w in fields:
        draw_autofit_text(draw, pos, val, max_w)

    output_image_path = os.path.join(get_temp_dir(), f"{ID}_front.jpg")
    pil_image.save(output_image_path, "JPEG", quality=95)
    return output_image_path


def write_text_back_student(BATCH, VALID_FROM, VALID_UPTO, ADDRESS1, ADDRESS2, TEMPLATE_PATH, ID):
    pil_image = Image.open(str(TEMPLATE_PATH)).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    if not isinstance(VALID_FROM, str) and VALID_FROM:
        VALID_FROM = VALID_FROM.strftime("%d-%m-%Y")
    if not isinstance(VALID_UPTO, str) and VALID_UPTO:
        VALID_UPTO = VALID_UPTO.strftime("%d-%m-%Y")

    fields = [
        ((300, 637), BATCH, 265),
        ((300, 677), VALID_FROM, 265),
        ((300, 717), VALID_UPTO, 265),
        ((300, 760), ADDRESS1, 265),
        ((300, 800), ADDRESS2, 265),
    ]

    for pos, val, max_w in fields:
        draw_autofit_text(draw, pos, val, max_w)

    output_image_path = os.path.join(get_temp_dir(), f"{ID}_back.jpg")
    pil_image.save(output_image_path, "JPEG", quality=95)
    return output_image_path


def write_qr_student(QR_PATH, ID):
    temp_image_path = os.path.join(get_temp_dir(), f"{ID}_back.jpg")
    if not os.path.exists(temp_image_path):
        temp_image_path = f"{ID}_back.jpg"

    if not os.path.exists(temp_image_path):
        return

    try:
        existing_image = cv2.imread(temp_image_path)
        profile_image = cv2.imread(QR_PATH)

        if existing_image is not None and profile_image is not None:
            pil_existing_image = Image.fromarray(cv2.cvtColor(existing_image, cv2.COLOR_BGR2RGB))
            existing_image_width, existing_image_height = pil_existing_image.size

            custom_width = 325
            custom_height = 325
            profile_image_resized = cv2.resize(profile_image, (custom_width, custom_height))

            new_image_x = (existing_image_width - custom_width) // 2
            x_start = new_image_x
            x_end = new_image_x + custom_width
            y_start = 280
            y_end = 280 + custom_height
            existing_image[y_start:y_end, x_start:x_end] = profile_image_resized

            cv_image_with_text = cv2.cvtColor(existing_image, cv2.COLOR_BGR2RGB)
            pil_image_with_text = Image.fromarray(cv_image_with_text)

            output_image_path = os.path.join(get_download_dir(), f"{ID}_back.jpg")
            pil_image_with_text.save(output_image_path, "JPEG", quality=95)
    finally:
        for p in [QR_PATH, temp_image_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
