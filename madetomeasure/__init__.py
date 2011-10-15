from pyramid.config import Configurator
from repoze.zodbconn.finder import PersistentApplicationFinder

from pyramid.i18n import TranslationStringFactory
from pyramid.session import UnencryptedCookieSessionFactoryConfig

MadeToMeasureTSF = TranslationStringFactory('MadeToMeasure')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    #Patch is for making deform translations work
    from madetomeasure import patches
    
    from madetomeasure.models.app import appmaker
    from madetomeasure.security import authn_policy
    from madetomeasure.security import authz_policy
    
    zodb_uri = settings.get('zodb_uri', False)
    if zodb_uri is False:
        raise ValueError("No 'zodb_uri' in application configuration.")

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)

    sessionfact = UnencryptedCookieSessionFactoryConfig('messages')
    
    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          root_factory=get_root,
                          session_factory = sessionfact,)
    
    config.add_static_view('static', 'madetomeasure:static')
    config.add_static_view('deform', 'deform:static')

    #Set which mailer to use
    config.include(settings['mailer'])

    config.include('madetomeasure.models.question_types')
    config.include('madetomeasure.models.translations')
    config.include('madetomeasure.models.date_time_helper')
    
    config.scan('betahaus.pyracont.fields.password')
    
    config.add_translation_dirs('deform:locale/',
                                'colander:locale/',
                                'madetomeasure:locale/',)

    config.hook_zca()
    config.scan('madetomeasure')
    return config.make_wsgi_app()


