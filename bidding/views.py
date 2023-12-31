from django.shortcuts import render, redirect,get_object_or_404
from  django.urls import reverse_lazy
from .models import Category, Item, Bid
from .forms import ItemForm, BidForm
from django.views.generic import DeleteView,UpdateView,ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages



# Create your views here.

def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})

class CategoryListView(ListView):
    # This view will display a list of categories
    model = Category
    template_name = "category_list.html"

def item_catagory(request, id):
    items= Item.objects.filter(category=Category.objects.get(id=id))
    return render(request, 'category.html', {'items': items})
    

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'item_create.html', {'form': form})

class ItemUpdateView(UpdateView):
    model = Item
    template_name = 'item_update.html'
    fields =['name','description','image','starting_bid']
    def get_object(self, *args, **kwargs):
        item = super().get_object(*args, **kwargs)
        if item.seller != self.request.user:
            raise PermissionDenied()
        return item

def is_item_owner (user, item_id):
  # Get the item object from the database
  item = Item.objects.get (id=item_id)
  # Return True if the user is the owner, False otherwise
  return user == item.seller

def item_detail(request, pk):
    item = Item.objects.get(pk=pk)
    is_owner = is_item_owner (request.user, item.pk)
    
    bids = Bid.objects.filter(item=item)
    if request.method == 'POST':
        if is_owner or not item.isActive:
            return HttpResponseForbidden()
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            try:
                bid.bidder = request.user
            except ValueError:
                raise PermissionDenied()
            bid.item = item
            if not item.current_bid or bid.amount > item.current_bid:
                item.current_bid = bid.amount
                item.save()
                bid.save()
                return redirect('item_detail', pk=pk)
            else:
                form.add_error('amount', 'Bid must be higher than current bid')
                
    else:
        form = BidForm()
        highest_bid = Bid.objects.filter(item=item).order_by('-amount').first()
        if highest_bid:
            bidder = highest_bid.bidder
            bidder_username = bidder.username
            if request.user == bidder and item.isActive == False:
                message = f'Congratulations {bidder_username}! You have won {item.name} with a bid of {item.current_bid}.'
                messages.success(request, message)
        
    return render(request, 'item_detail.html', {'item': item, 'bids': bids, 'form': form, 'is_owner': is_owner})
@login_required # new view function
@require_POST
def close_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    is_owner = is_item_owner (request.user, item.pk)
    if is_owner == False:
            return HttpResponseForbidden()
    # set item as inactive
    else:
        item.isActive = False
        item.save()
        # redirect to same page with confirmation message
        return redirect('item_detail', pk=pk)

class ItemDeleteView(DeleteView):
    model = Item
    template_name = "item_delete.html"
    success_url = reverse_lazy('item_list')
    def get_object(self, *args, **kwargs):
        item = super().get_object(*args, **kwargs)
        if item.seller != self.request.user:
            raise PermissionDenied()
        return item

def search(request):
    query = request.GET.get('q')
    if  Item.objects.filter(name__exact=query):
        result = Item.objects.get(name=query)
        return render(request,"results.html",{"result":result})
    else:
       recommended = Item.objects.filter(name__icontains=query)
       return render(request,"recommended.html",{"recommendations":recommended})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = password)
            login(request, user)
            return redirect('item_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('item_list')
        else:
            # Return an 'invalid login' error message.
            # Generate a random message for wrong password
            messages = [
                "Oops, that's not it.",
                "Try again, maybe you'll get lucky.",
                "Nope, not even close.",
                "You call that a password?",
                "Are you even trying?",
                "That's not the password, that's your name.",
                "Wrong password, but nice try.",
                "I'm sorry, Dave. I'm afraid I can't do that.",
                "Access denied. Please contact your system administrator.",
                "You have entered an incorrect password. Please enter the correct password."
            ]
            import random
            message = random.choice(messages)
            # Add the message to the context and render the login template
            context = {"message": message}
            return render(request, "login.html", context)
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('item_list')


