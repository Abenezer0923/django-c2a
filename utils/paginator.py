from django.core.paginator import Paginator


def common_pagination(objects, page=1, per_page=26) -> dict:
    """
    @param objects: Ordered QuerySet Object (Any)
    @param page: required page of pagination
    @param per_page: number of objects per page
    @return: custom dict: for graphene pagination type
    """
    paginator = Paginator(objects, per_page)

    result = paginator.page(page)  # results from the current page

    return {
        "page": page,
        "pages": paginator.num_pages,
        "has_next": result.has_next(),
        "has_prev": result.has_previous(),
        "objects": result.object_list,
        "total_objects": len(objects) if type(objects) == list else objects.count(),
    }


# from django.core.paginator import Paginator
# from typing import Union
# from django.db.models.query import QuerySet


# def common_pagination(objects: Union[QuerySet, list], page=1, per_page=26) -> dict:
#     """
#     @param objects: Ordered QuerySet Object (Any)
#     @param page: required page of pagination
#     @param per_page: number of objects per page
#     @return: custom dict: for graphene pagination type
#     """

#     is_even = lambda x: x % 2 == 0

#     if is_even(len(objects)):
#         paginator = Paginator(objects, per_page)
#     else:
#         paginator = Paginator(objects[:len(objects)-1], per_page)

#     result = paginator.page(page)  # results from the current page

#     return {
#         'page': page,
#         'pages': paginator.num_pages,
#         'has_next': result.has_next(),
#         'has_prev': result.has_previous(),
#         'objects': result.object_list,
#         'total_objects': len(objects) if type(objects) == list else objects.count(),
#     }
