from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib import messages
import qrcode
from .models import Ticket, ScanLog
import cv2
import numpy as np
from django.utils import timezone

def index(request):
    return render(request, 'main/index.html')


def generate_qr(request):
    qr_image_data = None
    ticket_code = None

    if request.method == 'POST':
        # Създаваме нов билет при генериране
        event_name = request.POST.get('event_name', 'Събитие по подразбиране')
        new_ticket = Ticket.objects.create(event_name=event_name)
        ticket_code = str(new_ticket.code)

        # Генериране на самия QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(ticket_code)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Запазваме изображението в паметта, за да го пратим към шаблона
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        import base64
        qr_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'main/generate.html', {
        'qr_image_data': qr_image_data,
        'ticket_code': ticket_code
    })


def scan_qr(request):
    scan_result = False
    scan_success = False
    message = ""
    scanned_code = ""

    if request.method == 'POST' and request.FILES.get('qr_image'):
        scan_result = True
        qr_file = request.FILES['qr_image']

        # Четем файла от паметта, за да го подадем на OpenCV
        file_bytes = np.asarray(bytearray(qr_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            message = "Грешка: Каченият файл не е валидно изображение."
        else:
            # Използваме вградения QR детектор на OpenCV
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)

            if data:
                scanned_code = data
                # Проверка в базата данни дали билетът съществува
                try:
                    ticket = Ticket.objects.get(code=data)

                    if ticket.is_used:
                        message = f"ВНИМАНИЕ: Билетът вече е ИЗПОЛЗВАН на {ticket.used_at.strftime('%d.%m.%Y %H:%M')}!"
                        scan_success = False
                    else:
                        # Маркираме го като използван
                        ticket.is_used = True
                        ticket.used_at = timezone.now()
                        ticket.save()

                        message = f"УСПЕХ: Билетът за '{ticket.event_name}' е ВАЛИДЕН и току-що бе маркиран като използван."
                        scan_success = True

                except Ticket.DoesNotExist:
                    message = "ГРЕШКА: Невалиден билет! Този код не съществува в системата."
                    scan_success = False
            else:
                message = "В качената снимка не беше открит или разчетен QR код."

                # Записваме опита за сканиране в историята (ScanLog)
        ScanLog.objects.create(
            scanned_text=scanned_code if scanned_code else "Неразчетен файл",
            is_successful=scan_success,
            message=message
        )

    return render(request, 'main/scan.html', {
        'scan_result': scan_result,
        'scan_success': scan_success,
        'message': message,
        'scanned_code': scanned_code
    })


def history(request):
    logs = ScanLog.objects.all().order_by('-scanned_at')
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'main/history.html', {'logs': logs, 'tickets': tickets})