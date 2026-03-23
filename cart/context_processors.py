from .models import Cart


def cart_item_count(request):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None
        return {'cart_item_count': cart.item_count if cart else 0}
    except Exception:
        return {'cart_item_count': 0}
