from rest_framework import renderers


class PassRenderer(renderers.BaseRenderer):
    """Return data as-is. View should supply a Response.
    It is used to download files from REST endpoints.
    """

    media_type = ""
    format = ""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
