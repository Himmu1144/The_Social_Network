from django.shortcuts import render, redirect
from account.forms import RegistrationForm, AccountAuthenticationForm , AccountUpdateForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout 
from account.models import Account
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64
# import requests
from django.core import files
from friend.models import FriendList , FriendRequest
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus

# Create your views here.


TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

def register_view(request, *args, **kwargs):

    user = request.user
    context = {}
    if user.is_authenticated:
        return HttpResponse(f'You are already authenticated as {user.username} with email - {user.email}')

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            email = form.cleaned_data['email'].lower()
            raw_password = form.cleaned_data['password1']
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            destination = kwargs.get('next')
            if destination:
                return redirect(destination)
            else:
                return redirect('home')
        else:
            context['registration_form'] = form

    else:
        form = RegistrationForm()
        context['registration_form'] = form

    return render(request, 'account/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request, *args, **kwargs):

    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = kwargs.get('next')
                if destination:
                    return redirect(destination)
                else:
                    return redirect('home')
        else:
            context['login_form'] = form

    return render(request, 'account/login.html', context)


def account_view(request, *args, **kwargs):

    context = {}
    user_id = kwargs.get('user_id')
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse('Bhaya, Yeah Account Exist Nhi Karta Hai Bhaya')
    if account:
        context['id'] = account.id
        context['email'] = account.email
        context['username'] = account.username
        context['profile_image'] = account.profile_image.url
        context['hide_email'] = account.hide_email

        try:
            friend_list =  FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()

        friends =  friend_list.friends.all()
        context['friends'] = friends
        friend_requests = None


        is_self = True
        is_friend = False
        user = request.user
        request_sent = None

        if user.is_authenticated and user != account:
            is_self = False
            if friends.filter(pk=user.pk):
                is_friend = True
            else:
                is_friend = False
                if get_friend_request_or_false(sender=account, receiver=user) != False:
                    # Them_sent_to_you
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).pk
                elif get_friend_request_or_false(sender=user, receiver=account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                else:
                    # No_request_sent
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except:
                pass

        # Set the template variables to the values
        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests
        context['BASE_URL'] = settings.BASE_URL

    return render(request, 'account/account.html', context)


def account_search_view(request, *args, **kwargs):

    user = request.user

    if not user.is_authenticated:
        return HttpResponse('kya Bhaya? Search Krne se pehle login toh karo!')

    context = {}
    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            
            search_results = Account.objects.filter(email__icontains=search_query).filter(
            username__icontains=search_query).distinct()
            print(search_results)
            user = request.user
            accounts = []  # [(account1, True), (account2, False), ...]
            if user.is_authenticated and search_results:
				# get the authenticated users friend list
                
                auth_user_friend_list = FriendList.objects.filter(user=user).first()
                
                for account in search_results:
                    accounts.append((account, auth_user_friend_list.is_mutual(account)))
                context['accounts'] = accounts
            else:
                for account in search_results:
                    accounts.append((account, False))
                context['accounts'] = accounts
    
    return render(request, "account/search_results.html", context)
    


def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse('kya Bhaya!, yeah account exist nhi karta hai bhaya.')
    if account.pk != request.user.pk:
        return HttpResponse("Bhaya don't be oversmart , You cannot edit someone elses profile.")
    context = {}

    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # account.profile_image.delete()
            form.save()
            return redirect('account:view', user_id=account.pk)
        else:
            # return HttpResponse('error')
            form = AccountUpdateForm(request.POST, request.FILES,
            initial = {
                "id": account.pk,
                "email": account.email, 
                "username": account.username,
                "profile_image": account.profile_image,
                "hide_email": account.hide_email,
            } )
            context['form'] = form
    else:
        form = AccountUpdateForm(
            initial = {
                "id": account.pk,
                "email": account.email, 
                "username": account.username,
                "profile_image": account.profile_image,
                "hide_email": account.hide_email,
            } )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE    
    return render(request, 'account/edit_account.html',context)

def save_temp_profile_image_from_base64String(imageString, user):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		if not os.path.exists(settings.TEMP):
			os.mkdir(settings.TEMP)
		if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
			os.mkdir(settings.TEMP + "/" + str(user.pk))
		url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
		storage = FileSystemStorage(location=url)
		image = base64.b64decode(imageString)
		with storage.open('', 'wb+') as destination:
			destination.write(image)
			destination.close()
		return url
	except Exception as e:
		print("exception: " + str(e))
		# workaround for an issue I found
		if str(e) == INCORRECT_PADDING_EXCEPTION:
			imageString += "=" * ((4 - len(imageString) % 4) % 4)
			return save_temp_profile_image_from_base64String(imageString, user)
	return None


def crop_image(request, *args, **kwargs):
	payload = {}
	user = request.user
	if request.POST and user.is_authenticated:
		try:
			imageString = request.POST.get("image")
			url = save_temp_profile_image_from_base64String(imageString, user)
			img = cv2.imread(url)

			cropX = int(float(str(request.POST.get("cropX"))))
			cropY = int(float(str(request.POST.get("cropY"))))
			cropWidth = int(float(str(request.POST.get("cropWidth"))))
			cropHeight = int(float(str(request.POST.get("cropHeight"))))
			if cropX < 0:
				cropX = 0
			if cropY < 0: # There is a bug with cropperjs. y can be negative.
				cropY = 0
			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]

			cv2.imwrite(url, crop_img)

			# delete the old image
			user.profile_image.delete()

			# Save the cropped image to user model
			user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
			user.save()

			payload['result'] = "success"
			payload['cropped_profile_image'] = user.profile_image.url

			# delete temp file
			os.remove(url)

		except Exception as e:
			print("exception: " + str(e))
			payload['result'] = "error"
			payload['exception'] = str(e)
	return HttpResponse(json.dumps(payload), content_type="application/json")