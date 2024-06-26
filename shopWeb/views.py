from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Producto, Categoria, SubCategoria
from .forms import ProductoForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction

# List of URLs that require authentication
protected_urls = [
    '/shopWeb/profile',  # Añade aquí todas las URLs que requieran autenticación
    '/shopWeb/admin/productos/',
    '/shopWeb/admin/productos/agregar',
    '/shopWeb/admin/productos/editar/<int:id>',
    '/shopWeb/productos/eliminar/<int:id>',
]

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
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return JsonResponse({'error': False, 'message': "Inicio de sesión exitoso."})
            else:
                login(request, user)
                return JsonResponse({'error': False, 'redirect_url': '/shopWeb/index'})
    return JsonResponse({'error': True, 'message': "Método no permitido."})
 
# LOGOUT
def logout_view(request):
    referer = request.META.get('HTTP_REFERER', '')

    logout(request)
    
    if any(url in referer for url in protected_urls):
        return redirect('/shopWeb/index')
    else:
        return redirect(referer or '/shopWeb/index')

# DETERMINAR ADMINISTRADORES
def es_admin(user):
    return user.is_staff

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

    return render(request, 'shopWeb/perfil_cliente/profile.html', {'user': user, 'form': form})

#CARRITO DE COMPRAS
def carro_compras(request):
    return render(request, 'shopWeb/perfil_cliente/carro_compras.html')


@csrf_exempt
@login_required
@require_POST
def procesar_pago(request):
    if request.method == 'POST':
        try:
            # Obtener el carrito de la sesión
            carrito = request.session.get('carrito', {})
            print(carrito)
            with transaction.atomic():
                # Iterar sobre los productos en el carrito y actualizar el stock
                for producto_id, cantidad in carrito.items():
                    print("Carrito items", carrito.items())
                    producto = get_object_or_404(Producto, id_producto=int(producto_id))
                    print("producto", producto)
                    print("producto stock", producto.stock)
                    if producto.stock >= cantidad:
                        producto.stock -= cantidad
                        producto.save()
                    else:
                        return JsonResponse({'error': True, 'message': f"No hay suficiente stock para {producto.nombre}."})
                
                # Vaciar el carrito después de procesar el pago
                request.session['carrito'] = {}

                return JsonResponse({'error': False, 'message': 'Pago procesado correctamente.'})
        
        except Exception as e:
            return JsonResponse({'error': True, 'message': str(e)}, status=500)

    return JsonResponse({'error': True, 'message': 'Método no permitido.'})


#PRODUCTOS

def productos_view(request, categoria_nombre, subcategoria_nombre):
    categoria = get_object_or_404(Categoria, categoria_nombre=categoria_nombre)
    subcategoria = get_object_or_404(SubCategoria, subcategoria_nombre=subcategoria_nombre, categoria=categoria)
    productos = Producto.objects.filter(id_categoria=categoria, id_subcategoria=subcategoria)

    print(productos)  # Para verificar que hay productos

    context = {
        'productos': productos,
        'categoria_nombre': categoria_nombre,
        'subcategoria_nombre': subcategoria_nombre,
    }

    return render(request, 'shopWeb/productos/productos.html', context)

def all_productos_view(request):
    
    productos = Producto.objects.all()
    print(productos)  

    context = {
        'productos': productos,
    }
    return render(request, 'shopWeb/productos/productos.html', context)


#CATEGORIA PRODUCTOS
def cat_herramientas(request):
    return render(request, 'shopWeb/productos/cat_herramientas.html')


def cat_plantas(request):
    return render(request, 'shopWeb/productos/cat_plantas.html')

def cat_insumos(request):
    return render(request, 'shopWeb/productos/cat_insumos.html')


# CRUD PRODUCTOS


def get_subcategorias(request, categoria_id):
    subcategorias = list(SubCategoria.objects.filter(categoria_id=categoria_id).values('subcategoria_id', 'subcategoria_nombre'))
    return JsonResponse(subcategorias, safe=False)

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
            form.save()
            return redirect('productos_admin')
        else:
            print(form.errors)
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
    categorias = Categoria.objects.all()
    subcategorias = SubCategoria.objects.filter(categoria=producto.id_categoria)
    return render(request, 'shopWeb/admin/producto_editar.html', {
        'form': form,
        'producto': producto,
        'categorias': categorias,
        'subcategorias': subcategorias
    })

@login_required
@user_passes_test(es_admin)
def producto_eliminar(request, id):
    producto = get_object_or_404(Producto, id_producto=id)
    producto.delete()
    return redirect('productos')


# CRUD DE PEDIDOS 
""" @login_required
@user_passes_test(es_admin)
def pedidos(request):
    return render(request, 'shopWeb/admin/pedidos.html')

@login_required
@user_passes_test(es_admin)
def pedido_nuevo(request):
    return render(request, 'shopWeb/admin/pedido_nuevo.html')

@login_required
@user_passes_test(es_admin)
def pedido_editar(request):
    return render(request, 'shopWeb/admin/pedido_editar.html')

@login_required
@user_passes_test(es_admin)
def pedido_eliminar(request):
    return render(request, 'shopWeb/admin/pedido_eliminar.html') """
