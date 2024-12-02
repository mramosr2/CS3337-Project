from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Favorite
# Create your views here.
from .models import MainMenu

from .forms import BookForm
from django.http import HttpResponseRedirect

from .models import Book, Rating

from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.db.models import Q
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .models import Book, Comment


def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })


def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():

            # form.save()
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()

            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted
                  })


def displaybooks(request):
    query = request.GET.get('q', '')  # Retrieve search term, default to empty string if not provided
    if query:
        books = Book.objects.filter(name__icontains=query)
    else:
        books = Book.objects.all()


    for b in books:
        b.pic_path = b.picture.url[14:]
        b.avg_rating = b.ratings.aggregate(Avg('rating'))['rating__avg']
        b.rating_count = b.ratings.count()
        user_rating = b.ratings.filter(user=request.user).first()
        b.user_rating = user_rating.rating if user_rating else None

    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                      'query': query
                  })

@login_required(login_url='login')
def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books,
                  })


@login_required(login_url='login')
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.pic_path = book.picture.url[14:]

    book.avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']

    user_rating = book.ratings.filter(user=request.user).first()
    book.user_rating = user_rating.rating if user_rating else None

    if request.method == 'POST':
        # Create a new comment
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(book=book, user=request.user, text=text)
            return redirect('book_detail', book_id=book_id)

    return render(request,
                  'bookMng/book_detail.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                  })



def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    return render(request,
                  'bookMng/book_delete.html',
                  {
                      'item_list': MainMenu.objects.all(),
                  })

def about(request):
    return render(request, 'bookMng/about.html', {
        'item_list': MainMenu.objects.all(),
    })
@login_required(login_url='login')
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'bookMng/favorite_list.html', {
        'item_list': MainMenu.objects.all(),
        'favorites': favorites,
    })
@login_required(login_url='login')
def add_to_favorites(request, book_id):
    book = Book.objects.get(id=book_id)
    Favorite.objects.get_or_create(user=request.user, book=book)
    return HttpResponseRedirect('/favorites/')
def remove_from_favorites(request, book_id):
    book = Book.objects.get(id=book_id)
    Favorite.objects.filter(user=request.user, book=book).delete()
    return HttpResponseRedirect('/favorites/')

def search_books(request):
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(Q(name__icontains=query))
    else:
        books = Book.objects.all()

    return render(request, 'bookMng/displaybooks.html', {
        'item_list': MainMenu.objects.all(),
        'books': books,
        'query': query,
    })


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)

def rate_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if the user has already rated this book
    rating = Rating.objects.filter(book=book, user=request.user).first()

    if request.method == 'POST':
        # Get the new rating value from the POST request
        new_rating = int(request.POST['rating'])

        if rating:
            # If a rating already exists, update it
            rating.rating = new_rating
            rating.save()
        else:
            # If no rating exists, create a new one
            rating = Rating(book=book, user=request.user, rating=new_rating)
            rating.save()

        avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']
        book.avg_rating = avg_rating
        book.save()

        return redirect('displaybooks')
    return redirect('displaybooks')
