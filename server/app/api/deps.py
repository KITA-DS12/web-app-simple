from app.services.post_service import post_service as get_post_service


def get_post_service_dep():
    return get_post_service