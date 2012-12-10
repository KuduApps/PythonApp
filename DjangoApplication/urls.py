import os
DIRNAME = os.path.dirname(__file__)

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from DjangoApplication.test_urls import (stdlib, ping_mysql, test_azure_call, run_azure_test, 
                                         test_local_file, test_http_request, test_write_illegal_path,
                                         test_mysql_dmo)

from mezzanine.core.views import direct_to_template


admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = patterns("",
    #(r'^manage/', include('lfs.manage.urls')),
    (r'^reviews/', include('reviews.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^paypal/pdt/', include('paypal.standard.pdt.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(DIRNAME, "media"), 'show_indexes': True }),

    ("^admin/", include(admin.site.urls)),

    # We don't want to presume how your homepage works, so here are a
    # few patterns you can use to set it up.

    # HOMEPAGE AS STATIC TEMPLATE
    # ---------------------------
    # This pattern simply loads the index.html template. It isn't
    # commented out like the others, so it's the default. You only need
    # one homepage pattern, so if you use a different one, comment this
    # one out.

    url("^$", direct_to_template, {"template": "index.html"}, name="home"),

    # HOMEPAGE AS AN EDITABLE PAGE IN THE PAGE TREE
    # ---------------------------------------------
    # This pattern gives us a normal ``Page`` object, so that your
    # homepage can be managed via the page tree in the admin. If you
    # use this pattern, you'll need to create a page in the page tree,
    # and specify its URL (in the Meta Data section) as "/", which
    # is the value used below in the ``{"slug": "/"}`` part. Make
    # sure to uncheck "show in navigation" when you create the page,
    # since the link to the homepage is always hard-coded into all the
    # page menus that display navigation on the site. Also note that
    # the normal rule of adding a custom template per page with the
    # template name using the page's slug doesn't apply here, since
    # we can't have a template called "/.html" - so for this case, the
    # template "pages/index.html" can be used.

    # url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),

    # HOMEPAGE FOR A BLOG-ONLY SITE
    # -----------------------------
    # This pattern points the homepage to the blog post listing page,
    # and is useful for sites that are primarily blogs. If you use this
    # pattern, you'll also need to set BLOG_SLUG = "" in your
    # ``settings.py`` module, and delete the blog page object from the
    # page tree in the admin if it was installed.

    # url("^$", "mezzanine.blog.views.blog_post_list", name="home"),

    (r'^stdlib.*',stdlib),
    (r'^ping_mysql.*',ping_mysql),
    (r'^azure$',test_azure_call),
    (r'^azure/$',test_azure_call),
    (r'^azure/.*$',run_azure_test),
    (r'^test_local_file.*$',test_local_file),
    (r'^test_http_request.*$',test_http_request),
    (r'^test_illegal_path.*$', test_write_illegal_path),
    (r'test_mysql_dmo.*$', test_mysql_dmo),
    #(r'', include('lfs.core.urls')),


    
    # MEZZANINE'S URLS
    # ----------------
    # Note: ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!
    # If you'd like more granular control over the patterns in
    # ``mezzanine.urls``, go right ahead and take the parts you want
    # from it, and use them directly below instead of using
    # ``mezzanine.urls``.
    ("^", include("mezzanine.urls")),

)

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler500 = "mezzanine.core.views.server_error"
