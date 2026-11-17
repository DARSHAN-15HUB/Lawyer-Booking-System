from datetime import timedelta
from .forms import (
    ClientRegisterForm,
    LawyerRegisterForm,
    LawyerDetailsForm,
    AppointmentForm,
    LawyerForm
)
from decimal import Decimal
import razorpay
from django.views.decorators.http import require_POST
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.conf import settings

from .models import Profile, Lawyer, Appointment,Payment
from .forms import ClientRegisterForm, AppointmentForm, LawyerForm
client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)
def home_view(request):
    return HttpResponse("LEGAL EASE IS WORKING!")
def home_view(request):

    lawyers = Lawyer.objects.all()

    context = {
        'lawyers': lawyers
    }

    return render(request, 'booking/home.html', context)

def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = ClientRegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(
                request,
                'Registration successful!'
            )

            return redirect('home')

    else:

        form = ClientRegisterForm()

    return render(
        request,
        'booking/register.html',
        {'form': form}
    )

def login_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            messages.success(
                request,
                'Login successful!'
            )

            return redirect('home')

    else:

        form = AuthenticationForm()

    return render(
        request,
        'booking/login.html',
        {'form': form}
    )

@login_required(login_url='login')
def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have logged out successfully.'
    )

    return redirect('home')

def lawyer_list_view(request):

    lawyers = Lawyer.objects.all()

    return render(
        request,
        'booking/lawyer_list.html',
        {'lawyers': lawyers}
    )



@login_required(login_url='login')
def book_appointment_view(request):

    # 1. Check user profile
    try:
        profile = request.user.profile

    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    # 2. Only clients can book appointments
    if profile.role != 'CLIENT':

        messages.error(
            request,
            'Only clients can book appointments.'
        )

        return redirect('home')

    # 3. Handle appointment form
    if request.method == 'POST':

        form = AppointmentForm(request.POST)

        if form.is_valid():

            appointment = form.save(commit=False)

            # 4. Assign logged-in client
            appointment.client = request.user

            # 5. Check future appointment date
            if appointment.appointment_date <= timezone.now():

                messages.error(
                    request,
                    'Please select a future appointment date.'
                )

            else:

                # 6. Set consultation duration to 30 minutes
                appointment_start = appointment.appointment_date

                appointment_end = (
                    appointment_start + timedelta(minutes=30)
                )

                # 7. Check overlapping appointments
                existing_appointment = Appointment.objects.filter(
                    lawyer=appointment.lawyer,
                    status__in=['PENDING', 'APPROVED'],
                    appointment_date__lt=appointment_end,
                    appointment_date__gt=appointment_start - timedelta(minutes=30)
                ).exists()

                # 8. Reject overlapping booking
                if existing_appointment:

                    messages.error(
                        request,
                        'This time slot is unavailable. Please choose another time.'
                    )

                else:

                    # 9. Save appointment
                    appointment.save()

                    messages.success(
                        request,
                        'Appointment booked successfully!'
                    )

                    return redirect('my_appointments')

    else:

        form = AppointmentForm()

    # 10. Send form to template
    context = {
        'form': form
    }

    return render(
        request,
        'booking/book_appointment.html',
        context
    )





@login_required(login_url='login')
def my_appointments_view(request):

    # Check user profile
    try:
        profile = request.user.profile

    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    # Only clients can access this page
    if profile.role != 'CLIENT':
        messages.error(
            request,
            'Only clients can access their appointments.'
        )
        return redirect('home')

    # Get all appointments
    all_appointments = Appointment.objects.filter(
        client=request.user
    ).select_related(
        'lawyer',
        'lawyer__user'
    ).order_by('-created_at')

    # Search by lawyer username
    search_query = request.GET.get('search', '').strip()

    if search_query:
        all_appointments = all_appointments.filter(
            lawyer__user__username__icontains=search_query
        )

    # Filter by appointment status
    selected_status = request.GET.get('status', '')

    valid_statuses = [
        'PENDING',
        'APPROVED',
        'REJECTED',
        'COMPLETED',
        'CANCELLED'
    ]

    if selected_status in valid_statuses:
        all_appointments = all_appointments.filter(
            status=selected_status
        )

    # Statistics remain independent of search and filters
    client_appointments = Appointment.objects.filter(
        client=request.user
    )

    context = {

        'appointments': all_appointments,

        'total_appointments': client_appointments.count(),

        'pending_count': client_appointments.filter(
            status='PENDING'
        ).count(),

        'approved_count': client_appointments.filter(
            status='APPROVED'
        ).count(),

        'completed_count': client_appointments.filter(
            status='COMPLETED'
        ).count(),

        'rejected_count': client_appointments.filter(
            status='REJECTED'
        ).count(),

        'cancelled_count': client_appointments.filter(
            status='CANCELLED'
        ).count(),

        'search_query': search_query,

        'selected_status': selected_status,
    }

    return render(
        request,
        'booking/my_appointments.html',
        context
    )

