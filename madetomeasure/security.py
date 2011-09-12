from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy


def groupfinder(name, request):
    """ Get groups for the current user.
        This is also a callback for the Authorization policy.
    """
    return [] #FIXME: Implement
    #return request.context.get_groups(name)

#Authentication policies
authn_policy = AuthTktAuthenticationPolicy(secret='sosecret',
                                           callback=groupfinder)
authz_policy = ACLAuthorizationPolicy()