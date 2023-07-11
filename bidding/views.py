from django.shortcuts import render, redirect
from .models import Category, Item, Bid
from .forms import ItemForm, BidForm

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