@login_required(login_url='login')
def lawyer_dashboard_view(request):

    # Check profile
    try:
        profile = request.user.profile

    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')

    # Check lawyer role
    if profile.role != 'LAWYER':
        messages.error(
            request,
            'You are not authorized to access this page.'
        )
        return redirect('home')

    # Get lawyer details
    try:
        lawyer = request.user.lawyer

    except Lawyer.DoesNotExist:
        messages.error(request, 'Lawyer profile not found.')
        return redirect('home')

    # Get all appointments
    all_appointments = Appointment.objects.filter(
        lawyer=lawyer
    ).order_by('-created_at')

    # Search
    search_query = request.GET.get('search', '').strip()

    if search_query:
        all_appointments = all_appointments.filter(
            client__username__icontains=search_query
        )

    # Status filter
    selected_status = request.GET.get('status', '')

    valid_statuses = [
        'PENDING',
        'APPROVED',
        'REJECTED',
        'COMPLETED',
        'CANCELLED'
    ]

    if selected_status in valid_statuses:
        all_appointments = all_appointments.filter(
            status=selected_status
        )

    # Dashboard statistics
    context = {
        'appointments': all_appointments,

        'total_appointments': Appointment.objects.filter(
            lawyer=lawyer
        ).count(),

        'pending_count': Appointment.objects.filter(
            lawyer=lawyer,
            status='PENDING'
        ).count(),

        'approved_count': Appointment.objects.filter(
            lawyer=lawyer,
            status='APPROVED'
        ).count(),

        'rejected_count': Appointment.objects.filter(
            lawyer=lawyer,
            status='REJECTED'
        ).count(),

        'completed_count': Appointment.objects.filter(
            lawyer=lawyer,
            status='COMPLETED'
        ).count(),

        'cancelled_count': Appointment.objects.filter(
            lawyer=lawyer,
            status='CANCELLED'
        ).count(),

        'search_query': search_query,
        'selected_status': selected_status,
    }

    return render(
        request,
        'booking/lawyer_dashboard.html',
        context
    )

@login_required(login_url='login')
def update_appointment_status_view(request, appointment_id):

    # Get appointment
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    # Check whether the logged-in user owns this lawyer profile
    if appointment.lawyer.user != request.user:

        messages.error(
            request,
            'You are not authorized to update this appointment.'
        )

        return redirect('home')

    # Only POST requests are allowed
    if request.method != 'POST':

        return redirect('lawyer_dashboard')

    # Get requested status
    status = request.POST.get('status')

    # Only pending appointments can be approved or rejected
    if appointment.status == 'PENDING':

        if status in ['APPROVED', 'REJECTED']:

            appointment.status = status
            appointment.save()

            messages.success(
                request,
                f'Appointment {status.lower()} successfully.'
            )

        else:

            messages.error(
                request,
                'Invalid appointment status.'
            )

    # Only approved appointments can be completed
    elif appointment.status == 'APPROVED':

        if status == 'COMPLETED':

            appointment.status = 'COMPLETED'
            appointment.save()

            messages.success(
                request,
                'Appointment marked as completed successfully.'
            )

        else:

            messages.error(
                request,
                'Invalid status update.'
            )

    else:

        messages.error(
            request,
            'This appointment cannot be modified.'
        )

    return redirect('lawyer_dashboard')


@login_required(login_url='login')
def cancel_appointment_view(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        client=request.user
    )

    if request.method == 'POST':

        if appointment.status == 'PENDING':

            appointment.status = 'CANCELLED'

            appointment.save()

            messages.success(
                request,
                'Appointment cancelled successfully.'
            )

        else:

            messages.error(
                request,
                'Only pending appointments can be cancelled.'
            )

    return redirect('my_appointments')

def lawyer_register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        user_form = LawyerRegisterForm(request.POST)

        lawyer_form = LawyerDetailsForm(
            request.POST,
            request.FILES
        )

        if user_form.is_valid() and lawyer_form.is_valid():

            with transaction.atomic():

                user = user_form.save()

                lawyer = lawyer_form.save(commit=False)
                lawyer.user = user
                lawyer.save()

            messages.success(
                request,
                'Lawyer registration successful!'
            )

            login(request, user)

            return redirect('lawyer_dashboard')

    else:

        user_form = LawyerRegisterForm()
        lawyer_form = LawyerDetailsForm()

    context = {
        'user_form': user_form,
        'lawyer_form': lawyer_form
    }

    return render(
        request,
        'booking/lawyer_register.html',
        context
    )

