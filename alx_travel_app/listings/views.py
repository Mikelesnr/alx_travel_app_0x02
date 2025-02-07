import requests
import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from .models import Listing, Booking,Payment
from .serializers import ListingSerializer, BookingSerializer
from django.views.decorators.csrf import csrf_exempt
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

@csrf_exempt
def initiate_payment(request):
    booking_reference = request.POST.get('booking_reference')
    amount = request.POST.get('amount')
    email = request.POST.get('email')  # Collect email as required
    first_name = request.POST.get('first_name', 'First Name')  # Optional, provide default
    last_name = request.POST.get('last_name', 'Last Name')    # Optional, provide default
    phone_number = request.POST.get('phone_number', '0912345678')  # Optional, provide default

    if not booking_reference or not amount or not email:
        logger.error('Missing booking reference, amount, or email')
        return JsonResponse({'error': 'Missing booking reference, amount, or email'}, status=400)

    chapa_url = 'https://api.chapa.co/v1/transaction/initialize'
    headers = {
        'Authorization': f'Bearer {os.getenv("CHAPA_SECRET_KEY")}',
        'Content-Type': 'application/json',
    }
    payload = {
        'amount': amount,
        'currency': 'ETB',
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'phone_number': phone_number,
        'tx_ref': booking_reference,
        'callback_url': 'http://localhost:8000/api/payment/verify/',
        'return_url': 'http://localhost:8000/payment/success/',
        'customization': {
            'title': 'Payment',  # Ensure the title is 16 characters or fewer
            'description': 'Pay for your booking at ALX Travel App'
        },
    }

    try:
        response = requests.post(chapa_url, headers=headers, json=payload)
        response_data = response.json()
        logger.debug(f"Chapa API response: {response_data}")

        if response_data.get('status') == 'failed':
            logger.error(f"Chapa API Error: {response_data.get('message')}")
            return JsonResponse({'error': response_data.get('message')}, status=400)

        data = response_data.get('data')
        if not data or not data.get('checkout_url'):
            logger.error('Checkout URL not returned by Chapa')
            return JsonResponse({'error': 'Checkout URL not returned by Chapa', 'response': response_data}, status=400)

        checkout_url = data['checkout_url']

        payment = Payment(
            booking_reference=booking_reference,
            amount=amount,
            transaction_id=checkout_url,
            payment_status='Pending'
        )
        payment.save()

        logger.debug(f"Payment initiated: {payment}")
        return JsonResponse({'checkout_url': checkout_url})

    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        return JsonResponse({'error': 'Error initiating payment'}, status=500)

def verify_payment(request):
    tx_ref = request.GET.get('tx_ref')
    if not tx_ref:
        logger.error('Missing transaction reference')
        return JsonResponse({'error': 'Missing transaction reference'}, status=400)

    try:
        chapa_url = f'https://api.chapa.co/v1/transaction/verify/{tx_ref}'
        headers = {
            'Authorization': f'Bearer {os.getenv("CHAPA_SECRET_KEY")}'
        }

        response = requests.get(chapa_url, headers=headers)
        response_data = response.json()
        logger.debug(f"Chapa API response: {response_data}")

        if response_data.get('status') == 'success':
            payment_status = response_data['data']['status']
            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
                payment.payment_status = payment_status
                payment.save()
                logger.debug(f"Payment verified: {payment}")
                return JsonResponse({'status': 'Payment verified', 'payment_status': payment_status})
            except Payment.DoesNotExist:
                logger.error('Payment not found')
                return JsonResponse({'error': 'Payment not found'}, status=404)
        else:
            logger.error('Verification failed')
            return JsonResponse({'error': 'Verification failed', 'response': response_data}, status=400)
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return JsonResponse({'error': 'Error verifying payment'}, status=500)

def payment_success(request):
    tx_ref = request.GET.get('tx_ref')
    if not tx_ref:
        return JsonResponse({'error': 'Missing transaction reference'}, status=400)

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
        payment_details = {
            'booking_reference': payment.booking_reference,
            'amount': payment.amount,
            'transaction_id': payment.transaction_id,
            'payment_status': payment.payment_status,
        }
        return JsonResponse({'status': 'success', 'payment_details': payment_details})
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)

def home(request):
    return HttpResponse("Welcome to ALX Travel App!")

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer