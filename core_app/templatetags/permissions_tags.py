from django import template
from core_app.modules.users.user_dal import UserDAL

register = template.Library()

@register.simple_tag(takes_context=True)
def check_permission(context, module_key, right_type):
    """
    Usage: {% check_permission "CASH_BOOK" "view" as can_view_cash %}
    """
    request = context.get('request')
    if not request:
        return False
        
    user_id = request.session.get('user_id')
    if not user_id:
        return False

    # Superuser check (agar aapne session mein flag rakha hai)
    if request.session.get('is_superuser'):
        return True

    # Rights fetch karein
    rights = UserDAL.get_user_rights_matrix(user_id)
    
    for r in rights:
        # Aapki SP 'vcmdkkey' return karti hai (e.g. 'CASH_BOOK', 'USER_MGMT')
        if r.get('vcmdkkey') == module_key.upper():
            if right_type == 'view':   return r.get('btcanview') == 1
            if right_type == 'add':    return r.get('btcancreate') == 1
            if right_type == 'edit':   return r.get('btcanedit') == 1
            if right_type == 'delete': return r.get('btcandelete') == 1
            
    return False