@login_required(login_url='login')
@require_POST
def verify_payment_view(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id,
        appointment__client=request.user
    )

    if payment.status == 'SUCCESS':
        messages.info(request, 'This payment is already verified.')
        return redirect('my_appointments')

    payment_id_from_razorpay = request.POST.get(
        'razorpay_payment_id'
    )

    order_id_from_razorpay = request.POST.get(
        'razorpay_order_id'
    )

    signature_from_razorpay = request.POST.get(
        'razorpay_signature'
    )

    if not all([
        payment_id_from_razorpay,
        order_id_from_razorpay,
        signature_from_razorpay
    ]):
        messages.error(request, 'Payment verification details are missing.')
        return redirect('my_appointments')

    if order_id_from_razorpay != payment.razorpay_order_id:
        messages.error(request, 'Invalid payment order.')
        return redirect('my_appointments')

    try:

        # Verify Razorpay's payment signature.
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id_from_razorpay,
            'razorpay_payment_id': payment_id_from_razorpay,
            'razorpay_signature': signature_from_razorpay
        })

        # Fetch the payment directly from Razorpay.
        razorpay_payment = client.payment.fetch(
            payment_id_from_razorpay
        )

        expected_amount = int(
            payment.amount * Decimal('100')
        )

        if razorpay_payment.get('order_id') != payment.razorpay_order_id:
            messages.error(request, 'Payment order does not match.')
            return redirect('my_appointments')

        if razorpay_payment.get('amount') != expected_amount:
            messages.error(request, 'Payment amount does not match.')
            return redirect('my_appointments')

        if razorpay_payment.get('currency') != 'INR':
            messages.error(request, 'Invalid payment currency.')
            return redirect('my_appointments')

        if razorpay_payment.get('status') != 'captured':
            messages.warning(
                request,
                'Payment is not captured yet. Please contact support if money was deducted.'
            )
            return redirect('my_appointments')

        # Mark payment successful only after verification.
        with transaction.atomic():

            payment.razorpay_payment_id = payment_id_from_razorpay
            payment.razorpay_signature = signature_from_razorpay
            payment.status = 'SUCCESS'

            payment.save()

        messages.success(
            request,
            'Payment completed and verified successfully!'
        )

    except razorpay.errors.SignatureVerificationError:

        messages.error(
            request,
            'Payment signature verification failed.'
        )

    except Exception:

        messages.error(
            request,
            'Unable to verify payment. Please contact support.'
        )

    return redirect('my_appointments')

@login_required(login_url='login')
def create_payment_view(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        client=request.user
    )

    if appointment.status != 'APPROVED':
        messages.error(request, 'Appointment is not approved yet.')
        return redirect('my_appointments')

    amount = appointment.lawyer.consultation_fee

    commission_rate = Decimal('5.00')

    commission = (
        amount * commission_rate / Decimal('100')
    ).quantize(Decimal('0.01'))

    lawyer_amount = amount - commission

    payment, created = Payment.objects.get_or_create(
        appointment=appointment,
        defaults={
            'amount': amount,
            'platform_commission_rate': commission_rate,
            'platform_commission': commission,
            'lawyer_amount': lawyer_amount,
            'status': 'PENDING'
        }
    )

    if payment.status == 'SUCCESS':
        messages.info(request, 'This appointment is already paid.')
        return redirect('my_appointments')

    if payment.razorpay_order_id:
        messages.info(request, 'A payment order already exists. Please continue with it.')
        razorpay_order_id = payment.razorpay_order_id
        razorpay_amount = int(payment.amount * Decimal('100'))

    else:
        razorpay_amount = int(amount * Decimal('100'))

        try:
            razorpay_order = client.order.create({
                'amount': razorpay_amount,
                'currency': 'INR',
                'receipt': f'appointment_{appointment.id}'
            })

            razorpay_order_id = razorpay_order['id']

            payment.razorpay_order_id = razorpay_order_id
            payment.save()

        except Exception:
            messages.error(request, 'Unable to create Razorpay order.')
            return redirect('my_appointments')

    context = {
        'payment': payment,
        'appointment': appointment,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_order_amount': razorpay_amount,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }

    return render(request, 'booking/payment.html', context)

