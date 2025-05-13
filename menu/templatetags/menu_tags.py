from django import template
from django.utils.safestring import mark_safe
from ..models import Menu

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_path = request.path_info

    try:
        menu = Menu.objects.prefetch_related('items__children').get(name=menu_name)
    except Menu.DoesNotExist:
        return ''

    # Построение дерева пунктов меню в памяти
    items = list(menu.items.all())

    # Создаем словарь id -> item для быстрого доступа
    item_dict = {item.id: item for item in items}

    # Создаем структуру: id -> {'item': item, 'children': []}
    tree_nodes = {}
    for item in items:
        tree_nodes[item.id] = {'item': item, 'children': []}

    # Строим дерево по родителям
    roots = []
    for item in items:
        if item.parent_id:
            parent_node = tree_nodes.get(item.parent_id)
            if parent_node:
                parent_node['children'].append(tree_nodes[item.id])
        else:
            roots.append(tree_nodes[item.id])

    # Определяем активный пункт и раскрываем ветки согласно условиям
    active_id = None

    def mark_active(node):
        nonlocal active_id
        item_url = node['item'].get_url()
        is_active = (item_url == current_path)

        # Проверка на совпадение по URL или по имени URL (если есть)
        if not is_active and hasattr(request, 'resolver_match'):
            try:
                match_url_name = request.resolver_match.view_name
                if match_url_name == node['item'].url_name:
                    is_active = True
            except AttributeError:
                pass

        node['active'] = is_active

        # Рекурсивно проверяем детей и определяем активность и раскрытие ветки
        node['children_active'] = False
        for child in node['children']:
            mark_active(child)
            if child.get('active') or child.get('children_active'):
                node['children_active'] = True

        if is_active:
            active_id_local[0] = node['item'].id

        return is_active

    active_id_local = [None]
    for root in roots:
        mark_active(root)

    # Функция для рендеринга дерева в HTML (используем рекурсию)
    def render_menu(nodes):
        html = '<ul>'
        for node in nodes:
            classes = []
            if node.get('active'):
                classes.append('active')
            if node.get('children') and (node.get('active') or node.get('children_active')):
                classes.append('expanded')
            class_attr = f' class="{" ".join(classes)}"' if classes else ''
            url = node['item'].get_url()
            html += f'<li{class_attr}><a href="{url}">{node["item"].title}</a>'
            if node.get('children') and (node.get('active') or node.get('children_active')):
                html += render_menu(node['children'])
            html += '</li>'
        html += '</ul>'
        return html

    menu_html = render_menu(roots)

    return mark_safe(menu_html)