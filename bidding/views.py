from django.shortcuts import render, redirect
from  django.urls import reverse_lazy
from .models import Category, Item, Bid
from .forms import ItemForm, BidForm
from django.views.generic import DeleteView,UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm



# Create your views here.

def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})

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



def item_detail(request, pk):
    item = Item.objects.get(pk=pk)
    bids = Bid.objects.filter(item=item)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.bidder = request.user
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
    return render(request, 'item_detail.html', {'item': item, 'bids': bids, 'form': form})

class ItemDeleteView(DeleteView):
    model = Item
    template_name = "item_delete.html"
    success_url = reverse_lazy('item_list')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
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
            pass
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('item_list')


