from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')

        def add_cors_headers_response_callback(event):
            def cors_headers(request, response):
                response.headers.update({
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS,PUT,DELETE',
                'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
                })
            event.request.add_response_callback(cors_headers)

        config.add_subscriber(add_cors_headers_response_callback, 'pyramid.events.NewRequest')
        # ------------------------------------------

        config.scan()
    return config.make_wsgi_app()