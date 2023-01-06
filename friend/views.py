from django.shortcuts import render, redirect
from django.http import HttpResponse
from account.models import Account
from friend.models import FriendRequest , FriendList
import json

# Create your views here.

def friend_requests(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get('user_id')
        account = Account.objects.get(pk=user_id)
        if account == user:
            friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            context['friend_requests'] = friend_requests
        else:
            return HttpResponse('Kya Bhaya, Aese kisi aur ki friend req list thodi dekhte hai bhaya!')

    else:
        return redirect('login')
        
    return render(request, 'friend/friend_requests.html', context)

def send_friend_request(request, *args, **kwargs):

    user = request.user
    payload = {}
    sent = 'Friend Request Sent.'
    payload['sent'] = sent
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                for request in friend_requests:
                    if request.is_active:
                        raise Exception('Kya Bhaya , You have already sent the request bhaya.')
                friend_request = FriendRequest(sender=user,receiver=receiver)
                friend_request.save()
                payload['response'] = sent
            except FriendRequest.DoesNotExist:
                friend_request = FriendRequest(sender=user,receiver=receiver)
                friend_request.save()
                payload['response'] = sent
            
        else:
            payload['response'] = "Bhaya, jis person ko friend request bhej rahe ho vo exist nhi karta bhaya!"
    
    else:
        payload['response'] = 'you must be authenticated to send a friend request.'
    return HttpResponse(json.dumps(payload), content_type="application/json")

def accept_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}

    if request.method == 'GET' and user.is_authenticated:
        friend_request_id = kwargs.get('friend_request_id')
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver == user:
                jabba = friend_request.accept()
                payload['response'] = 'Friend Request Accepted!'
            else:
                return HttpResponse('Bhaya, you just can not accept someone elses request')
        else:
            payload['response'] = 'This request does not exist!'
    else:
        payload['response'] = 'something went horriblly wrong!'
    return HttpResponse(json.dumps(payload), content_type="application/json")

def remove_friend(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')
        if user_id:
            try:
                removee = Account.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee=removee)
                payload['response'] = "Successfully removed the friend."
            except Exception as e:
                payload['response'] = 'Something went wrong ' + str(e)
        else:
            payload['response'] = 'Jis vyakti ko aap sampark karna chahate hai vo exist nhi krte hai!'
    else:
        payload['response'] = 'How did you even get here!'
    return HttpResponse(json.dumps(payload), content_type="application/json")

def decline_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		friend_request_id = kwargs.get("friend_request_id")
		if friend_request_id:
			friend_request = FriendRequest.objects.get(pk=friend_request_id)
			# confirm that is the correct request
			if friend_request.receiver == user:
				if friend_request: 
					# found the request. Now decline it
					updated_notification = friend_request.decline()
					payload['response'] = "Friend request declined."
				else:
					payload['response'] = "Something went wrong."
			else:
				payload['response'] = "That is not your friend request to decline."
		else:
			payload['response'] = "Unable to decline that friend request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to decline a friend request."
	return HttpResponse(json.dumps(payload), content_type="application/json")

def cancel_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receiver_user_id")
		if user_id:
			receiver = Account.objects.get(pk=user_id)
			try:
				friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
			except FriendRequest.DoesNotExist:
				payload['response'] = "Nothing to cancel. Friend request does not exist."

			# There should only ever be ONE active friend request at any given time. Cancel them all just in case.
			if len(friend_requests) > 1:
				for request in friend_requests:
					request.cance()
				payload['response'] = "Friend request canceled."
			else:
				# found the request. Now cancel it
				friend_requests.first().cancel()
				payload['response'] = "Friend request canceled."
		else:
			payload['response'] = "Unable to cancel that friend request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to cancel a friend request."
	return HttpResponse(json.dumps(payload), content_type="application/json")

def friends_list_view(request, *args, **kwargs):
    user = request.user
    context = {}
    if user.is_authenticated:
        user_id = kwargs.get('user_id')
        if user_id:
            try:
                this_user = Account.objects.get(pk=user_id)
            except Account.DoesNotExist:
                return HttpResponse("That user does not exist.")
            try:
                friend_list = FriendList.objects.get(user=this_user)
            except FriendList.DoesNotExist:
                return HttpResponse(f"Could not find a friends list for {this_user.username}")
            
            if user != this_user:
                if not(user in friend_list.friends.all()):
                    return HttpResponse("You must be friends to view their friends list.")
            
            friends = []
            auth_user_friend_list = FriendList.objects.get(user=user)
            for friend in friend_list.friends.all():
                friends.append((friend,auth_user_friend_list.is_mutual(friend)))
            context['friends'] = friends
    else:		
        return HttpResponse("You must be authenticated to view friends.")
    return render(request, "friend/friend_list.html", context)