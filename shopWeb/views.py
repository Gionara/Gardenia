from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Producto, Categoria, SubCategoria
from .forms import ProductoForm

# Create your views here.

#INDEX

def index(request):
    return render(request, 'shopWeb/index.html')

# REGISTER
def register(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verificar si el email ya está registrado
        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo electrónico ya está registrado, por favor inicie sesión.")
            return render(request, 'shopWeb/register.html')
        else:
            # Si el email no está registrado, procede a crear el usuario
            user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre, last_name=apellido)
            user.save()
            return JsonResponse({'error': False, 'redirect_url': '/shopWeb/index'})

    # Borra cualquier mensaje previo antes de renderizar la página de registro
    messages.used = True

    return render(request, 'shopWeb/register.html')

# LOGIN
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verificar si el usuario existe
        user = User.objects.filter(username=email).first()
        if user is None:
            return JsonResponse({'error': True, 'field': 'email', 'message': "El correo electrónico no está registrado."})

        # Verificar si la contraseña es correcta
        if not user.check_password(password):
            return JsonResponse({'error': True, 'field': 'password', 'message': "La contraseña es incorrecta."})

        # Iniciar sesión si el usuario y contraseña son válidos
        login(request, user)
        return JsonResponse({'error': False, 'message': "Inicio de sesión exitoso."})

    return JsonResponse({'error': True, 'message': "Método no permitido."})
 
# LOGOUT
def logout_view(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))
# INFO 
def politicas(request):
    return render(request, 'shopWeb/info/politicas.html')

def sobre_nosotros(request):
    return render(request,'shopWeb/info/sobre_nosotros.html')

#PERFIL 

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene al usuario logueado después del cambio de contraseña
            return JsonResponse({'error': False, 'message': '¡Tu contraseña ha sido actualizada correctamente!'})
        else:
            errors = {}
            for field in form.errors:
                errors[field] = form.errors[field][0]
            return JsonResponse({'error': True, 'errors': errors})
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'shopWeb/perfil/profile.html', {'user': user, 'form': form})



#PRODUCTOS

def all_products(request):
    return render(request, 'shopWeb/productos/all_products.html')

#CATEGORIA HERRAMIENTAS
def cat_herramientas(request):
    return render(request, 'shopWeb/productos/cat_herramientas/cat_herramientas.html')

def palas(request):
    return render(request, 'shopWeb/productos/cat_herramientas/palas.html')

def tijeras(request):
    return render(request, 'shopWeb/productos/cat_herramientas/tijeras.html')

def otras_herramientas(request):
    return render(request, 'shopWeb/productos/cat_herramientas/otras_herramientas.html')

#CATEGORIA PLANTAS Y SEMILLAS

def cat_plantas(request):
    return render(request, 'shopWeb/productos/cat_plantas/cat_plantas.html')

def flores(request):
    return render(request, 'shopWeb/productos/cat_plantas/flores.html')

def huerto(request):
    return render(request, 'shopWeb/productos/cat_plantas/huerto.html')

def plantas_arboles(request):
    return render(request, 'shopWeb/productos/cat_plantas/plantas_arboles.html')

#CATEGORIA INSUMOS

def cat_insumos(request):
    return render(request, 'shopWeb/productos/cat_insumos/cat_insumos.html')

def fertilizantes(request):
    return render(request, 'shopWeb/productos/cat_insumos/fertilizantes.html')

def otros_insumos(request):
    return render(request, 'shopWeb/productos/cat_insumos/otros_insumos.html')

def tierra(request):
    return render(request, 'shopWeb/productos/cat_insumos/tierra.html')

# CRUD PRODUCTOS

def es_admin(user):
    return user.is_staff



def obtener_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')

    subcategorias = SubCategoria.objects.filter(categoria_id=categoria_id).values('subcategoria_id', 'subcategoria_nombre')

    data = {
        'subcategorias': list(subcategorias)
    }

    return JsonResponse(data)

@login_required
@user_passes_test(es_admin)
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'shopWeb/admin/productos.html', {'productos': productos})

@login_required
@user_passes_test(es_admin)
def producto_nuevo(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            precio = form.cleaned_data['precio']
            stock = form.cleaned_data['stock']
            categoria_id = form.cleaned_data['categoria']
            subcategoria_id = form.cleaned_data['subcategoria']
            imagen = form.cleaned_data['imagen']
            categoria = Categoria.objects.get(id_categoria=categoria_id)
            subcategoria = SubCategoria.objects.get(id_subcategoria=subcategoria_id)

            producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock,
                                id_categoria=categoria, id_subcategoria=subcategoria, img=imagen)
            producto.save()
            return redirect('productos')
    else:
        form = ProductoForm()

    categorias = Categoria.objects.all()
    subcategorias = SubCategoria.objects.all() 
    return render(request, 'shopWeb/admin/producto_nuevo.html', {'form': form, 'categorias': categorias, 'subcategorias': subcategorias})

@login_required
@user_passes_test(es_admin)
def producto_editar(request, id):
    producto = get_object_or_404(Producto, id_producto=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'shopWeb/admin/producto_editar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def producto_eliminar(request, id):
    producto = get_object_or_404(Producto, id_producto=id)
    producto.delete()
    return redirect('shopWeb:productos')